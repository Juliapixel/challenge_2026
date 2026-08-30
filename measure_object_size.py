import cv2


def id_estaca (marker_corners, marker_ids):
    # Se nenhum ID for identificado
    if marker_ids is None or len(marker_ids) == 0:
        return None

    marcadores = []

    for i, corner in enumerate(marker_corners):
        pontos = corner[0] # estamos alcançando as vertices de cada ArUco
        centro_altura = pontos[:,1].mean() 
        marcadores.append((int(marker_ids[i]), centro_altura))

    marcadores.sort(key=lambda m: m[1])
    primeiro_id = marcadores[0][0]

    return primeiro_id


def altura_grama(marker_ids):
    ALTURA_MARCADOR_CM = 10.0  # Supondo que cada marcador tem 10 cm de altura
   # MARCADORES_POR_ESTACA = 4  # Cada estaca tem 4 marcadores

    if marker_ids is not None:
        return len(marker_ids) * ALTURA_MARCADOR_CM
        #altura_grama = MARCADORES_POR_ESTACA * ALTURA_MARCADOR_CM - (ALTURA_MARCADOR_CM * len(marker_ids))
    else:
        #altura_grama = 0.0
        return 0.0

    return altura_grama

def verificar_poda(marker_ids):
    if marker_ids is None:
        return False

    return len(marker_ids) >= 3 # Se houver 3 ou mais marcadores, a grama precisa ser podada

# realizar a análise da imagem e retornar os resultados
def analisar_imagem(input_image):

    # identificando marcadores
    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    parameters = cv2.aruco.DetectorParameters()

    detector = cv2.aruco.ArucoDetector(dictionary, parameters)
    marker_corners, marker_ids, rejected_candidates = detector.detectMarkers(input_image)

    # Obtendo os resultados da análise
    estaca = id_estaca(marker_corners, marker_ids)
    altura = altura_grama(marker_ids)
    poda = verificar_poda(marker_ids),

    return {
        "id_estaca": estaca,
        "altura_grama": altura,
        "marcadores_detectados": len(marker_ids) if marker_ids is not None else 0,
        "necessita_poda": poda
    }
