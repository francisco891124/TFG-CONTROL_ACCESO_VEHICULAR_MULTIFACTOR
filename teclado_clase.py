import RPi.GPIO as GPIO

class teclado():
	def __init__(self, C1, C2, C3, C4, R1, R2, R3, R4):
		GPIO.setmode(GPIO.BCM)
		GPIO.setwarnings(False)
		self.TECLADO = [[1, 2, 3, "A"],
			[4, 5, 6, "B"],
			[7, 8, 9, "C"],
			["*", 0, "#", "D"]]
		self.ROW = [R1, R2, R3, R4]
		self.COL = [C1, C2, C3, C4]
	def getLlave(self):
		for j in range (len(self.COL)):
			GPIO.setup (self.COL[j], GPIO.OUT)
			GPIO.output (self.COL[j], GPIO.LOW)
		for i  in range (len(self.ROW)):
			GPIO.setup (self.ROW[i], GPIO.IN, pull_up_down=GPIO.PUD_UP)
		rowVal = -1
		for i in range (len(self.ROW)):
			tmpLeer = GPIO.input (self.ROW[i])
			if tmpLeer == 0:
				rowVal = i
		if rowVal < 0 or rowVal > 3:
			self.exit()
			return
		for j in range (len(self.COL)):
			GPIO.setup (self.COL[j], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
		GPIO.setup (self.ROW[rowVal], GPIO.OUT)
		GPIO.output (self.ROW[rowVal], GPIO.HIGH)
		colVal = -1
		for j in range (len(self.COL)):
			tmpLeer = GPIO.input (self.COL[j])
			if tmpLeer == 1:
				colVal = j
		if colVal < 0 or colVal > 3:
			self.exit()
			return
		if len(self.COL) == 3:
			if colVal < 0 or colVal > 2:
				self.exit()
				return
		self.exit()
		return self.TECLADO[rowVal][colVal]
	def exit(self):
		for i in range (len(self.ROW)):
			GPIO.setup (self.ROW[i], GPIO.IN, pull_up_down=GPIO.PUD_UP)
		for j in range (len(self.COL)):
			GPIO.setup (self.COL[j], GPIO.IN, pull_up_down=GPIO.PUD_UP)

