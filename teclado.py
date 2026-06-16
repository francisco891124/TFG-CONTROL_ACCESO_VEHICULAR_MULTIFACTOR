import time
import RPi.GPIO as GPIO
import teclado_clase as teclado

Tc = teclado.teclado(6, 13, 19, 26, 17, 27, 22, 5)
digito = None
ultimo_digito = None
contrasena = ""

print ("Inroduzca la contrasena", flush=True)
try:
	while True:
		digito = Tc.getLlave()
		if not ultimo_digito == digito:
			if not digito == None:
				if len(contrasena) < 4:
					contrasena += str(digito)
				if len(contrasena) == 4:
					break
			ultimo_digito = digito
			time.sleep(0.1)
except KeyboardInterrupt:
	print ("\nScript finalizado", flush=True)
finally:
	print (contrasena, flush=True)
	Tc.exit()
	GPIO.cleanup()




