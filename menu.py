import cv2
import numpy as np
import speech_recognition as sr
import threading
from bbdd import obtenerMenu

# Función que muestra el menú y permite seleccionar una receta mediante comandos de voz
def iniciar_menu_ar():
    
    # Inicializar el menú con los nombres de las recetas y sus ingredientes
    menu_items = [f"{nombre}: {ingredientes}" for nombre, ingredientes in obtenerMenu()]
    menu_names = [nombre for nombre, ingredientes in obtenerMenu()]

    # Iniciar la captura de video
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: No se puede abrir la cámara")
        return

    # Cargar el diccionario de marcadores ArUco
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_50)
    # Crear los parámetros del detector ArUco
    parameters = cv2.aruco.DetectorParameters()

    # Variable para rastrear el ítem del menú actual
    current_menu_item = 0

    # Inicializar el reconocedor de voz
    recognizer = sr.Recognizer()
    listening = False
    selected_item = None

    def recognize_speech():
        nonlocal current_menu_item, listening, selected_item
        while True:
            if listening:
                with sr.Microphone() as source:
                    recognizer.adjust_for_ambient_noise(source)
                    print("Escuchando...")
                    try:
                        audio = recognizer.listen(source, timeout=5)
                        command = recognizer.recognize_google(audio, language="es-ES")
                        command = command.lower()
                        if "siguiente" in command:
                            current_menu_item = (current_menu_item + 1) % len(menu_items)
                            print(f"Comando reconocido: {command}, cambiando a {menu_items[current_menu_item]}")
                        elif "seleccionar" in command:
                            selected_item = menu_names[current_menu_item]
                            print(f"Comando reconocido: {command}, seleccionando {selected_item}")
                            break
                    except sr.WaitTimeoutError:
                        print("Tiempo de espera agotado, intentando nuevamente...")
                    except sr.UnknownValueError:
                        print("No se entendió el comando")
                    except sr.RequestError:
                        print("Error en el servicio de reconocimiento de voz")
                listening = False

    # Crear un hilo para el reconocimiento de voz
    voice_thread = threading.Thread(target=recognize_speech, daemon=True)
    voice_thread.start()

    while selected_item is None:
        # Capturar el cuadro
        ret, frame = cap.read()
        if not ret:
            print("Error: No se puede recibir el cuadro (stream finalizado?)")
            break

        # Convertir a escala de grises
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detectar los marcadores ArUco
        corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(gray, aruco_dict, parameters=parameters)

        if ids is not None and len(ids) > 0:
            # Se detectaron marcadores
            listening = True

            # Dibujar los marcadores detectados
            frame = cv2.aruco.drawDetectedMarkers(frame, corners, ids)

            # Iterar sobre cada marcador detectado
            for corner in corners:
                # Obtener el punto superior izquierdo del marcador
                top_left = tuple(corner[0][0].astype(int))

                # Dibujar el menú (un rectángulo simple en este ejemplo)
                cv2.rectangle(frame, top_left, (top_left[0] + 300, top_left[1] + 100), (125, 125, 125), -1)
                # Mostrar solo el ítem del menú actual
                cv2.putText(frame, menu_items[current_menu_item], (top_left[0] + 10, top_left[1] + 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
        else:
            # No se detectaron marcadores, restablecer el ítem del menú
            current_menu_item = 0

        # Mostrar el cuadro con el menú superpuesto
        cv2.imshow('AR Menu', frame)

        # Salir con la tecla 'q'
        if cv2.waitKey(1) & 0xFF == ord(' '):
            break

    # Liberar la captura y cerrar ventanas
    cap.release()
    cv2.destroyAllWindows()

    return selected_item
