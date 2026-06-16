import argparse
import cv2
from ultralytics import YOLO
import pytesseract
import os
from datetime import datetime
import re
import time

MODEL_PATH = "placa.pt"
CONF_THRESHOLD = 0.35
IMGSZ = 864
SAVE_DIR = "resultados"

os.makedirs(SAVE_DIR, exist_ok=True)

print("Cargando YOLO...")
model = YOLO(MODEL_PATH)
print("SISTEMA PREPARADO", flush=True)

def limpiar_matricula(texto):
	texto = str(texto).upper().strip()
	texto = re.sub(r'[^A-Z0-9]', '', texto)
	match = re.search(r'(\d{4})([A-Z]{3})', texto)
	#if len(texto) >= 6 and texto[:4].isdigit() and texto[4:].isalpha():
	if match:
		return f"{match.group(1)} {match.group(2)}"
		#return f"{texto[:4]} {texto[4:]}"
	#return texto if len(texto) >= 5 else ""
	return texto[:8] if len(texto) >= 5 else ""

def procesar_imagen(ruta_imagen):
	start = time.time()
	img = cv2.imread(ruta_imagen)
	if img is None:
		print("Error al leer la imagen", flush=True)
		return

	img_result = img.copy()

	results = model.predict(source=img, conf=CONF_THRESHOLD, imgsz=IMGSZ, device="cpu", verbose=False)

	if len(results[0].boxes) == 0:
		print("No se detecto matricula", flush=True)
		return

	box = results[0].boxes[0]
	conf = box.conf.item()
	x1, y1, x2, y2 = map(int, box.xyxy[0])
	#print(f"YOLO DETECTO PLACA CON CONFIANZA: {box.conf.item():.2f}", flush=True)

	#height = y2 - y1
	#width = x2 - x1
	#y1_new = y1 + int(height * 0.45)
	#y2_new = y2 - int(height * 0.15)

	cv2.rectangle(img_result, (x1, y1), (x2, y2), (0, 255, 100), 3)
	#cv2.rectangle(img_result, (x1, y1_new), (x2, y2_new), (0, 255, 0), 4)
	cv2.putText(img_result, f"conf: {conf:.2f}", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

	placa = img[y1:y2, x1:x2]

	gray = cv2.cvtColor(placa, cv2.COLOR_BGR2GRAY)
	gray = cv2.resize(gray, None, fx=3.0, fy=3.0, interpolation=cv2.INTER_CUBIC)
	#denoised = cv2.bilateralFilter(gray, 11, 90, 90)
	denoised = cv2.fastNlMeansDenoising(gray, None, h=10, searchWindowSize=21, templateWindowSize=7)
	clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(8,8))
	enhanced = clahe.apply(denoised)

	_, thresh = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)


	#custom_config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
	custom_config = r'''--oem 3 --psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 -c tessedit_do_invert=1 --dpi 300'''

	texto = pytesseract.image_to_string(thresh, config=custom_config, lang='spa').strip()

	#print(f"texto crudo de tesseract: '{texto}'", flush=True)

	matricula = limpiar_matricula(texto)

	if matricula:
		print(matricula, flush=True)
		cv2.putText(img_result, matricula, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 3)
	else:
		print(texto, flush=True)

	#timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
	#salida = os.path.join(SAVE_DIR, f"matricula_{timestamp}.jpg")
	#cv2.imwrite(salida, img_result)
	#cv2.imwrite(os.path.join(SAVE_DIR, f"thresh_{timestamp}.jpg"), thresh)

	#print(f"Tiempo total: {time.time()-start:.2f} segundos\n", flush=True)

while True:
	ruta_imagen = input()
	#ruta_imagen = "coche.jpeg"
	procesar_imagen(ruta_imagen)

