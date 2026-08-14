import cv2

# Gerando marcadores
# dicionario = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
# marker_image = cv2.aruco.generateImageMarker(dicionario, 3, 200)
# cv2.imwrite("marker3.png", marker_image)


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

# Identificando marcadores e criando parâmetros
if len(marker_ids) >= 3:
    print (" 🟢 Altura menor que 10 cm")
if len(marker_ids) == 2:
    print (" 🟡 Altura entre 10 e 30 cm")
if len(marker_ids) >= 1:
    print (" 🔴 Altura maior que 30 cm")