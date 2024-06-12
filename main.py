import tkinter as tk
from tkinter import messagebox
from practica import cargarModelo, mostrarModelo, devolverEscena
import bbdd
import menu

def verificar_usuario(event=None):  # Permitir que la función acepte un argumento opcional
    nombre = entry_username.get()
    existe_usuario = bbdd.usuarioExiste(nombre)
    
    if existe_usuario:
        messagebox.showinfo("Login Successful", f"Bienvenido de nuevo, {nombre}")
        root.destroy()
        iniciar_programa(nombre)
    else:
        messagebox.showerror("Login Failed", "Usuario no encontrado. Por favor, introduce tus alergias y preferencias.")
        mostrar_campos_alergias_preferencias()

def mostrar_campos_alergias_preferencias():
    alergias_label.grid(row=2, column=0, padx=10, pady=10)
    entry_alergias.grid(row=2, column=1, padx=10, pady=10)
    
    preferencias_label.grid(row=3, column=0, padx=10, pady=10)
    entry_preferencias.grid(row=3, column=1, padx=10, pady=10)
    
    confirmar_button.grid(row=4, column=0, columnspan=2, pady=10)

def confirmar_datos():
    nombre = entry_username.get()
    alergias = entry_alergias.get()
    preferencias = entry_preferencias.get()
    bbdd.insertarUsuario(nombre, alergias, preferencias)
    messagebox.showinfo("User Created", "Usuario creado con éxito")
    root.destroy()
    iniciar_programa(nombre)

def iniciar_programa(nombre):
    escena, cam, ar, mirender = devolverEscena()  # Creamos la escena y la cámara
    receta, marcador = menu.iniciar_menu_ar()
    print("Receta seleccionada: ", receta)
    
    #modelo = cargarModelo(ruta_receta, escala)  # Cargamos el modelo 3D (en formato glb)
    ruta_receta, escala = bbdd.obtener_ruta_escala_receta(receta)
    #datos = bbdd.obtener_ruta_escala_receta(receta)
    #ruta_receta = datos[0]
    #escala = datos[1]
    modelo = cargarModelo(ruta_receta, escala)  # Cargamos el modelo 3D (en formato glb)
    #modelo = cargarModelo("modelos/ramen_bowl.glb", 1.0)  # Cargamos el modelo 3D (en formato glb
    escena.add_node(modelo)  # Y la añadimos a la escena
    
    # Mostrar el modelo 3D encima de un marcador de la biblioteca
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
root.title("Login")

# Crear y colocar los widgets de la ventana de inicio de sesión
tk.Label(root, text="Username:").grid(row=0, column=0, padx=10, pady=10)
entry_username = tk.Entry(root)
entry_username.grid(row=0, column=1, padx=10, pady=10)
entry_username.bind("<Return>", verificar_usuario)  # Asociar la tecla Enter con la función verificar_usuario

alergias_label = tk.Label(root, text="Alergias:")
entry_alergias = tk.Entry(root)
preferencias_label = tk.Label(root, text="Preferencias:")
entry_preferencias = tk.Entry(root)
confirmar_button = tk.Button(root, text="Confirmar", command=confirmar_datos)

tk.Button(root, text="Login", command=verificar_usuario).grid(row=1, column=0, columnspan=2, pady=10)

# Iniciar el bucle de eventos de tkinter
root.mainloop()
