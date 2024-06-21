import cv2
import numpy as np
import vosk
import threading
import json
import pyaudio
from bbdd import obtenerMenu, obtener_ingrediente_por_marcador, obtener_recetas_por_ingrediente, obtener_ingredientes_de_receta

modo = "Estatico"

# Inicializar el modelo de Vosk
model = vosk.Model("voz/vosk-model-small-es-0.42")

# Inicializar el stream de audio
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=4000)

def iniciar_menu_ar():
    global modo
    listening = False
    selected_item = None
    marcador = None
    ingredientes_visible = False

    # Diccionario para almacenar el estado del menú para cada marcador
    menu_states = {}

    def recognize_speech():
        nonlocal listening, selected_item, menu_states, marcador, ingredientes_visible
        global modo
        rec = vosk.KaldiRecognizer(model, 16000)

        while True:
            if listening:
                print("Escuchando...")
                while listening:
                    data = stream.read(4000, exception_on_overflow=False)
                    if len(data) == 0:
                        break
                    if rec.AcceptWaveform(data):
                        result = json.loads(rec.Result())
                        command = result.get("text", "").lower()
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
                            elif "ingredientes" in command:
                                ingredientes_visible = True
                                print(f"Mostrando ingredientes de {selected_item}")
                            elif "atrás" in command:
                                ingredientes_visible = False
                                print("Ocultando ingredientes")
                            elif "estático" in command:
                                modo = "Estatico"
                            elif "dinámico" in command:
                                modo = "Dinamico"

    # Hilo para reconocimiento de voz
    thread = threading.Thread(target=recognize_speech, daemon=True)
    thread.start()

    # Iniciar la captura de video
    cap = cv2.VideoCapture(0)
    # Acelerar la captura de video
    cap.set(cv2.CAP_PROP_FPS, 60)
    # Buffer máximo para cámara fluida
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 3)

    if not cap.isOpened():
        print("Error: No se puede abrir la cámara")
        return

    # Cargar el diccionario de marcadores ArUco
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_50)
    # Crear los parámetros del detector ArUco
    parameters = cv2.aruco.DetectorParameters()

    while selected_item is None or ingredientes_visible:
        # Capturar el cuadro
        ret, frame = cap.read()
        if not ret:
            print("Error: No se puede recibir el cuadro (stream finalizado?)")
            break

        # Convertir a escala de grises
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detectar los marcadores ArUco
        detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)
        corners, ids, rejectedImgPoints = detector.detectMarkers(gray)

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
                    cv2.putText(frame, f"Ingrediente: {ingrediente[0]}", (top_left[0] + 10, top_left[1] + 30), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
                    for idx, receta in enumerate(state['menu_items']):
                        prefix = "-> " if idx == state['current_item'] else "   "
                        cv2.putText(frame, prefix + receta, (top_left[0] + 10, top_left[1] + 60 + 20*idx), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)

                    # Mostrar los ingredientes de la receta seleccionada si se ha dado el comando
                    if ingredientes_visible:
                        ingredientes = obtener_ingredientes_de_receta(state['menu_items'][state['current_item']])
                        if ingredientes:
                            top_left_ingredientes = (top_left[0], top_left[1] + 100 + 20*len(recetas))
                            cv2.rectangle(frame, top_left_ingredientes, 
                                          (top_left_ingredientes[0] + 300, top_left_ingredientes[1] + 25*len(ingredientes)), 
                                          (0, 0, 0), -1)
                            for idx, ingrediente in enumerate(ingredientes):
                                cv2.putText(frame, ingrediente, 
                                            (top_left_ingredientes[0] + 10, top_left_ingredientes[1] + 20*(idx + 1)), 
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

def obtenerStream():
    return stream, p
#
## Llamar a la función principal
#iniciar_menu_ar()
