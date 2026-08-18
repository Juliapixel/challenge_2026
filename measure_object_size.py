import cv2

# Gerando marcadores
# dicionario = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
# marker_image = cv2.aruco.generateImageMarker(dicionario, 3, 200)
# cv2.imwrite("marker3.png", marker_image)

input_image = cv2.imread("marcadores5.png")

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

# Assumindo que cada marcador tem 10cm de lado, não há vão entre eles, o
# primeiro marcador está a 0cm do chão e há `TOTAL_DE_MARCADORES` marcadores no
# total

TOTAL_DE_MARCADORES = 5

altura_grama = TOTAL_DE_MARCADORES * 10 - ((TOTAL_DE_MARCADORES - len(marker_ids)) * 10)

if altura_grama > 30:
    print (" 🔴 Altura maior que 30 cm")
elif altura_grama > 15:
    print (" 🟡 Altura entre 15 e 30 cm")
else:
    print (" 🟢 Altura menor que 15 cm")

 # Função para saber o ID da estaca
 # O ID da estaca é o ID do primeiro ArUco (de cima para baixo)
def id_estaca (output_image, dictionary):
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

print(f'ID da estaca: {id_estaca(output_image, dictionary)}')




