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
            nombre TEXT,
            alergias TEXT,
            preferencias TEXT
        )
    ''')

    # Crear tabla de recetas (añadir ruta del modelo 3D y su escala, además del marcador asociado)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recetas (
            id INTEGER PRIMARY KEY,
            nombre TEXT,
            ingredientes TEXT,
            propiedades TEXT
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

def insertarReceta(nombre, ingredientes, propiedades):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO recetas (nombre, ingredientes, propiedades) VALUES (?, ?, ?)
    ''', (nombre, ingredientes, propiedades))
    conn.commit()
    conn.close()

def consultarUsuarios():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM usuarios')
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

def esAptaParaUsuario(id_usuario, id_receta):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute('SELECT alergias, preferencias FROM usuarios WHERE id = ?', (id_usuario,))
    usuario = cursor.fetchone()
    alergias_usuario = usuario[0].split(',')
    preferencias_usuario = usuario[1].split(',')

    cursor.execute('SELECT propiedades FROM recetas WHERE id = ?', (id_receta,))
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
def borrarTablas():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS usuarios')
    cursor.execute('DROP TABLE IF EXISTS recetas')
    conn.commit()
    conn.close()


def recetasAptasConIngrediente(id_usuario, ingrediente):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('SELECT id, nombre FROM recetas WHERE ingredientes LIKE ?', ('%' + ingrediente + '%',))
    recetas = cursor.fetchall()
    recetas_aptas = []

    for receta in recetas:
        id_receta, nombre_receta = receta
        if esAptaParaUsuario(id_usuario, id_receta):
            recetas_aptas.append(nombre_receta)

    conn.close()
    return recetas_aptas

