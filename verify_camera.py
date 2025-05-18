import base64
import time

import cv2

if __name__ == '__main__':
    cap = cv2.VideoCapture(0)

    time.sleep(1)

    ret, frame = cap.read()

    # Converte para escala de cinza
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Codifica em JPEG
    success, buffer = cv2.imencode('.jpg', gray_frame)
    if not success:
        raise RuntimeError("Falha ao codificar o frame em JPEG")

    # Converte o buffer em bytes e depois em Base64
    jpg_bytes = buffer.tobytes()
    b64_str = base64.b64encode(jpg_bytes).decode('utf-8')

    # Monta o Data URI
    data_uri = f"data:image/jpeg;base64,{b64_str}"

    print(data_uri)

    # Libera a câmera
    cap.release()