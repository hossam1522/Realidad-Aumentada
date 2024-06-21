from practica import cargarModelo, mostrarModelo, devolverEscena

escena, cam, ar, mirender = devolverEscena()  # Creamos la escena y la cámara


receta = "Espagueti"

if receta == "Ramen":
  ruta_receta = "modelos/ramen_bowl.glb"
  escala = 1.0
  tipo = 'glb'
  rotacion = 90.0
elif receta == "Galleta":
  ruta_receta = "modelos/galleta.glb"
  escala = 0.3
  tipo = 'glb'
  rotacion = 0.0
elif receta == "Hamburguesa":
  ruta_receta = "modelos/hamburguesa.blend"
  escala = 0.3
  tipo = 'blend'
  rotacion = 90.0
elif receta == "Espagueti":
  ruta_receta = "modelos/espagueti.obj"
  escala = 0.1
  tipo = 'obj'
  rotacion = 90.0
elif receta == "Tarta Chocolate":
  ruta_receta = "modelos/Chocolate Cake.obj"
  escala = 0.05
  tipo = 'obj'
  rotacion = 90.0
elif receta == "Pizza":
  ruta_receta = "modelos/pizza.glb"
  escala = 0.1
  tipo = 'glb'
  rotacion = 0.0

modelo = cargarModelo(ruta_receta, escala, tipo, rotacion)  # Cargamos el modelo 3D (en formato glb)
escena.add_node(modelo)  # Y la añadimos a la escena

ar.process = lambda frame: mostrarModelo(frame, 0)
    
try:
    ar.play("AR", key=ord(' '))
finally:
    ar.release()