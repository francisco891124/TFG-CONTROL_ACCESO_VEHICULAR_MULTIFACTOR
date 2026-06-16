from bluepy.btle import Scanner, DefaultDelegate
import sys
import time

TIMEOUT = 4
RSSI_MAX = -65

class ScanDelegate(DefaultDelegate):
	def __init__(self):
		super().__init__()

scanner = Scanner().withDelegate(ScanDelegate())
start_time = time.time()
FOUND = False
uuids_encontrados = []

try:
	while time.time() - start_time < TIMEOUT :
		devices = scanner.scan(2.0)

		for dev in devices:
			if dev.rssi >= RSSI_MAX:
				for (adtype, desc, value) in dev.getScanData():
					uuid = value.lower()
					if uuid not in uuids_encontrados:
						uuids_encontrados.append(uuid)
						#print(f"UUID detectado: {uuid} | RSSI: {dev.rssi}", flush=True)
						FOUND = True
		time.sleep(0.1)
	print(uuids_encontrados, flush=True)
	if not FOUND:
		print ("No se detecta ningun uuid", flush=True)
		sys.exit(1)
	sys.exit()
except KeyboardInterrupt:
	print ("Escaneo interrumpido por usuario", flush=True)
