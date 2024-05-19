import cv2
import numpy as np

# Iniciar la captura de video
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: No se puede abrir la cámara")
    exit()

# Cargar el diccionario de marcadores ArUco
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_50)
# Crear los parámetros del detector ArUco
parameters = cv2.aruco.DetectorParameters()

while True:
    # Capturar el cuadro
    ret, frame = cap.read()
    if not ret:
        print("Error: No se puede recibir el cuadro (stream finalizado?)")
        break

    # Convertir a escala de grises
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detectar los marcadores ArUco
    corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(gray, aruco_dict, parameters=parameters)

    # Si se detectan marcadores
    if ids is not None:
        # Dibujar los marcadores detectados
        frame = cv2.aruco.drawDetectedMarkers(frame, corners, ids)

        # Iterar sobre cada marcador detectado
        for corner in corners:
            # Obtener el punto superior izquierdo del marcador
            top_left = tuple(corner[0][0].astype(int))

            # Dibujar el menú (un rectángulo simple en este ejemplo)
            cv2.rectangle(frame, top_left, (top_left[0] + 150, top_left[1] + 100), (125, 125, 125), -1)
            cv2.putText(frame, "Menu Item 1", (top_left[0] + 10, top_left[1] + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
            # Poner más items de menú aquí
            cv2.putText(frame, "Menu Item 2", (top_left[0] + 10, top_left[1] + 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(frame, "Menu Item 3", (top_left[0] + 10, top_left[1] + 70), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)


    # Mostrar el cuadro con el menú superpuesto
    cv2.imshow('AR Menu', frame)

    # Salir con la tecla 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar la captura y cerrar ventanas
cap.release()
cv2.destroyAllWindows()
