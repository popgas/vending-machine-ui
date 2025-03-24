import cv2
import numpy as np
import os
import time
import multiprocessing
from flask_cors import CORS
import logging
from flask import Flask, request, jsonify
from datetime import datetime
import time
import glob
from gpiozero import LED, Button

# Criação de pasta para armazenar os logs
pasta_logs = "./logs"
os.makedirs(pasta_logs, exist_ok=True)

# Nome do arquivo de log baseado na data atual
nome_arquivo_log = os.path.join(pasta_logs, f"App_{datetime.now().strftime('%Y-%m-%d')}.log")

# Classe de filtro personalizada para ignorar logs específicos
class FiltroIgnorarStream(logging.Filter):
    def filter(self, record):
        # Retorna False para ignorar mensagens contendo "STREAM"
        return "STREAM" not in record.getMessage()
    
# Configuração do logging
logging.basicConfig(
    level=logging.DEBUG,  # Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),  # Exibe os logs no terminal
        logging.FileHandler(nome_arquivo_log, encoding="utf-8")  # Salva os logs no arquivo
    ]
)

# Adicionar filtro para ignorar logs indesejados
for handler in logging.getLogger().handlers:
    handler.addFilter(FiltroIgnorarStream())

##############################################
# Hardware Integration Classes and Functions #
##############################################

class HardwareController:
    def __init__(self):
        self.quantidade_de_ciclos = [14, 14, 13]
        self.atual_ciclos = 0
        self.contador = 0
        
        self.pino_abre_porta = 23
        
        #Carrossel
        self.GPIO_PIN_12 = 12
        
        #porta 1
        self.GPIO_PIN_23 = 23 #abre
        self.GPIO_PIN_24 = 24 #fecha
        
        #porta 2
        self.GPIO_PIN_25 = 25 #abre
        self.GPIO_PIN_8 = 8 #fecha
        
        #porta 3
        self.GPIO_PIN_7 = 7 #abre
        self.GPIO_PIN_1 = 1 #fecha

        self.GPIO_PIN_26 = 26 #porta de recarga
        
        #self.GPIO_PIN_13 = 13  # Corrigido o nome do pino
        # Contador de ciclos (inicializado em 0)

        # Configurar todos os pinos GPIO como saída e inicializá-los como LOW
        pinos_saida = [
            self.GPIO_PIN_12, 
            self.GPIO_PIN_23, self.GPIO_PIN_24,
            self.GPIO_PIN_25, self.GPIO_PIN_8, 
            self.GPIO_PIN_7, self.GPIO_PIN_1,
            self.GPIO_PIN_26, self.pino_abre_porta
        ]
        for pino in pinos_saida:
            led = LED(pino)
            led.on()

        #Configurar os pinos de entrada com resistores de pull-up
        PIN_26_BUTTON = Button(self.GPIO_PIN_26)

        self.porta_de_recarga_aberta = False
        self.time_porta_de_recarga = None

        self.senha_correta = "96240415"
    
    def acionar_saida(self, pin):
        logging.info(f"Acionar Saida {pin}")
        print(f"Acionar Saida {pin}")
        try:
            led = LED(pin)
            led.off()
            time.sleep(2) 
            led.on()
        except Exception as e:
            print(f"Erro ao acionar saída {p} : {e}")
            logging.error(f"Erro ao acionar saída {p} : {e}")

    def cleanup(self):
        print("GPIO cleanup completed.")


def camera_process(conn):
    # Define persistent camera device paths
    camera_device_paths = ["/dev/video0", "/dev/video4", "/dev/video2"]
    # Fixed images for comparison
    fixed_image_paths = glob.glob("./Fotos_PB/*.png")
    print(fixed_image_paths)

    # Maximum captures for each camera device
    max_captures_list = [13, 14, 13]
    
    camera = Camera(camera_device_paths, fixed_image_paths, max_captures_list)
    camera.start(pipe=conn)


