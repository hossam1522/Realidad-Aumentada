from practica import cargarModelo, mostrarModelo, devolverEscena

escena, cam, ar, mirender = devolverEscena()  # Creamos la escena y la cámara


receta = "Hamburguesa"  # Receta a probar

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
  ruta_receta = "modelos/hamburguesa/hamburguesa.obj"
  escala = 0.7
  tipo = 'obj'
  rotacion = 0.0
elif receta == "Espagueti":
  ruta_receta = "modelos/espagueti.obj"
  escala = 0.1
  tipo = 'obj'
  rotacion = 90.0
elif receta == "Tarta Chocolate":
  ruta_receta = "modelos/tarta2/Chocolate Cake.obj"
  escala = 0.05
  tipo = 'obj'
  rotacion = 90.0
elif receta == "Pizza":
  ruta_receta = "modelos/pizza.glb"
  escala = 0.1
  tipo = 'glb'
  rotacion = 0.0
elif receta == "Pancake":
  ruta_receta = "modelos/pancake.glb"
  escala = 0.7
  tipo = 'glb'
  rotacion = 180.0
elif receta == "Pastel de Manzana":
  ruta_receta = "modelos/Pastel_manzana/pastel_manzana.glb"
  escala = 0.05
  tipo = 'glb'
  rotacion = 90.0
elif receta == "Gazpacho":
  ruta_receta = "modelos/Gazpacho/gazpacho.glb"
  escala = 0.1
  tipo = 'glb'
  rotacion = 90.0
elif receta == "Lasaña":
  ruta_receta = "modelos/lasagna/lasagna.glb"
  escala = 0.5
  tipo = 'glb'
  rotacion = 0.0
elif receta == "Pollo":
  ruta_receta = "modelos/Pollo/pollo.obj"
  escala = 3.0
  tipo = 'obj'
  rotacion = 90.0
elif receta == "Tarta Nata":
  ruta_receta = "modelos/tarta1/tarta.obj"
  escala = 6.0
  tipo = 'obj'
  rotacion = 90.0
elif receta == "Macarons":
  ruta_receta = "modelos/macaron.obj"
  escala = 0.1
  tipo = 'obj'
  rotacion = 90.0
elif receta == "Pancakes":
  ruta_receta = "modelos/pancakes/pancakes.glb"
  escala = 0.2
  tipo = 'glb'
  rotacion = 90.0

modelo = cargarModelo(ruta_receta, escala, tipo, rotacion)  # Cargamos el modelo 3D (en formato glb)
escena.add_node(modelo)  # Y la añadimos a la escena

ar.process = lambda frame: mostrarModelo(frame, 1)
    
try:
    ar.play("AR", key=ord(' '))
finally:
    ar.release()