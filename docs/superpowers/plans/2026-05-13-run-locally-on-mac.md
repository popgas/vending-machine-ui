# Rodar localmente no Mac — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Permitir rodar `python index.py` no macOS sem crashes, logando e seguindo quando operações de hardware (GPIO/câmera/áudio) ou env vars faltantes falharem. Comportamento em produção (Raspberry Pi) inalterado.

**Architecture:** Novo módulo central `infrastructure/environment.py` com `is_dev_mode()` e `get_env(key, default)`. Cada worker de hardware (`GpioWorker`, `AudioWorker`, `CameraWorker`) ganha try/except completo logando falhas. Telas e workers que liam `os.environ[X]` diretamente passam a usar `get_env`. Bug de leftover em `internet_aware_retrier.py` corrigido.

**Tech Stack:** Python 3.12, Tkinter, pygame, opencv-python, gpiozero, RPi.GPIO, reactivex, unittest.

**Spec:** `docs/superpowers/specs/2026-05-13-run-locally-on-mac-design.md`

---

### Task 1: Criar módulo `infrastructure/environment.py` com testes

**Files:**
- Create: `infrastructure/environment.py`
- Create: `tests/test_environment.py`

- [ ] **Step 1: Escrever os testes que falham**

Criar `tests/test_environment.py`:

```python
import os
import unittest
from unittest.mock import patch


class TestEnvironment(unittest.TestCase):
    def test_is_dev_mode_returns_true_on_darwin(self):
        from infrastructure.environment import is_dev_mode
        with patch('platform.system', return_value='Darwin'):
            self.assertTrue(is_dev_mode())

    def test_is_dev_mode_returns_false_on_linux(self):
        from infrastructure.environment import is_dev_mode
        with patch('platform.system', return_value='Linux'):
            self.assertFalse(is_dev_mode())

    def test_get_env_returns_value_when_set(self):
        from infrastructure.environment import get_env
        with patch.dict(os.environ, {'FOO': 'bar'}):
            self.assertEqual(get_env('FOO'), 'bar')

    def test_get_env_returns_default_when_missing(self):
        from infrastructure.environment import get_env
        # garantir que a var não exista
        os.environ.pop('MISSING_KEY', None)
        self.assertEqual(get_env('MISSING_KEY', 'fallback'), 'fallback')

    def test_get_env_returns_none_when_missing_no_default(self):
        from infrastructure.environment import get_env
        os.environ.pop('MISSING_KEY', None)
        self.assertIsNone(get_env('MISSING_KEY'))


if __name__ == '__main__':
    unittest.main()
```

- [ ] **Step 2: Rodar testes para confirmar que falham**

Run: `python -m unittest tests.test_environment -v`
Expected: FAIL com `ModuleNotFoundError: No module named 'infrastructure.environment'`

- [ ] **Step 3: Implementar `infrastructure/environment.py`**

```python
import os
import platform

from infrastructure.observability.logger import Logger


def is_dev_mode() -> bool:
    """True when running on macOS (development machine)."""
    return platform.system() == 'Darwin'


def get_env(key: str, default=None):
    """
    Read env var safely.
    - Returns the value if set.
    - Returns `default` (which may be None) if missing.
    - Logs a warning if missing AND not in dev mode (production should have all vars set).
    """
    value = os.environ.get(key, default)

    if value is None and not is_dev_mode():
        Logger.get_logger().warning(f"env var ausente: {key}")

    return value
```

- [ ] **Step 4: Rodar testes para confirmar que passam**

Run: `python -m unittest tests.test_environment -v`
Expected: PASS (5 testes)

- [ ] **Step 5: Commit**

```bash
git add infrastructure/environment.py tests/test_environment.py
git commit -m "feat: módulo environment com is_dev_mode e get_env"
```

---

### Task 2: Tornar `GpioWorker` seguro no Mac

**Files:**
- Modify: `infrastructure/hardware/gpio.py`

- [ ] **Step 1: Substituir conteúdo do arquivo**

Substituir `infrastructure/hardware/gpio.py` por:

