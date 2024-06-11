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

#    def recognize_speech():
#        nonlocal current_menu_item, listening, selected_item
#        while True:
#            if listening:
#                with sr.Microphone() as source:
#                    recognizer.adjust_for_ambient_noise(source)
#                    print("Escuchando...")
#                    try:
#                        audio = recognizer.listen(source, timeout=5)
#                        command = recognizer.recognize_google(audio, language="es-ES")
#                        command = command.lower()
#                        if "siguiente" in command:
#                            current_menu_item = (current_menu_item + 1) % len(menu_items)
#                            print(f"Comando reconocido: {command}, cambiando a {menu_items[current_menu_item]}")
#                        elif "seleccionar" in command:
#                            selected_item = menu_names[current_menu_item]
#                            print(f"Comando reconocido: {command}, seleccionando {selected_item}")
#                            break
#                        elif "estatico" in command:
#                            modo = "Estatico"
#                            print(f"Comando reconocido: {command}, seleccionando modo {modo}")
#                        elif "dinamico" in command:
#                            modo = "Dinamico"
#                            print(f"Comando reconocido: {command}, seleccionando modo {modo}")
#                    except sr.WaitTimeoutError:
#                        print("Tiempo de espera agotado, intentando nuevamente...")
#                    except sr.UnknownValueError:
#                        print("No se entendió el comando")
#                    except sr.RequestError:
#                        print("Error en el servicio de reconocimiento de voz")
#                listening = False

#    def recognize_speech():
#      global modo, current_menu_item, listening, selected_item
#      with sr.Microphone() as source:
#          recognizer.adjust_for_ambient_noise(source)
#          while True:
#              if listening:
#                  print("Escuchando...")
#                  try:
#                      audio = recognizer.listen(source, timeout=5)
#                      command = recognizer.recognize_google(audio, language="es-ES").lower()
#                      
#                      if "siguiente" in command:
#                          current_menu_item = (current_menu_item + 1) % len(menu_items)
#                          print(f"Comando reconocido: {command}, cambiando a {menu_items[current_menu_item]}")
#                      
#                      elif "seleccionar" in command:
#                          selected_item = menu_items[current_menu_item]
#                          print(f"Comando reconocido: {command}, seleccionando {selected_item}")
#                          break
#                      
#                      elif "estatico" in command:
#                          modo = "Estatico"
#                          print(f"Comando reconocido: {command}, seleccionando modo {modo}")
#                      
#                      elif "dinamico" in command:
#                          modo = "Dinamico"
#                          print(f"Comando reconocido: {command}, seleccionando modo {modo}")
#                  
#                  except sr.WaitTimeoutError:
#                      print("Tiempo de espera agotado, intentando nuevamente...")
#                  
#                  except sr.UnknownValueError:
#                      print("No se entendió el comando")
#                  
#                  except sr.RequestError as e:
#                      print(f"Error en el servicio de reconocimiento de voz: {e}")
#                  
#                  listening = False

    audio_queue = queue.Queue()

    def capture_audio():
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)
            while True:
                if listening:
                    print("Escuchando...")
                    try:
                        audio = recognizer.listen(source, timeout=5)
                        audio_queue.put(audio)
                    except sr.WaitTimeoutError:
                        print("Tiempo de espera agotado, intentando nuevamente...")

    def recognize_speech():
        global modo, current_menu_item, listening, selected_item
        while True:
            if not audio_queue.empty():
                audio = audio_queue.get()
                try:
                    command = recognizer.recognize_google(audio, language="es-ES").lower()
                    
                    if "siguiente" in command:
                        current_menu_item = (current_menu_item + 1) % len(menu_items)
                        print(f"Comando reconocido: {command}, cambiando a {menu_items[current_menu_item]}")
                    
                    elif "seleccionar" in command:
                        selected_item = menu_names[current_menu_item]
                        print(f"Comando reconocido: {command}, seleccionando {selected_item}")
                        break
                    
                    elif "estatico" in command:
                        modo = "Estatico"
                        print(f"Comando reconocido: {command}, seleccionando modo {modo}")
                    
                    elif "dinamico" in command:
                        modo = "Dinamico"
                        print(f"Comando reconocido: {command}, seleccionando modo {modo}")
                
                except sr.UnknownValueError:
                    print("No se entendió el comando")
                
                except sr.RequestError as e:
                    print(f"Error en el servicio de reconocimiento de voz: {e}")

    # Crear hebras para captura de audio y reconocimiento de voz
    audio_thread = threading.Thread(target=capture_audio, daemon=True)
    recognize_thread = threading.Thread(target=recognize_speech, daemon=True)

    audio_thread.start()
    recognize_thread.start()

    # Crear un hilo para el reconocimiento de voz
    #voice_thread = threading.Thread(target=recognize_speech, daemon=True)
    #voice_thread.start()

    # Inicializar el tiempo de detección
    
    ultimo_tiempo_deteccion = time.time()

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
            ultimo_tiempo_deteccion = time.time()  # Actualizar el tiempo de detección

            # Dibujar los marcadores detectados
            frame = cv2.aruco.drawDetectedMarkers(frame, corners)

            # Iterar sobre cada marcador detectado
            #for corner in corners:
            #    # Obtener el punto superior izquierdo del marcador
            #    top_left = tuple(corner[0][0].astype(int))
            #
            #    # Dibujar el menú (un rectángulo simple en este ejemplo)
            #    cv2.rectangle(frame, top_left, (top_left[0] + 300, top_left[1] + 100), (125, 125, 125), -1)
            #    # Mostrar solo el ítem del menú actual
            #    cv2.putText(frame, menu_items[current_menu_item], (top_left[0] + 10, top_left[1] + 30), 
            #                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)

            # Iterar sobre cada marcador detectado
            for i in range(len(ids)):
                id_marcador = ids[i][0]
                corner = corners[i]

                # Obtener el ingrediente asociado al marcador
                ingrediente = obtener_ingrediente_por_marcador(int(id_marcador))

                if ingrediente is not None:
                    # Obtener las recetas asociadas al ingrediente
                    recetas = obtener_recetas_por_ingrediente(ingrediente[0])

                    # Obtener el punto superior izquierdo del marcador
                    top_left = tuple(corner[0][0].astype(int))

                    # Dibujar el menú (un rectángulo simple en este ejemplo)
                    cv2.rectangle(frame, top_left, (top_left[0] + 300, top_left[1] + 100 + 20*len(recetas)), (125, 125, 125), -1)

                    # Mostrar el ingrediente y las recetas en el cuadro
                    cv2.putText(frame, f"Ingrediente: {ingrediente}", (top_left[0] + 10, top_left[1] + 30), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
                    for idx, receta in enumerate(recetas):
                        cv2.putText(frame, receta, (top_left[0] + 10, top_left[1] + 60 + 20*idx), 
                                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)

        else:
            # Comprobar si han pasado más de 3 segundos sin detectar marcadores
            if time.time() - ultimo_tiempo_deteccion > 3:
                # Restablecer el ítem del menú
                current_menu_item = 0

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

        # Mostrar el cuadro con el menú superpuesto
        cv2.imshow('AR Menu', frame)

        # Salir con el espacio
        if cv2.waitKey(1) & 0xFF == ord(' '):
            break

    # Liberar la captura y cerrar ventanas
    cap.release()
    cv2.destroyAllWindows()

    return selected_item
