from practica import cargarModelo, mostrarModelo, devolverEscena
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

ruta_receta=""
escala = 1.0
if receta == "Ramen":
    ruta_receta = "modelos/ramen_bowl.glb"
elif receta == "Hamburguesa":
    ruta_receta = "modelos/hamburguesa.glb"
    escala = 0.3

modelo = cargarModelo(ruta_receta, escala) # Cargamos el modelo 3D (en formato glb)
escena.add_node(modelo) # Y la añadimos a la escena

# Mostrar el modelo 3D encima de un marcador de la biblioteca
ar.process = mostrarModelo
try:
    ar.play("AR", key=ord(' '))
finally:
    ar.release()