```python
import os
import time

import reactivex as rx

from reactivex.scheduler import ThreadPoolScheduler

from domains.enums.machine_doors import VendingMachinePins
from infrastructure.environment import is_dev_mode
from infrastructure.observability.logger import Logger

try:
    from gpiozero import LED, Button, Device
    from gpiozero.pins.mock import MockFactory
except ImportError:
    pass

is_rp_5 = os.environ.get('RP5')
is_macos = is_dev_mode()
use_gpiozero = is_rp_5 or is_macos


if is_macos:
    # Set the pin factory to mock for macOS
    try:
        Device.pin_factory = MockFactory()
    except NameError:
        pass  # gpiozero not installed/imported


try:
    import RPi.GPIO as GPIO
except ImportError:
    from infrastructure.hardware.dummy_gpio import DummyGPIO
    GPIO = DummyGPIO()


class GpioWorker:
    pool_scheduler = ThreadPoolScheduler(1)
    output_pins = [
        VendingMachinePins.openDoor1,
        VendingMachinePins.openDoor2,
        VendingMachinePins.openDoor3,
        VendingMachinePins.closeDoor1,
        VendingMachinePins.closeDoor2,
        VendingMachinePins.closeDoor3,
        VendingMachinePins.rotateCarrousel,
    ]

    @staticmethod
    def config():
        try:
            if use_gpiozero:
                GpioWorker._config_gpiozero()
            else:
                GpioWorker._config_rp_3()
        except Exception as e:
            Logger.get_logger().warning(f"GPIO config skipped: {e}")

    @staticmethod
    def _config_rp_3():
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

        for pin in GpioWorker.output_pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.HIGH)

        GPIO.setup(VendingMachinePins.reloadDoor, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    @staticmethod
    def _config_gpiozero():
        for pin_num in GpioWorker.output_pins:
            pin = LED(pin_num)
            pin.on()
            pin.close()

    @staticmethod
    def activate(pin_num):
        rx.just(pin_num).subscribe(
            on_next=GpioWorker.__activate_pin,
            on_completed=lambda: print("Pin activated"),
            on_error=lambda e: print(f"Pin not activated: {e}"),
            scheduler=GpioWorker.pool_scheduler
        )

    @staticmethod
    def close_all_doors():
        for door_pin in (
            VendingMachinePins.closeDoor1,
            VendingMachinePins.closeDoor2,
            VendingMachinePins.closeDoor3,
        ):
            GpioWorker.activate(door_pin)

    @staticmethod
    def __activate_pin(pin_num):
        logger = Logger.get_logger()
        logger.info(f"Acionar saída {pin_num}")

        try:
            if use_gpiozero:
                pin = LED(pin_num)
                pin.off()
                time.sleep(2)
                pin.on()
                pin.close()
            else:
                GPIO.output(pin_num, GPIO.LOW)
                time.sleep(2)
                GPIO.output(pin_num, GPIO.HIGH)

        except Exception as e:
            logger.warning(f"GPIO activate skipped on pin {pin_num}: {e}")
```

A mudança chave: `is_macos = is_dev_mode()` (em vez de checar `platform` direto) e `config()` agora tem try/except externo que loga e segue. `__activate_pin` já tinha try/except — apenas trocamos `error` por `warning` para o caso esperado de skip no Mac.

- [ ] **Step 2: Rodar testes existentes para garantir que não quebraram**

Run: `python -m unittest tests.test_gpio -v`
Expected: PASS (5 testes que já existiam)

- [ ] **Step 3: Commit**

```bash
git add infrastructure/hardware/gpio.py
git commit -m "feat: gpio_worker usa is_dev_mode e loga skip ao invés de crashar"
```

---

### Task 3: Tornar `AudioWorker` seguro no Mac

**Files:**
- Modify: `infrastructure/hardware/audio.py`

- [ ] **Step 1: Substituir conteúdo do arquivo**

Substituir `infrastructure/hardware/audio.py` por:

