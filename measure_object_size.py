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
    ALTURA_MARCADOR_CM = 5.0  # Supondo que cada marcador tem 5 cm de altura
    MARCADORES_POR_ESTACA = 4  # Cada estaca tem 4 marcadores

    if marker_ids is not None:
        altura_grama = MARCADORES_POR_ESTACA * ALTURA_MARCADOR_CM - (ALTURA_MARCADOR_CM * len(marker_ids))
    else:
        altura_grama = 0.0

    return altura_grama


input_image = cv2.imread("teste.webp")

# Identificando marcadores
dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
parameters = cv2.aruco.DetectorParameters()

detector = cv2.aruco.ArucoDetector(dictionary, parameters)
marker_corners, marker_ids, rejected_candidates = detector.detectMarkers(input_image)

# Mostrando
output_image = input_image.copy()
cv2.aruco.drawDetectedMarkers(output_image, marker_corners, marker_ids)
cv2.namedWindow("contornos", cv2.WINDOW_NORMAL)
cv2.imshow("contornos", output_image)
cv2.waitKey(0)



print(f'ID da estaca: {id_estaca(marker_corners, marker_ids)}')
print(f'Altura da grama: {altura_grama(marker_ids)} cm')



