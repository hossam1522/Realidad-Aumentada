from practica import cargarModelo, camaraPyrender, mostrarModelo, render, devolverEscena
import pyrender
import camara
import bbdd
import menu

# Preguntamos por el usuario que va a iniciar sesión
print ("Introduce tu nombre de usuario:")
nombre = input()

# Buscamos el usuario en la base de datos
existe_usuario = bbdd.usuarioExiste(nombre)

if existe_usuario:
    print("Bienvenido de nuevo, ", nombre)
else:
    print("Usuario no encontrado, por favor, introduce tus alergias y preferencias:")
    alergias = input("Alergias: ")
    preferencias = input("Preferencias: ")
    bbdd.insertarUsuario(nombre, alergias, preferencias)
    print("Usuario creado con éxito")


escena, cam, ar, mirender = devolverEscena() # Creamos la escena y la cámara

receta = menu.iniciar_menu_ar()
print ("Receta seleccionada: ", receta)
#receta = "Ramen"
ruta_receta=""
if receta == "Ramen":
    #ruta_receta = "modelos/ramen_bowl.glb"
    modelo = cargarModelo("modelos/ramen_bowl.glb") # Cargamos el modelo 3D (en formato glb)
    escena.add_node(modelo) # Y la añadimos a la escena
elif receta == "Hamburguesa":
    #ruta_receta = "modelos/hamburguesa.glb"
    modelo = cargarModelo("modelos/hamburguesa.glb")
    escena.add_node(modelo)

#modelo = cargarModelo(ruta_receta) # Cargamos el modelo 3D (en formato glb)
#escena.add_node(modelo) # Y la añadimos a la escena

# Mostrar el modelo 3D encima de un marcador de la biblioteca
ar.process = mostrarModelo
try:
    ar.play("AR", key=ord(' '))
finally:
    ar.release()