```python
import pygame
import reactivex as rx
from reactivex.scheduler import ThreadPoolScheduler

from infrastructure.observability.logger import Logger


class AudioWorker:
    pool_scheduler = ThreadPoolScheduler(1)

    @staticmethod
    def play(path):
        rx.just(path).subscribe(
            on_next=AudioWorker.__play_audio,
            on_completed=lambda: print("audio played"),
            on_error=lambda e: print(f"audio not played {e}"),
            scheduler=AudioWorker.pool_scheduler
        )

    @staticmethod
    def __play_audio(path):
        try:
            print("playing", path)
            pygame.mixer.init()
            pygame.mixer.music.stop()
            pygame.mixer.music.load(path)
            pygame.mixer.music.play()
        except Exception as e:
            Logger.get_logger().warning(f"audio play skipped ({path}): {e}")

    @staticmethod
    def stop():
        rx.just(None).subscribe(
            on_next=lambda e: AudioWorker.__stop_audio(),
            on_completed=lambda: print("audio stopped"),
            on_error=lambda e: print(f"audio not stopped {e}"),
            scheduler=AudioWorker.pool_scheduler,
        )

    @staticmethod
    def __stop_audio():
        try:
            pygame.mixer.music.stop()
        except Exception as e:
            Logger.get_logger().warning(f"audio stop skipped: {e}")
```

Mudança: `__play_audio` e nova `__stop_audio` têm try/except que loga e segue. `stop()` agora delega para `__stop_audio()` (antes chamava `pygame.mixer.music.stop()` direto no callback do rx).

- [ ] **Step 2: Rodar testes existentes para garantir que não quebraram**

Run: `python -m unittest tests.test_audio -v`
Expected: PASS (2 testes)

- [ ] **Step 3: Commit**

```bash
git add infrastructure/hardware/audio.py
git commit -m "feat: audio_worker loga falhas de pygame sem crashar"
```

---

### Task 4: Tornar `CameraWorker` seguro no Mac

**Files:**
- Modify: `infrastructure/hardware/camera.py`

- [ ] **Step 1: Modificar `take_photo_from_all_cameras` para usar `get_env`**

No arquivo `infrastructure/hardware/camera.py`, substituir:

```python
    @staticmethod
    def take_photo_from_all_cameras():
        cameras = [
            os.environ['CAMERA_1'],
            os.environ['CAMERA_2'],
            os.environ['CAMERA_3']
        ]
```

Por:

```python
    @staticmethod
    def take_photo_from_all_cameras():
        from infrastructure.environment import get_env
        cameras = [
            get_env('CAMERA_1', '0'),
            get_env('CAMERA_2', '0'),
            get_env('CAMERA_3', '0'),
        ]
```

- [ ] **Step 2: Trocar `exit()` por logging+return**

No mesmo arquivo, substituir:

```python
            if not cap.isOpened():
                print("Error: Could not open camera.")
                exit()
```

Por:

```python
            if not cap.isOpened():
                Logger.get_logger().warning(f"camera {camera} could not open; skipping")
                cap.release()
                continue
```

- [ ] **Step 3: Garantir contagem `i` correta após `continue`**

Inspecionar o método inteiro de `take_photo_from_all_cameras`. O `i += 1` está no fim do loop. Como adicionamos `continue` antes de `photos.append`, o `i` não é incrementado para câmeras que falham. Isso é o comportamento desejado (a foto não é adicionada). Verificar lendo o arquivo:

Run: `grep -n "i += 1\|i = 1\|continue\|photos.append" infrastructure/hardware/camera.py`
Expected: ver que `i += 1` está depois de `photos.append`. Se não estiver, ajustar.

- [ ] **Step 4: Rodar testes existentes para garantir que não quebraram**

Run: `python -m unittest tests.test_camera -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add infrastructure/hardware/camera.py
git commit -m "feat: camera_worker usa get_env e não chama exit() em falha"
```

---

### Task 5: Tornar `Websocket` seguro sem `ABLY_KEY`

**Files:**
- Modify: `infrastructure/hardware/websocket.py`

