from picamera2 import Picamera2
import cv2
import time
import os
import logging

logging.getLogger("picamera2").setLevel(logging.WARNING)
logging.getLogger("libcamera").setLevel(logging.WARNING)

RESOLUCION = (3280, 2464)
CALIDAD_JPEG = 90

picam2 = Picamera2()
config = picam2.create_still_configuration(main={"size": RESOLUCION})
picam2.configure(config)
picam2.start()

print("Camara iniciada. esperando 1 segundo para estabilizar...", flush=True)
time.sleep(1.2)

try:
	if os.path.exists("coche.jpeg"):
		os.remove("coche.jpeg")
	imagen_rgb = picam2.capture_array()
	imagen_bgr = cv2.cvtColor(imagen_rgb, cv2.COLOR_RGB2BGR)

	ancho = 640
	alto = 480
	imagen_bgr = cv2.resize(imagen_bgr, (ancho, alto), interpolation=cv2.INTER_AREA)

	nombre_archivo = "coche.jpeg"
	cv2.imwrite(nombre_archivo, imagen_bgr, [cv2.IMWRITE_JPEG_QUALITY, CALIDAD_JPEG])
	print("IMAGEN GUARDADA", flush=True)
except Exception as e:
	print(f"Error: {e}", flush =True)
finally:
	picam2.stop()
	print("Camara detenida", flush=True)

