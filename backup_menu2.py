import cv2
import numpy as np
import speech_recognition as sr
import threading
import time
import queue
from bbdd import obtenerMenu, obtener_ingrediente_por_marcador, obtener_recetas_por_ingrediente

modo = "Estatico"

# Función que muestra el menú y permite seleccionar una receta mediante comandos de voz
def iniciar_menu_ar():
    global modo
    # Inicializar el reconocedor de voz
    recognizer = sr.Recognizer()
    listening = False
    selected_item = None
    marcador = None

    # Diccionario para almacenar el estado del menú para cada marcador
    menu_states = {}

    def recognize_speech():
        nonlocal listening, selected_item, menu_states, marcador
        global modo
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)
            while True:
                if listening:
                    print("Escuchando...")
                    try:
                        audio = recognizer.listen(source, timeout=5)
                        command = recognizer.recognize_google(audio, language="es-ES")
                        command = command.lower()
                        print(f"Comando reconocido: {command}")
                        for id_marcador, state in menu_states.items():
                            if "siguiente" in command:
                                state['current_item'] = (state['current_item'] + 1) % len(state['menu_items'])
                                print(f"Marcador {id_marcador}: Cambiando a {state['menu_items'][state['current_item']]}")
                            elif "seleccionar" in command:
                                selected_item = state['menu_items'][state['current_item']]
                                marcador = id_marcador
                                print(f"Marcador {id_marcador}: Item seleccionado {selected_item}")
                                listening = False
                                break
                            elif "estático" in command:
                                modo = "Estatico"
                            elif "dinámico" in command:
                                modo = "Dinamico"
                    except sr.WaitTimeoutError:
                        print("Tiempo de espera agotado")
                    except sr.UnknownValueError:
                        print("No se entendió el comando")
                    except sr.RequestError as e:
                        print(f"Error al solicitar resultados de reconocimiento de voz; {e}")

    # Hilo para reconocimiento de voz
    threading.Thread(target=recognize_speech, daemon=True).start()

    # Iniciar la captura de video
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: No se puede abrir la cámara")
        return

    # Cargar el diccionario de marcadores ArUco
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_50)
    # Crear los parámetros del detector ArUco
    parameters = cv2.aruco.DetectorParameters()

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
            listening = True
            # Dibujar los marcadores detectados
            frame = cv2.aruco.drawDetectedMarkers(frame, corners)

            # Iterar sobre cada marcador detectado
            for i in range(len(ids)):
                id_marcador = ids[i][0]
                corner = corners[i]

                # Obtener el ingrediente asociado al marcador
                ingrediente = obtener_ingrediente_por_marcador(int(id_marcador))
                if ingrediente:
                    # Obtener las recetas asociadas al ingrediente
                    recetas = obtener_recetas_por_ingrediente(ingrediente[0])

                    # Si el marcador no tiene un estado de menú, inicializarlo
                    if id_marcador not in menu_states:
                        menu_states[id_marcador] = {
                            'menu_items': recetas,
                            'current_item': 0
                        }

                    state = menu_states[id_marcador]

                    # Obtener el punto superior izquierdo del marcador
                    top_left = tuple(corner[0][0].astype(int))

                    # Dibujar el menú (un rectángulo simple en este ejemplo)
                    cv2.rectangle(frame, top_left, (top_left[0] + 300, top_left[1] + 100 + 20*len(recetas)), (125, 125, 125), -1)

                    # Mostrar el ingrediente y las recetas en el cuadro
                    cv2.putText(frame, f"Ingrediente: {ingrediente}", (top_left[0] + 10, top_left[1] + 30), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
                    for idx, receta in enumerate(state['menu_items']):
                        prefix = "-> " if idx == state['current_item'] else "   "
                        cv2.putText(frame, prefix + receta, (top_left[0] + 10, top_left[1] + 60 + 20*idx), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
        else:
            listening = False

        # Añadir un fondo al texto del modo
        text = modo
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.7
        font_thickness = 2
        text_size, _ = cv2.getTextSize(text, font, font_scale, font_thickness)
        text_w, text_h = text_size

        # Definir la posición del texto y el rectángulo
        text_x, text_y = 10, 30
        rect_x1, rect_y1 = text_x - 5, text_y - text_h - 5
        rect_x2, rect_y2 = text_x + text_w + 5, text_y + 5

        # Dibujar el rectángulo y el texto
        cv2.rectangle(frame, (rect_x1, rect_y1), (rect_x2, rect_y2), (0, 0, 0), -1)
        cv2.putText(frame, text, (text_x, text_y), font, font_scale, (255, 255, 255), font_thickness, cv2.LINE_AA)

        # Mostrar el cuadro
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord(' '):
            break

    # Liberar los recursos
    cap.release()
    cv2.destroyAllWindows()

    return selected_item, marcador

def obtenerModo():
    return modo