- [ ] **Step 1: Substituir conteúdo do arquivo**

Substituir `infrastructure/hardware/websocket.py` por:

```python
import asyncio

from ably import AblyRealtime
from ably.types.message import Message

from domains.enums.machine_doors import VendingMachinePins
from infrastructure.environment import get_env
from infrastructure.hardware.camera import CameraWorker
from infrastructure.hardware.gpio import GpioWorker
from infrastructure.observability.logger import Logger


class Websocket:
    def __init__(self):
        vm_id = get_env('VENDING_MACHINE_ID', 'dev-vm-01')
        self.channel_name = f'vending_machine_{vm_id}'
        self.command_name = f'{self.channel_name}:commands'
        self.result_name = f'{self.channel_name}::results'
        print(self.command_name)
        self.channel_command_handler = None
        self.channel_result_handler = None

    @staticmethod
    async def configure():
        ably_key = get_env('ABLY_KEY')
        if not ably_key:
            Logger.get_logger().warning("ABLY_KEY ausente; websocket skipped")
            return

        try:
            websocket = Websocket()
            await websocket.connect(ably_key)
            await asyncio.Event().wait()
        except Exception as e:
            Logger.get_logger().warning(f"websocket configure skipped: {e}")

    async def connect(self, ably_key: str):
        ably = AblyRealtime(ably_key)

        await ably.connection.once_async('connected')

        print("connected")

        channel = ably.channels.get(self.command_name)
        await channel.subscribe(self.command_handler)

    async def command_handler(self, event: Message):
        print(f'__command_handler: {event}')

        match event.name:
            case 'cameras:take_photos':
                await self.__take_photos(event)
            case 'doors:open':
                await self.__open_doors(event)
            case 'doors:close':
                await self.__close_doors(event)

    async def __take_photos(self, event: Message):
        GpioWorker.close_all_doors()

        photos = CameraWorker.take_photo_from_all_cameras()

        await self.channel_result_handler.publish(event.name, {
            'photos': photos
        })

    async def __open_doors(self, event: Message):
        match event.data['door_number']:
            case 1:
                GpioWorker.activate(VendingMachinePins.openDoor1)
            case 2:
                GpioWorker.activate(VendingMachinePins.openDoor2)
            case 3:
                GpioWorker.activate(VendingMachinePins.openDoor3)

        await self.channel_result_handler.publish(event['name'])

    async def __close_doors(self, event: Message):
        match event.data['door_number']:
            case 1:
                GpioWorker.activate(VendingMachinePins.closeDoor1)
            case 2:
                GpioWorker.activate(VendingMachinePins.closeDoor2)
            case 3:
                GpioWorker.activate(VendingMachinePins.closeDoor3)

        await self.channel_result_handler.publish(event['name'])
```

Mudanças: import de `os` removido (não usado mais), `get_env` usado para `VENDING_MACHINE_ID` e `ABLY_KEY`, `configure()` agora retorna cedo se sem key e tem try/except externo, `connect` recebe `ably_key` como parâmetro.

- [ ] **Step 2: Verificar que arquivo importa corretamente**

Run: `python -c "from infrastructure.hardware.websocket import Websocket; print('ok')"`
Expected: `ok`

- [ ] **Step 3: Commit**

```bash
git add infrastructure/hardware/websocket.py
git commit -m "feat: websocket pula configuração quando ABLY_KEY ausente"
```

---

### Task 6: Tornar `HealthChecker` seguro

**Files:**
- Modify: `infrastructure/hardware/health_checker.py`

- [ ] **Step 1: Substituir conteúdo do arquivo**

Substituir `infrastructure/hardware/health_checker.py` por:

```python
from infrastructure.environment import get_env
from infrastructure.http.popgas_api import PopGasApi
from infrastructure.observability.logger import Logger


class HealthChecker:
    @staticmethod
    def start(app):
        print("started")
        app.after(1000 * 60, lambda: HealthChecker.ping(app))

    @staticmethod
    def ping(app):
        try:
            vm_id = get_env('VENDING_MACHINE_ID')
            if not vm_id:
                Logger.get_logger().warning("VENDING_MACHINE_ID ausente; ping skipped")
                return

            print("sending ping request")
            PopGasApi.request("PUT", f"/vending-machine-orders/{vm_id}/ping")
        finally:
            app.after(1000 * 60, lambda: HealthChecker.ping(app))
```