class Camera:
    def __init__(self, camera_indices, fixed_image_paths, max_captures_list):
        logging.info("Class Camera Iniciada")
        self.camera_indices = camera_indices
        self.fixed_image_paths = fixed_image_paths
        self.fixed_images = self.load_fixed_images()
        self.capture_counts = [0] * len(camera_indices)
        self.max_captures_list = max_captures_list
        self.cap = None
        self.camera_atual = 0
        self.initialize_camera()
    
    def load_fixed_images(self, pasta="Fotos_PB"):
        logging.info("Camera - Load Fixed Images")
        images = []
        try:
            # Verifica se a pasta existe
            if not os.path.exists(pasta):
                logging.error(f"Pasta '{pasta}' não encontrada.")
                return images
            # Lista todos os arquivos na pasta
            arquivos = [os.path.join(pasta, arquivo) for arquivo in os.listdir(pasta) if arquivo.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tif', '.tiff'))]
            # Carrega as imagens em preto e branco
            for caminho in arquivos:
                imagem = cv2.imread(caminho, cv2.IMREAD_GRAYSCALE)  # Lê a imagem em preto e branco
                if imagem is not None:
                    images.append(imagem)
                    logging.info(f"Imagem carregada: {caminho}")
                else:
                    logging.error(f"Erro ao carregar a imagem: {caminho}")
            if not images:
                logging.warning("Nenhuma imagem válida foi encontrada na pasta.")
        except Exception as e:
            logging.error(f"Erro ao carregar imagens da pasta '{pasta}': {e}")
        return images

    def initialize_camera(self):
        logging.info("Camera - Initialize Camera")
        """Tenta abrir a câmera atual. Fecha e reabre se necessário."""
        logging.info("\nReseta cameras")
        if self.cap:
            self.release_camera()  # Fecha qualquer câmera aberta anteriormente
    
        logging.info(f"inicializa camera {self.camera_atual} \n")
        self.cap = cv2.VideoCapture(self.camera_indices[self.camera_atual])
        if not self.cap.isOpened():
            raise ValueError(f"Não foi possível abrir a câmera {self.camera_indices[self.camera_atual]}")
        logging.info(f"Câmera {self.camera_indices[self.camera_atual]} inicializada.")

    def release_camera(self):
        logging.info("Camera - Release Camera")
        """Libera a câmera atual."""
        if self.cap:
            self.cap.release()
            logging.info(f"Câmera {self.camera_indices[self.camera_atual]} liberada.")

    def reset_camera(self):
        logging.info("Camera - Reset Camera")
        """Reinicializa a câmera atual."""
        logging.info(f"Resetando câmera {self.camera_indices[self.proxima]}")
        self.initialize_camera()

    def start(self, pipe):
        logging.info("Camera - Start")
        cv2.namedWindow("Câmera", cv2.WINDOW_NORMAL)

        # Adiciona uma espera de 3 segundos para inicialização da câmera
        logging.info("Aguardando inicialização da câmera...")
        time.sleep(2)  # Tempo de espera ajustável

        while self.camera_atual < len(self.camera_indices):
            ret, frame = self.cap.read()
            if not ret:
                logging.error(f"Falha na captura de imagem na câmera {self.camera_indices[self.camera_atual]}. Tentando reiniciar.")
                self.reinicia_camera()
                continue  # Tenta capturar novamente

            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Converte o frame para preto e branco
            cv2.imshow("Câmera", gray_frame)

            if pipe.poll():
                command = pipe.recv()
                logging.info(f"Camera - comando - {command} - recebido")

                if command == 'camera1':
                    logging.info(f"Camera 1 - Selecinada")
                    if self.camera_atual != 0:
                        self.camera_atual = 0
                        self.initialize_camera()

                elif command == 'camera2':
                    logging.info(f"Camera 2 - Selecinada")
                    if self.camera_atual != 1:
                        self.camera_atual = 1
                        self.initialize_camera()

                elif command == 'camera3':
                    logging.info(f"Camera 3 - Selecinada")
                    if self.camera_atual != 2:
                        self.camera_atual = 2
                        self.initialize_camera()

                elif command == 'c':
                    
                    if not self.cap.isOpened():
                        self.initialize_camera()

                    logging.info(f"C:\n camera atual = {self.camera_atual}")

                    self.capture_counts[self.camera_atual] += 1
                    logging.info(f"Captura {self.capture_counts[self.camera_atual]} na câmera {self.camera_indices[self.camera_atual]}")
                    
                    if self.compare_images(gray_frame):
                        pipe.send('recognized')
                    else:
                        pipe.send('image_not_recognized')

                elif command == 'q':
                    logging.info(f"Comando para sair recebido. Finalizando.")
                    break

            if cv2.waitKey(1) & 0xFF == ord('q'):
                logging.info(f"Saindo do programa.")
                break

        cv2.destroyAllWindows()
        self.release_camera()

    def compare_images(self, gray_frame):
        logging.info("Camera - Compare Images")
        """Compara o frame capturado com as imagens fixas em preto e branco."""
        for idx, fixed_image in enumerate(self.fixed_images):
            resized_frame = cv2.resize(gray_frame, (fixed_image.shape[1], fixed_image.shape[0]))
            correlation = cv2.matchTemplate(resized_frame, fixed_image, cv2.TM_CCOEFF_NORMED)
            max_corr = np.max(correlation)

            # Captura apenas os dois primeiros dígitos antes do ponto
            if max_corr >= 100:
                formatted_corr = str(max_corr)[:3]  # Trunca para os três primeiros caracteres
            elif max_corr >= 10:
                formatted_corr = str(max_corr)[:2]  # Trunca para os dois primeiros caracteres
            else:
                formatted_corr = f"{max_corr:.2f}"  # Formata para dois dígitos após o ponto se menor que 10

            logging.info(f"Imagem fixa {idx + 1}, correlação máxima: {formatted_corr}")

            if max_corr >= 0.2:  # Ajuste do limiar de correlação
                
                logging.info(f"Imagem {idx + 1} reconhecida com correlação de {formatted_corr}")
                return True
        logging.error(f"Nenhuma imagem reconhecida.")
        return False


##############################################
# HTTP Server (Flask) for Hardware Functions #
##############################################

app = Flask(__name__)
CORS(app)

# Global objects for hardware and camera integration.
hardware_controller = HardwareController()


@app.route('/trigger/<int:pin>', methods=['GET'])
def trigger_pin(pin):
    """
    Triggers a specified GPIO pin.
    Example: GET /trigger/19
    """
    try:
        hardware_controller.acionar_saida(pin)
        return jsonify({"message": f"Triggered pin {pin}"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/capture/<int:camera>', methods=['GET'])
def capture_image(camera):
    """
    Commands the camera process to capture an image and compare it against fixed images.
    Example: GET /capture
    """
    try:
        if parent_conn:
            parent_conn.send('camera{camera}')

            time.sleep(2)

            parent_conn.send('c')
            
            time.sleep(5)

            if parent_conn.poll():
                result = parent_conn.recv()
                return jsonify({"result": result}), 200
            else:
                return jsonify({"error": "Timeout waiting for camera response"}), 504
        else:
            return jsonify({"error": "Camera pipe not available"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/health', methods=['GET'])
def healthCheck():
    return jsonify({"result": "OK"}), 200

@app.route('/quit', methods=['GET'])
def quit_camera():
    """
    Sends a quit command to the camera process.
    Example: GET /quit
    """
    try:
        if parent_conn:
            parent_conn.send('q')
            return jsonify({"message": "Sent quit command to camera process"}), 200
        else:
            return jsonify({"error": "Camera pipe not available"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


##############################################
# Main Block to Run the Server and Clean Up  #
##############################################

if __name__ == "__main__":
    try:
        parent_conn, child_conn = multiprocessing.Pipe()
        camera_process_obj = multiprocessing.Process(target=camera_process, args=(child_conn,))
        camera_process_obj.start()
        app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        print("Server interrupted by user.")
    finally:
        try:
            if parent_conn:
                parent_conn.send('q')
        except Exception as e:
            print(f"Error sending quit command: {e}")
        camera_process_obj.join()
        hardware_controller.cleanup()
        print("Application terminated.")
