import cv2
import numpy as np
import cuia
from matplotlib import pyplot as plt
import pyrender
import trimesh
import camara
import mathutils
import math
from pathlib import Path
import bbdd


diccionario = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_50)

# AVISO; Las coordenadas para referirse a los píxeles de una imagen son (columna, fila)

# Función para invertir las componentes Y y Z del opencv original para que no hay problmeas con pyrender
def fromOpencvToPyrender(rvec, tvec):
  pose = np.eye(4)
  pose[0:3,3] = tvec.T
  pose[0:3,0:3] = cv2.Rodrigues(rvec)[0]
  pose[[1,2]] *= -1
  pose = np.linalg.inv(pose)
  return(pose)


def cargarModelo(nombrefi, escala=1.0, tipo='glb', rotacion = 0.0):
  modelo_trimesh = trimesh.load(nombrefi, file_type=tipo)
  modelo_mesh = pyrender.Mesh.from_trimesh(list(modelo_trimesh.geometry.values()))

  mat_loc = mathutils.Matrix.Translation((0.0, 0.0, 0.05))

  #if rotacion:
  mat_rot = mathutils.Matrix.Rotation(math.radians(rotacion), 4, 'X')

  #mat_rot = mathutils.Matrix.Rotation(math.radians(90.0), 4, 'X')

  mat_sca = mathutils.Matrix.Scale(escala, 4)

  #if rotacion:
  meshpose = mat_loc @ mat_rot @ mat_sca
  #else:
  #  meshpose = mat_loc @ mat_sca

  #meshpose = mat_loc @ mat_rot @ mat_sca
  #meshpose = mat_loc @ mat_sca

  modelo = pyrender.Node(mesh=modelo_mesh, matrix=meshpose) # Creamos un nodo indicando la malla y su pose
  return modelo


def camaraPyrender(camara):
  fx = camara.cameraMatrix[0][0]
  fy = camara.cameraMatrix[1][1]
  cx = camara.cameraMatrix[0][2]
  cy = camara.cameraMatrix[1][2]

  camInt = pyrender.IntrinsicsCamera(fx, fy, cx, cy)
  cam = pyrender.Node(camera=camInt)
  return cam


def render(camId=0):
  bk = cuia.bestBackend(camId)
  ar = cuia.myVideo(camId, bk)
  hframe = ar.get(cv2.CAP_PROP_FRAME_HEIGHT)
  wframe = ar.get(cv2.CAP_PROP_FRAME_WIDTH)
  mirender = pyrender.OffscreenRenderer(wframe, hframe)
  return ar, mirender

def detectarPose(frame, idMarcador, tam, diccionario=diccionario):
    detector = cv2.aruco.ArucoDetector(diccionario)
    bboxs, ids, rechazados = detector.detectMarkers(frame)
    if ids is not None:
        for i in range(len(ids)):
            if ids[i] == idMarcador:
                objPoints = np.array([[-tam/2.0, tam/2.0, 0.0],
                                      [tam/2.0, tam/2.0, 0.0],
                                      [tam/2.0, -tam/2.0, 0.0],
                                      [-tam/2.0, -tam/2.0, 0.0]])
                ret, rvec, tvec = cv2.solvePnP(objPoints, bboxs[i], camara.cameraMatrix, camara.distCoeffs)
                if ret:
                    return((True, rvec, tvec))
    return((False, None, None))

def realidadMixta(renderizador, frame, escena):
    color, m = renderizador.render(escena)
    bgr = cv2.cvtColor(color, cv2.COLOR_RGB2BGR) #convertimos la imagen de color al espacio BGR

    _, m = cv2.threshold(m, 0, 1, cv2.THRESH_BINARY) #Umbralizamos la matriz de profundidad poniendo a cero los valores negativos y el resto a uno
    m = (m*255).astype(np.uint8) #Para usarla como canal alfa necesitamos expresarla en el rango [0,255] como números enteros
    m = np.stack((m,m,m), axis=2) #Creamos una imagen de 3 bandas repitiendo la máscara obtenida

    #A continuación empleamos la máscara y su inversa para combinar la imagen del frame con la imagen generada por el render
    inversa = cv2.bitwise_not(m)
    pp = cv2.bitwise_and(bgr, m)
    fondo = cv2.bitwise_and(frame, inversa)
    res = cv2.bitwise_or(fondo, pp)
    return(res)

# Función para mostrar modelos 3D en la cámara
def mostrarModelo(frame, marcador):
    ret, rvec, tvec = detectarPose(frame, marcador, 0.40) #Buscaremos el marcador 0 impreso con 19cm de lado
    if ret:
        poseCamara = fromOpencvToPyrender(rvec, tvec) #Determinamos la posición de la cámara en forma de matriz de transformación de Pyrender
        escena.set_pose(cam, poseCamara) #Ubicamos la cámara en la posición obtenido
        frame = realidadMixta(mirender, frame, escena) #Mezclamos mundo real y mundo virtual
    return(frame)


def devolverEscena():
    escena.add_node(cam)
    return escena, cam, ar, mirender


escena = pyrender.Scene(bg_color=(0,0,0), ambient_light=(1.0, 1.0, 1.0))

cam = camaraPyrender(camara)

# Mostrar el modelo 3D encima de un marcador de la biblioteca
ar, mirender = render()




# Idea -> Con una biblioteca de marcadores leer y según lo que se lea se procesa un modelo 3D