Mudanças: `os` removido, `get_env` usado, early-return quando ausente, `finally` continua reagendando para manter o heartbeat de retry.

- [ ] **Step 2: Verificar import**

Run: `python -c "from infrastructure.hardware.health_checker import HealthChecker; print('ok')"`
Expected: `ok`

- [ ] **Step 3: Commit**

```bash
git add infrastructure/hardware/health_checker.py
git commit -m "feat: health_checker pula ping quando VENDING_MACHINE_ID ausente"
```

---

### Task 7: Corrigir bug em `internet_aware_retrier.py`

**Files:**
- Modify: `infrastructure/hardware/internet_aware_retrier.py`

- [ ] **Step 1: Substituir conteúdo do arquivo**

Substituir `infrastructure/hardware/internet_aware_retrier.py` por:

```python
import tkinter as tk
from tkinter import ttk

from infrastructure.observability.logger import Logger


class InternetAwareRetryer:
    root_app = None
    popup = None

    @staticmethod
    def start(func: callable):
        try:
            func()

            if InternetAwareRetryer.root_app is not None and InternetAwareRetryer.popup is not None:
                InternetAwareRetryer.popup.destroy()
                InternetAwareRetryer.popup = None
        except Exception as e:
            Logger.get_logger().warning(f"InternetAwareRetryer caught: {e}")

            if InternetAwareRetryer.root_app is not None and InternetAwareRetryer.popup is None:
                popup = tk.Toplevel(InternetAwareRetryer.root_app)
                popup.title("Connection Error")
                popup.geometry("300x120")
                popup.resizable(False, False)

                label = ttk.Label(popup, text="No internet connection detected!", wraplength=250)
                label.pack(pady=20)

                popup.attributes("-topmost", True)
                InternetAwareRetryer.popup = popup

            if InternetAwareRetryer.root_app is not None:
                InternetAwareRetryer.root_app.after(5000, lambda: InternetAwareRetryer.start(func))
```

Mudanças: 
- `import tk` → `import tkinter as tk` (era bug)
- `raise Exception("teste")` removido
- Lógica de popup corrigida: antes criava popup só se `root_app is None` (invertido). Agora cria se `root_app is not None` e popup ainda não foi criado
- Popup armazenado no atributo de classe para poder destruir depois
- Quando func executa com sucesso, destruir popup se existir
- Loga exceção para debug

- [ ] **Step 2: Verificar import**

Run: `python -c "from infrastructure.hardware.internet_aware_retrier import InternetAwareRetryer; print('ok')"`
Expected: `ok`

- [ ] **Step 3: Commit**

```bash
git add infrastructure/hardware/internet_aware_retrier.py
git commit -m "fix: internet_aware_retrier - remove raise leftover e corrige import"
```

---

### Task 8: Atualizar `new_order_intent.py` para usar `get_env`

**Files:**
- Modify: `presentation/abstractions/new_order_intent.py`

- [ ] **Step 1: Atualizar `get_camera()`**

Em `presentation/abstractions/new_order_intent.py`, substituir o método `get_camera`:

```python
    def get_camera(self) -> int | str:
        if platform.system() == 'Darwin':
            return 0

        if self.__use_first_door():
            return os.environ['CAMERA_1']
        elif self.__use_second_doors():
            return os.environ['CAMERA_2']
        else:
            return os.environ['CAMERA_3']
```

Por:

```python
    def get_camera(self) -> int | str:
        from infrastructure.environment import is_dev_mode, get_env

        if is_dev_mode():
            return 0

        if self.__use_first_door():
            return get_env('CAMERA_1', '0')
        elif self.__use_second_doors():
            return get_env('CAMERA_2', '0')
        else:
            return get_env('CAMERA_3', '0')
```

