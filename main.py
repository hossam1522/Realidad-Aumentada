import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox, QVBoxLayout, QPushButton, QLabel, QLineEdit, QCheckBox, QGridLayout
import cv2
import face_recognition
import numpy as np
from practica import cargarModelo, mostrarModelo, devolverEscena
import bbdd
import menu
import json

def capturar_imagen():
    video_capture = cv2.VideoCapture(0)
    ret, frame = video_capture.read()
    video_capture.release()
    if ret:
        return frame
    else:
        return None

def reconocer_usuario(frame):
    known_face_encodings = []
    known_face_names = []

    usuarios = bbdd.consultarUsuarios()
    if not usuarios:
        return None  # No hay usuarios en la base de datos

    for usuario in usuarios:
        if usuario[4]:  # usuario[4] contiene la codificación facial
            encoding_usuario = json.loads(usuario[4])
            if isinstance(encoding_usuario, list) and len(encoding_usuario) == 128:
                known_face_encodings.append(np.array(encoding_usuario))
                known_face_names.append(usuario[1])  # usuario[1] es el nombre del usuario
            else:
                print(f"Codificación facial no válida para el usuario {usuario[1]}")

    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations)

    if not face_encodings:
        print("No se encontraron caras en la imagen capturada")
        return None  # No se encontraron caras en la imagen capturada

    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        if face_distances.size > 0:
            best_match_index = np.argmin(face_distances)

            if matches[best_match_index]:
                return known_face_names[best_match_index]
    return None

class RegisterWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Register')
        layout = QGridLayout()

        self.name_label = QLabel('Nombre:')
        self.name_input = QLineEdit()

        self.alergias_labels = ["Lactosa", "Gluten", "Frutos secos", "Mariscos", "Huevos"]
        self.alergias_checks = []
        for alergia in self.alergias_labels:
            check = QCheckBox(alergia)
            self.alergias_checks.append(check)

        self.preferencias_label = QLabel('Preferencias:')
        self.preferencias_input = QLineEdit()

        self.register_button = QPushButton('Register', self)
        self.register_button.clicked.connect(self.confirmar_datos)

        layout.addWidget(self.name_label, 0, 0)
        layout.addWidget(self.name_input, 0, 1)
        
        for i, check in enumerate(self.alergias_checks):
            layout.addWidget(check, i + 1, 0, 1, 2)

        layout.addWidget(self.preferencias_label, len(self.alergias_checks) + 1, 0)
        layout.addWidget(self.preferencias_input, len(self.alergias_checks) + 1, 1)

        layout.addWidget(self.register_button, len(self.alergias_checks) + 2, 0, 1, 2)

        self.setLayout(layout)

    def confirmar_datos(self):
        nombre = self.name_input.text()

        seleccion_alergias = []
        for check in self.alergias_checks:
            if check.isChecked():
                seleccion_alergias.append(check.text())

        alergias_str = ", ".join(seleccion_alergias)
        preferencias = self.preferencias_input.text()

        frame = capturar_imagen()
        if frame is None:
            QMessageBox.critical(self, "Error", "No se pudo capturar la imagen. Asegúrese de que la cámara está funcionando correctamente.")
            return

        codificacion = face_recognition.face_encodings(frame)
        if not codificacion:
            QMessageBox.critical(self, "Error", "No se ha podido codificar su rostro. Por favor, inténtelo de nuevo.")
            return
        
        json_codificacion = json.dumps(codificacion[0].tolist())

        bbdd.insertarUsuario(nombre, alergias_str, preferencias, json_codificacion)
        QMessageBox.information(self, "User Created", "Usuario creado con éxito")
        self.close()
        iniciar_programa(nombre)

def iniciar_programa(nombre):
    escena, cam, ar, mirender = devolverEscena()  # Creamos la escena y la cámara
    receta, marcador = menu.iniciar_menu_ar(nombre)
    print("Receta seleccionada: ", receta)
    
    try:
        ruta_receta, escala, tipo_archivo, rotacion = bbdd.obtener_datos_receta(receta)
    except TypeError:
        QMessageBox.critical(None, "Error", "No se ha encontrado la receta seleccionada")
        exit()

    modelo = cargarModelo(ruta_receta, escala, tipo_archivo, rotacion)  # Cargamos el modelo 3D (en formato glb)
    escena.add_node(modelo)  # Y la añadimos a la escena
    
    if menu.obtenerModo() == "Estatico":
        ar.process = lambda frame: mostrarModelo(frame, 0)
    else:
        ar.process = lambda frame: mostrarModelo(frame, marcador)
        
    try:
        ar.play("AR", key=ord(' '))
    finally:
        ar.release()

if __name__ == '__main__':
    app = QApplication(sys.argv)

    frame = capturar_imagen()
    if frame is None:
        QMessageBox.critical(None, "Error", "No se pudo capturar la imagen. Asegúrese de que la cámara está funcionando correctamente.")
        sys.exit()

    nombre = reconocer_usuario(frame)

    if nombre:
        QMessageBox.information(None, "Login Successful", f"Bienvenido de nuevo, {nombre}")
        iniciar_programa(nombre)
    else:
        QMessageBox.critical(None, "Login Failed", "No se ha encontrado ningún usuario asociado a usted. Por favor, regístrese.")
        register_window = RegisterWindow()
        register_window.show()

    sys.exit(app.exec_())
