import tkinter as tk
from tkinter import messagebox
import cv2
import face_recognition
import numpy as np
from practica import cargarModelo, mostrarModelo, devolverEscena
import bbdd
import menu

def capturar_imagen():
    video_capture = cv2.VideoCapture(0)
    ret, frame = video_capture.read()
    video_capture.release()
    return frame

def reconocer_usuario(frame):
    known_face_encodings = []
    known_face_names = []

    usuarios = bbdd.consultarUsuarios()
    if not usuarios:
        return None  # No hay usuarios en la base de datos

    for usuario in usuarios:
        if usuario[4]:  # Asegurarse de que la ruta de la imagen no esté vacía
            imagen_usuario = face_recognition.load_image_file(usuario[4])
            encoding_usuario = face_recognition.face_encodings(imagen_usuario)
            if encoding_usuario:
                known_face_encodings.append(encoding_usuario[0])
                known_face_names.append(usuario[1])  # usuario[1] es el nombre del usuario

    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations)

    if not face_encodings:
        return None  # No se encontraron caras en la imagen capturada

    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        if face_distances.size > 0:
            best_match_index = np.argmin(face_distances)

            if matches[best_match_index]:
                return known_face_names[best_match_index]
    return None

def verificar_usuario():
    frame = capturar_imagen()
    nombre = reconocer_usuario(frame)

    if nombre:
        messagebox.showinfo("Login Successful", f"Bienvenido de nuevo, {nombre}")
        root.destroy()
        iniciar_programa(nombre)
    else:
        messagebox.showerror("Login Failed", "No se ha podido reconocer al usuario")
        mostrar_pantalla_login()

def mostrar_pantalla_login():
    login_window = tk.Tk()
    login_window.title("Login")

    tk.Label(login_window, text="Username:").grid(row=0, column=0, padx=10, pady=10)
    entry_username = tk.Entry(login_window)
    entry_username.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(login_window, text="Alergias:").grid(row=1, column=0, padx=10, pady=10)

    # Lista para almacenar las casillas de verificación
    alergias_checks = []
    alergias = ["Lactosa", "Gluten", "Frutos secos", "Mariscos", "Huevos"]

    row = 2
    for alergia in alergias:
        var = tk.IntVar(value=0)
        check = tk.Checkbutton(login_window, text=alergia, variable=var)
        check.grid(row=row, column=0, columnspan=2, sticky='w', padx=10, pady=5)
        alergias_checks.append((alergia, var))
        row += 1

    tk.Label(login_window, text="Preferencias:").grid(row=row, column=0, padx=10, pady=10)
    entry_preferencias = tk.Entry(login_window)
    entry_preferencias.grid(row=row, column=1, padx=10, pady=10)

    tk.Button(login_window, text="Confirmar", command=lambda: confirmar_datos(login_window, entry_username, alergias_checks, entry_preferencias)).grid(row=row+1, column=0, columnspan=2, pady=10)

    login_window.mainloop()

def confirmar_datos(login_window, entry_username, alergias_checks, entry_preferencias):
    nombre = entry_username.get()
    
    seleccion_alergias = []
    for alergia, var in alergias_checks:
        if var.get() == 1:
            seleccion_alergias.append(alergia)

    alergias_str = ", ".join(seleccion_alergias)
    preferencias = entry_preferencias.get()

    frame = capturar_imagen()
    imagen_path = f"facial/{nombre}.jpg"
    cv2.imwrite(imagen_path, frame)

    bbdd.insertarUsuario(nombre, alergias_str, preferencias, imagen_path)
    messagebox.showinfo("User Created", "Usuario creado con éxito")
    login_window.destroy()
    iniciar_programa(nombre)

def iniciar_programa(nombre):
    escena, cam, ar, mirender = devolverEscena()  # Creamos la escena y la cámara
    receta, marcador = menu.iniciar_menu_ar()
    print("Receta seleccionada: ", receta)
    
    try:
      ruta_receta, escala = bbdd.obtener_ruta_escala_receta(receta)
    except TypeError:
        messagebox.showerror("Error", "No se ha encontrado la receta seleccionada")
        return
    modelo = cargarModelo(ruta_receta, escala)  # Cargamos el modelo 3D (en formato glb)
    escena.add_node(modelo)  # Y la añadimos a la escena
    
    if menu.obtenerModo() == "Estatico":
        ar.process = lambda frame: mostrarModelo(frame, 0)
    else:
        ar.process = lambda frame: mostrarModelo(frame, marcador)
        
    try:
        ar.play("AR", key=ord(' '))
    finally:
        ar.release()

# Crear la ventana principal
root = tk.Tk()
root.withdraw()  # Ocultar la ventana principal mientras se verifica el usuario

# Intentar verificar al usuario con reconocimiento facial
verificar_usuario()

# Iniciar el bucle de eventos de tkinter
root.mainloop()
