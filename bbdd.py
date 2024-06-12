import sqlite3

def conectar():
    # Conectarse a la base de datos (o crearla si no existe)
    conn = sqlite3.connect('BBDD/cuia.db')
    return conn

def crearTablas():
    conn = conectar()
    cursor = conn.cursor()

    # Crear tabla de usuarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY,
            nombre TEXT UNIQUE,
            alergias TEXT,
            preferencias TEXT
        )
    ''')

    # Crear tabla de recetas (añadir ruta del modelo 3D y su escala)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recetas (
            id INTEGER PRIMARY KEY,
            nombre TEXT,
            ingredientes TEXT,
            propiedades TEXT,
            ruta_modelo TEXT,
            escala FLOAT
        )
    ''')

    # Crear tabla de ingredientes con recetas asociadas y su marcador
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ingredientes (
            id INTEGER PRIMARY KEY,
            nombre TEXT UNIQUE,
            marcador INTEGER UNIQUE
        )
    ''')

    conn.commit()
    conn.close()

def insertarUsuario(nombre, alergias, preferencias):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO usuarios (nombre, alergias, preferencias) VALUES (?, ?, ?)
    ''', (nombre, alergias, preferencias))
    conn.commit()
    conn.close()

def insertarReceta(nombre, ingredientes, propiedades, ruta_modelo, escala):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO recetas (nombre, ingredientes, propiedades, ruta_modelo, escala) VALUES (?, ?, ?, ?, ?)
    ''', (nombre, ingredientes, propiedades, ruta_modelo, escala))
    conn.commit()
    conn.close()

def borrarReceta(nombre):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM recetas WHERE nombre = ?', (nombre,))
    conn.commit()
    conn.close()

def insertarIngrediente(nombre, marcador):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO ingredientes (nombre, marcador) VALUES (?, ?)
    ''', (nombre, marcador))
    conn.commit()
    conn.close()

def consultarUsuarios():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM usuarios')
    resultados = cursor.fetchall()
    conn.close()
    return resultados

def consultarIngredientesyMarcadores():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM ingredientes')
    resultados = cursor.fetchall()
    conn.close()
    return resultados

def usuarioExiste(nombre_usuario):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM usuarios WHERE nombre = ?', (nombre_usuario,))
    existe = cursor.fetchone()[0] > 0
    conn.close()
    return existe

def consultarRecetas():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM recetas')
    resultados = cursor.fetchall()
    conn.close()
    return resultados

def obtenerMenu():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('SELECT nombre, ingredientes FROM recetas')
    recetas = cursor.fetchall()
    conn.close()
    return recetas

#def esAptaParaUsuario(id_usuario, id_receta):
#    conn = conectar()
#    cursor = conn.cursor()
#
#    cursor.execute('SELECT alergias, preferencias FROM usuarios WHERE id = ?', (id_usuario,))
#    usuario = cursor.fetchone()
#    alergias_usuario = usuario[0].split(',')
#    preferencias_usuario = usuario[1].split(',')
#
#    cursor.execute('SELECT propiedades FROM recetas WHERE id = ?', (id_receta,))
#    receta = cursor.fetchone()
#    propiedades_receta = receta[0].split(',')
#
#    conn.close()
#
#    for alergia in alergias_usuario:
#        if alergia in propiedades_receta:
#            return False
#    
#    for preferencia in preferencias_usuario:
#        if preferencia not in propiedades_receta:
#            return False
#
#    return True

def esAptaParaUsuario(nombre_usuario, nombre_receta):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute('SELECT alergias, preferencias FROM usuarios WHERE nombre = ?', (nombre_usuario,))
    usuario = cursor.fetchone()
    alergias_usuario = usuario[0].split(',')
    preferencias_usuario = usuario[1].split(',')

    cursor.execute('SELECT propiedades FROM recetas WHERE nombre = ?', (nombre_receta,))
    receta = cursor.fetchone()
    propiedades_receta = receta[0].split(',')

    conn.close()

    for alergia in alergias_usuario:
        if alergia in propiedades_receta:
            return False
    
    for preferencia in preferencias_usuario:
        if preferencia not in propiedades_receta:
            return False

    return True

