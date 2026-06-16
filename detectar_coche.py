import subprocess
import time
import sqlite3
import os
import RPi.GPIO as GPIO

detector_matricula = subprocess.Popen(["python3", "-u", "detectar_matricula.py"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1)

DB_PATH = "usuarios.db"
TRIG = 25
ECHO = 18
coche_anterior = False
secuencia_ejecutada = False

def setup_sensor():
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(TRIG, GPIO.OUT)
	GPIO.setup(ECHO, GPIO.IN)
	print("Sensor ultrasonido preparado")

def medir_distancia():
	GPIO.output(TRIG, False)
	time.sleep(0.01)
	GPIO.output(TRIG, True)
	time.sleep(0.00001)
	GPIO.output(TRIG, False)

	pulso_inicio = time.time()
	while GPIO.input(ECHO) == 0:
		pulso_inicio = time.time()

	pulso_fin = time.time()
	while GPIO.input(ECHO) == 1:
		pulso_fin = time.time()
	duracion = pulso_fin - pulso_inicio
	distancia_cm = (duracion * 34300) / 2
	return round(distancia_cm, 1)

def conectar_db():
	conexion = sqlite3.connect(DB_PATH, check_same_thread=False)
	conexion.row_factory = sqlite3.Row
	return conexion

db_conexion = conectar_db()
print("conexion a base de datos abierta y persistente")

def verificar_usuario(matricula: str, contrasena: str, uuid:str) -> bool:
	if not uuid or not matricula or not contrasena:
		print("Faltan datos")
		return False
	try:
		cursor = db_conexion.cursor()

		uuid_limpio = uuid.replace("'", "").replace('"', "").replace("[", "").replace("]", "")
		lista_uuids = [item.strip() for item in uuid_limpio.split(",") if item.strip()]
		if not lista_uuids:
			print("No hay uuids validos")
			return False
		for item  in lista_uuids:
			query = """SELECT idusuario FROM usuarios WHERE matricula = ? AND contrasena = ? AND uuid = ? LIMIT 1"""
			cursor.execute(query, (matricula.strip(), contrasena.strip(),item,))
			resultado_usuario = cursor.fetchone()
			if resultado_usuario is not None:
				return True
		return False

	except Exception as e:
		print("Error en la consulta DB: {type(e).__name__} - {e}")
		import traceback
		traceback.print_exc()
		return False

while True:
	linea_matricula = detector_matricula.stdout.readline().strip()
	print(linea_matricula)
	if linea_matricula == "SISTEMA PREPARADO":
		time.sleep(2.0)
		os.system('clear')
		break

setup_sensor()
print("Sistema esperando vehiculo")
while True:
	#coche_detectado = True
	distancia = medir_distancia()
	#print(distancia)
	if distancia <= 150 and not secuencia_ejecutada:
		print("COCHE DETECTADO")
		detector_camara = subprocess.Popen(["sudo", "python3", "-u", "captura_imagen.py"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1)
		while True:
			linea_camara = detector_camara.stdout.readline().strip()
			#print(linea_camara)
			if linea_camara == "IMAGEN GUARDADA":
				break
		imagen  = "coche.jpeg"
		time.sleep(0.3)
		print("detectando matricula...")
		detector_matricula.stdin.write(imagen + "\n")
		detector_matricula.stdin.flush()
		resultado = detector_matricula.stdout.readline().strip()
		print(resultado)
		control_pin = 0
		while control_pin < 2:
			detector_pin = subprocess.Popen(["python3", "-u", "teclado.py"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1)
			linea_pin = detector_pin.stdout.readline().strip()
			print(linea_pin)
			control_pin = 1
			if control_pin == 1:
				linea_contrasena = detector_pin.stdout.readline().strip()
				#print(linea_contrasena)
				control_pin = 2
		control_ble = 0
		while control_ble < 1:
			detector_ble = subprocess.Popen(["sudo", "python3", "-u", "detectar_ble.py"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1)
			linea_ble = detector_ble.stdout.readline().strip()
			#print(linea_ble)
			control_ble = 1

		if resultado and linea_contrasena and linea_ble:
			autorizado = verificar_usuario(matricula=resultado, contrasena=linea_contrasena, uuid=linea_ble)
			if autorizado:
				print("usuario AUTORIZADO")
				print("barrera abierta")
			else:
				print("Acceso DENEGADO")
				#print(f"Matricula: {resultado.strip()}")
				#print(f"Ble detectados: {linea_ble}")
		else:
			print("Faltan datos de matricula, pin o ble")

		coche_anterior = True
		secuencia_ejecutada = True
		time.sleep(5.0)
		os.system('clear')
	elif distancia > 150 and coche_anterior:
		print("El coche ha pasado. Volviendo a estado de autorizacion de acceso")
		secuencia_ejecutada = False
		coche_anterior = False
		os.system('clear')
	time.sleep(0.15)