- [ ] **Step 2: Rodar testes existentes do new_order_intent**

Run: `python -m unittest tests.test_new_order_intent -v`
Expected: PASS

- [ ] **Step 3: Commit**

```bash
git add presentation/abstractions/new_order_intent.py
git commit -m "feat: new_order_intent usa get_env para CAMERA_X"
```

---

### Task 9: Atualizar telas que leem `VENDING_MACHINE_ID`

**Files:**
- Modify: `presentation/views/screens/card_machine/card_machine.py`
- Modify: `presentation/views/screens/product_selected/product_selected.py`
- Modify: `presentation/views/screens/emtpy_stock/empty_stock.py`
- Modify: `presentation/views/screens/camera_verification/camera_verification.py`
- Modify: `presentation/views/screens/technical_support/technical_support.py`

Para cada arquivo, substituir `os.environ['VENDING_MACHINE_ID']` por `get_env('VENDING_MACHINE_ID', 'dev-vm-01')` e adicionar o import.

- [ ] **Step 1: Atualizar `card_machine.py`**

Em `presentation/views/screens/card_machine/card_machine.py`:

No topo do arquivo (após outros imports `infrastructure.`), adicionar:

```python
from infrastructure.environment import get_env
```

Substituir linha 202:

```python
        vm_id = os.environ['VENDING_MACHINE_ID']
```

Por:

```python
        vm_id = get_env('VENDING_MACHINE_ID', 'dev-vm-01')
```

- [ ] **Step 2: Atualizar `product_selected.py`**

Em `presentation/views/screens/product_selected/product_selected.py`:

Adicionar import:

```python
from infrastructure.environment import get_env
```

Substituir linha 142:

```python
        vm_id = os.environ['VENDING_MACHINE_ID']
```

Por:

```python
        vm_id = get_env('VENDING_MACHINE_ID', 'dev-vm-01')
```

- [ ] **Step 3: Atualizar `empty_stock.py`**

Em `presentation/views/screens/emtpy_stock/empty_stock.py`:

Adicionar import:

```python
from infrastructure.environment import get_env
```

Substituir linha 57:

```python
        vm_id = os.environ['VENDING_MACHINE_ID']
```

Por:

```python
        vm_id = get_env('VENDING_MACHINE_ID', 'dev-vm-01')
```

- [ ] **Step 4: Atualizar `camera_verification.py`**

Em `presentation/views/screens/camera_verification/camera_verification.py`:

Adicionar import:

```python
from infrastructure.environment import get_env
```

Substituir linha 130 dentro do `PopGasApi.request`:

```python
            'vending_machine_id': os.environ['VENDING_MACHINE_ID'],
```

Por:

```python
            'vending_machine_id': get_env('VENDING_MACHINE_ID', 'dev-vm-01'),
```

- [ ] **Step 5: Atualizar `technical_support.py`**

Em `presentation/views/screens/technical_support/technical_support.py`:

Adicionar import:

```python
from infrastructure.environment import get_env
```

Substituir linha 58:

```python
        vm_id = os.environ['VENDING_MACHINE_ID']
```

Por:

```python
        vm_id = get_env('VENDING_MACHINE_ID', 'dev-vm-01')
```

- [ ] **Step 6: Verificar que todos imports funcionam**

Run: `python -c "import presentation.views.screens.card_machine.card_machine; import presentation.views.screens.product_selected.product_selected; import presentation.views.screens.emtpy_stock.empty_stock; import presentation.views.screens.camera_verification.camera_verification; import presentation.views.screens.technical_support.technical_support; print('all imports ok')"`

Expected: `all imports ok` (ou se falhar por causa de dependências hardware, ao menos não deve falhar por causa de imports do `get_env`)

- [ ] **Step 7: Rodar suite completa de testes**

Run: `python -m unittest discover tests -v`
Expected: PASS em todos (alguns testes que dependem de hardware podem requerer envs mockadas; se passavam antes, devem continuar passando)

- [ ] **Step 8: Commit**