# Función para borrar tablas
def borrarTablas(nombre_tabla):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS ' + nombre_tabla)
    conn.commit()
    conn.close()

def borrarTodosValoresTabla(nombre_tabla):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM ' + nombre_tabla)
    conn.commit()
    conn.close()

# Funcion para borrar todas las tablas, haya cuales haya
def borrarTodasLasTablas():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
    tablas = cursor.fetchall()
    for tabla in tablas:
        cursor.execute('DROP TABLE IF EXISTS ' + tabla[0])
    conn.commit()
    conn.close()

#def recetasAptasConIngrediente(id_usuario, ingrediente):
#    conn = conectar()
#    cursor = conn.cursor()
#    cursor.execute('SELECT id, nombre FROM recetas WHERE ingredientes LIKE ?', ('%' + ingrediente + '%',))
#    recetas = cursor.fetchall()
#    recetas_aptas = []
#
#    for receta in recetas:
#        id_receta, nombre_receta = receta
#        if esAptaParaUsuario(id_usuario, id_receta):
#            recetas_aptas.append(nombre_receta)
#
#    conn.close()
#    return recetas_aptas

def recetasAptasConIngrediente(nombre_usuario, ingrediente):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('SELECT nombre FROM recetas WHERE ingredientes LIKE ?', ('%' + ingrediente + '%',))
    recetas = cursor.fetchall()
    recetas_aptas = []

    for receta in recetas:
        nombre_receta = receta[0]
        if esAptaParaUsuario(nombre_usuario, nombre_receta):
            recetas_aptas.append(nombre_receta)

    conn.close()
    return recetas_aptas

def obtener_ruta_escala_receta(nombre_receta):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('SELECT ruta_modelo, escala FROM recetas WHERE nombre = ?', (nombre_receta,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado

# Función para obtener todos los marcadores desponibles
def obtener_todos_marcadores():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('SELECT marcador FROM ingredientes')
    resultado = cursor.fetchall()
    conn.close()
    return resultado

# Función para obtener el ingredientes asociado a un marcador
def obtener_ingrediente_por_marcador(marcador):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('SELECT nombre FROM ingredientes WHERE marcador = ?', (marcador,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado

# Obtener recetas por ingrediente
def obtener_recetas_por_ingrediente(ingrediente):
    if ingrediente is None:
        return []
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('SELECT nombre FROM recetas WHERE ingredientes LIKE ?', ('%' + ingrediente + '%',))
    resultado = cursor.fetchall()
    conn.close()
    return [row[0] for row in resultado]


def inicializarPrograma():
    borrarTodasLasTablas()
    crearTablas()
    insertarUsuario("hossam", None, None)
    insertarReceta("Ramen", "fideos, huevo, cebolla, cebollino, caldo", "sin_gluten,sin_lactosa", "modelos/ramen_bowl.glb", 1.0)
    insertarReceta("Hamburguesa", "carne, pan, lechuga, tomate, queso", "sin_gluten,sin_lactosa", "modelos/hamburguesa.glb", 0.3)
    insertarIngrediente("huevo", 1)

#inicializarPrograma()

#x = obtener_ingrediente_por_marcador(1)
#y = obtener_recetas_por_ingrediente(x[0])
#print(y)

#print(obtener_ruta_escala_receta("Ramen"))
#insertarReceta("Donut", "harina, azucar, huevo, aceite", "sin_gluten,sin_lactosa", "modelos/donut.glb", 1)
#borrarReceta("Galleta")
#insertarReceta("Galleta", "harina, azucar, huevo, mantequilla", "sin_gluten,sin_lactosa", "modelos/galleta.glb", 0.3)