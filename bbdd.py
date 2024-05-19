import sqlite3

def conectar():
    # Conectarse a la base de datos (o crearla si no existe)
    conn = sqlite3.connect('BBDD/cuia.db')
    return conn

def crearTablaUsuarios():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY,
            nombre TEXT,
            edad INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def insertarUsuario(nombre, edad):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO usuarios (nombre, edad) VALUES (?, ?)
    ''', (nombre, edad))
    conn.commit()
    conn.close()

def consultarUsuarios():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM usuarios')
    resultados = cursor.fetchall()
    conn.close()
    return resultados

def borrarUsuario(id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM usuarios WHERE id = ?', (id,))
    conn.commit()
    conn.close()

def borrarTodosUsuarios():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM usuarios')
    conn.commit()
    conn.close()

def modificarUsuario(id, nombre, edad):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('UPDATE usuarios SET nombre = ?, edad = ? WHERE id = ?', (nombre, edad, id))
    conn.commit()
    conn.close()

def borrarTablas():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS usuarios')
    conn.commit()
    conn.close()