```bash
git add presentation/views/screens/card_machine/card_machine.py \
        presentation/views/screens/product_selected/product_selected.py \
        presentation/views/screens/emtpy_stock/empty_stock.py \
        presentation/views/screens/camera_verification/camera_verification.py \
        presentation/views/screens/technical_support/technical_support.py
git commit -m "feat: telas usam get_env para VENDING_MACHINE_ID"
```

---

### Task 10: Criar `.env.example`

**Files:**
- Create: `.env.example`

- [ ] **Step 1: Criar `.env.example`**

Criar `.env.example` na raiz do projeto com:

```
# Identificador da máquina (em dev pode ser qualquer string)
VENDING_MACHINE_ID=dev-vm-01

# Chave do Ably para websocket (vazio = pula conexão)
ABLY_KEY=

# Câmeras: em dev o código usa 0 (webcam padrão do Mac); em produção, /dev/video0 etc.
CAMERA_1=0
CAMERA_2=0
CAMERA_3=0

# Flag para indicar Raspberry Pi 5 (não setar em Mac)
RP5=
```

- [ ] **Step 2: Commit**

```bash
git add .env.example
git commit -m "docs: adiciona .env.example com defaults para dev"
```

---

### Task 11: Verificação manual — rodar `python index.py` no Mac

**Files:**
- (verificação apenas)

- [ ] **Step 1: Garantir que dependências estão instaladas**

Run: `pip install -r requirements.txt`
Expected: instala sem erros (ou aceita avisos de pacotes só-de-Pi como `RPi.GPIO`)

- [ ] **Step 2: Rodar o app sem env vars setadas**

Run: `python index.py`
Expected: 
- App abre em fullscreen
- Tela `welcome` é exibida
- Logs mostram skips de GPIO/áudio quando aplicável
- NÃO crasha com `KeyError`
- NÃO crasha com erro de pygame
- NÃO crasha com erro de GPIO

Pressionar `Cmd+Q` ou matar o processo para fechar.

- [ ] **Step 3: Navegar pelo fluxo end-to-end**

Reproduzir manualmente (cliques na UI):
1. Tela welcome → clicar "Comprar"
2. Tela product_selection → clicar uma das opções
3. Telas seguintes devem renderizar; transições disparadas por timer (`self.app.after(...)`) devem funcionar
4. Verificar que nenhuma exceção não-tratada aparece no terminal

Confirmar no log que vê mensagens como:
- `GPIO activate skipped on pin X: ...`
- `audio play skipped (...)`
- ou similares — indicando que skipps estão funcionando

- [ ] **Step 4: Rodar suite completa de testes uma última vez**

Run: `python -m unittest discover tests -v`
Expected: PASS

- [ ] **Step 5: Commit final (caso haja ajustes durante verificação)**

Se durante a verificação manual encontrar pontos adicionais que precisam de fix, fazer ajuste e commitar com mensagem descritiva. Caso contrário, esta task termina sem commit.

---

## Self-review

Verificação contra a spec:

**1. Cobertura da spec:**
- ✓ `infrastructure/environment.py` criado (Task 1)
- ✓ `gpio.py` com try/except (Task 2)
- ✓ `audio.py` com try/except (Task 3)
- ✓ `camera.py` usa `get_env` + não chama `exit()` (Task 4)
- ✓ `websocket.py` pula se ABLY_KEY ausente (Task 5)
- ✓ `health_checker.py` usa `get_env` (Task 6)
- ✓ `internet_aware_retrier.py` com bug corrigido (Task 7)
- ✓ `new_order_intent.py` usa `get_env` (Task 8)
- ✓ Todas as 5 telas com `VENDING_MACHINE_ID` atualizadas (Task 9)
- ✓ `.env.example` criado (Task 10)
- ✓ Verificação manual (Task 11)

**2. Sem placeholders:** todas as steps têm código exato ou comando exato.

**3. Consistência de tipos:** `is_dev_mode() -> bool`, `get_env(key, default=None)` — usado consistentemente em todos os módulos.
