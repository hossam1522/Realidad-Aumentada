from practica import cargarModelo, camaraPyrender, mostrarModelo, render, devolverEscena
import pyrender
import camara

escena, cam, ar, mirender = devolverEscena() # Creamos la escena y la cámara

modelo = cargarModelo("modelos/ramen_bowl.glb")
escena.add_node(modelo) # Y la añadimos a la escena

# Mostrar el modelo 3D encima de un marcador de la biblioteca
ar.process = mostrarModelo
try:
    ar.play("AR", key=ord(' '))
finally:
    ar.release()