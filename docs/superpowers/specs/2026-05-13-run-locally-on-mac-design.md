# Design: Rodar o projeto localmente no Mac

**Data:** 2026-05-13
**Autor:** Leonardo Caldas

## Contexto

O projeto `vending-machine-ui` é uma UI Tkinter rodando em Raspberry Pi que controla uma máquina de venda automática de gás. Interage com hardware via `RPi.GPIO`/`gpiozero` (portas, carrossel), câmeras USB (`cv2.VideoCapture`), e áudio (`pygame.mixer`). Também depende de variáveis de ambiente (`VENDING_MACHINE_ID`, `ABLY_KEY`, `CAMERA_1/2/3`) e de integrações de rede (Ably realtime, API PopGás).

Hoje, ao rodar no Mac de desenvolvimento:
- `KeyError` em variáveis de ambiente faltantes (`os.environ['X']`)
- Inicialização de GPIO pode falhar mesmo com `MockFactory`
- `cv2.VideoCapture` pode travar
- `pygame.mixer` pode falhar sem device de áudio
- Conexão com Ably falha sem chave
- Bug em `internet_aware_retrier.py` (raise leftover, import quebrado)

Resultado: o fluxo trava antes de o desenvolvedor conseguir ver a UI completa.

## Objetivo

Permitir rodar o projeto end-to-end no Mac para testes de UI, sem alterar o comportamento em produção (Raspberry Pi). Toda falha de hardware deve ser logada e o fluxo deve continuar.

**Não é objetivo:** simular hardware fielmente (delays reais, eventos de entrada, etc.).

## Decisões de design

1. **Detecção de modo dev:** automática via `platform.system() == 'Darwin'`. Sem env var extra para configurar.
2. **Comportamento em falha:** logar `"<operação> skipped on Mac: <motivo>"` e continuar. Nada de suprimir silenciosamente.
3. **Variáveis de ambiente:** ler sempre via helper `get_env(key, default)`. Criar `.env.example` documentando o que existe.

## Arquitetura

### Novo módulo: `infrastructure/environment.py`

Ponto único de decisão. Duas funções:

```python
def is_dev_mode() -> bool:
    """Returns True when running on macOS (development)."""
    return platform.system() == 'Darwin'

def get_env(key: str, default=None):
    """Reads env var; logs warning if absent and not in dev mode."""
    value = os.environ.get(key, default)
    if value is None and not is_dev_mode():
        Logger.get_logger().warning(f"env var ausente: {key}")
    return value
```

### Padrão de hardware worker

Cada worker (`AudioWorker`, `CameraWorker`, `GpioWorker`) segue o padrão:

```
try:
    <real hardware operation>
except Exception as e:
    Logger.get_logger().warning(f"<op> skipped: {e}")
    <return safe fallback>
```

Quando o worker já tem garantia de que vai falhar no Mac (ex: GPIO físico), pode short-circuitar antes via `if is_dev_mode(): log + return`.

## Arquivos afetados

### Novos arquivos

- **`infrastructure/environment.py`** — módulo central com `is_dev_mode()` e `get_env()`
- **`.env.example`** — template de variáveis com valores de dev

### Modificados

**Hardware:**
- `infrastructure/hardware/gpio.py` — envolver `config()` e `__activate_pin()` em try/except completo; logar skips de forma legível
- `infrastructure/hardware/audio.py` — try/except em `__play_audio()` e `stop()`; logar falha de pygame
- `infrastructure/hardware/camera.py` — trocar `os.environ['CAMERA_X']` por `get_env`; em `take_photo`, se câmera não abrir, retornar `CameraResult(error=True)` (callback já cuida do erro)
- `infrastructure/hardware/websocket.py` — try/except no `configure()`; pular se `ABLY_KEY` ausente
- `infrastructure/hardware/health_checker.py` — trocar `os.environ['VENDING_MACHINE_ID']` por `get_env`; pular ping se None
- `infrastructure/hardware/internet_aware_retrier.py` — remover `raise Exception("teste")` e corrigir `import tk` → `import tkinter as tk`

**Domínio/apresentação (apenas troca de env var):**
- `presentation/abstractions/new_order_intent.py` — `os.environ['CAMERA_X']` → `get_env('CAMERA_X', '0')`
- `presentation/views/screens/card_machine/card_machine.py` — `VENDING_MACHINE_ID` via `get_env`
- `presentation/views/screens/product_selected/product_selected.py` — idem
- `presentation/views/screens/emtpy_stock/empty_stock.py` — idem
- `presentation/views/screens/camera_verification/camera_verification.py` — idem
- `presentation/views/screens/technical_support/technical_support.py` — idem

### Inalterados (já têm tratamento adequado ou irrelevantes para o objetivo)

- `infrastructure/http/popgas_api.py` — já tem try/except no `request()`
- Telas que não tocam hardware/env vars diretamente

## Fluxo esperado no Mac

```
python index.py
  ↓
GpioWorker.config()
  → loga "GPIO config skipped on Mac" e segue
  ↓
WelcomeScreen abre
  ↓ (usuário clica)
PaymentSelectionScreen
  → AudioWorker.play() tenta pygame, se falha loga e segue
  ↓ (usuário escolhe pix)
CardMachineScreen
  → PopGasApi.request() tenta API real (se internet) ou falha silenciosamente
  → AudioWorker.play() tenta e segue
  ↓
PlaceEmptyContainerScreen
  → GpioWorker.activate() loga skip e segue
  ↓
CameraVerificationScreen
  → CameraWorker tenta abrir câmera 0 do Mac; se falhar retorna error=True
  → fluxo continua para próxima tela
  ↓
... resto do fluxo ...
```

## Variáveis no `.env.example`

```
VENDING_MACHINE_ID=dev-vm-01
ABLY_KEY=
CAMERA_1=0
CAMERA_2=0
CAMERA_3=0
RP5=
```

## Testes (manuais)

- `python index.py` boota no Mac sem crash
- Cada tela renderiza
- Transições disparadas por hardware/timer continuam fluindo
- Logs mostram explicitamente quando algo foi pulado por estar no Mac
- Nenhum `KeyError` por env var faltante
- Comportamento no Pi: inalterado (toda a lógica de hardware real ainda roda dentro do try)

## Riscos

- **Risco:** alguma chamada de hardware está em um caminho síncrono que bloqueia a UI mesmo no Mac.
  **Mitigação:** ao logar+skipar rápido, libera a thread imediatamente. Workers já usam `ThreadPoolScheduler`.

- **Risco:** mudar `os.environ[X]` para `get_env(X, default)` esconde bugs reais de configuração em produção.
  **Mitigação:** `get_env` loga warning quando a var está ausente em produção. Defaults só fazem sentido em modo dev — em produção, `get_env(X)` (sem default) retorna None e o caller decide.

- **Risco:** sequência de telas depende de evento físico (porta fechou) que não acontece no Mac.
  **Mitigação:** telas usam `self.app.after(...)` para timers, não eventos de hardware como input — então o fluxo avança por tempo. Já testado pelo padrão existente.
