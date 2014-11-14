import Adafruit_CharLCD_Mod as LCD
import logging
import traceback
#import pykka
#import mopidy
#from mopidy import core
import threading
from time import sleep


logger = logging.getLogger(__name__)

class LCDplate():
	def __init__(self):
		self.lcd = LCD.Adafruit_CharLCDPlate()
		self.running = False
		self.pressed = threading.Event()
		self.up = threading.Event()
		self.left = threading.Event()
		self.right = threading.Event()
		self.select = threading.Event()
		self.down = threading.Event()
		self.messageFlag = threading.Event()
		self.wait_for_release = True
		self.blistener = threading.Thread(target=self.buttonListener)
		self.lcd.create_char(1,[0,8,12,14,12,8,0,0]) #Play symbol 
		self.lcd.create_char(2,[0,10,10,10,10,10,0,0]) #Pause Symbol
		self.lcd.create_char(3,[0,14,14,14,14,14,14,0]) #stopped symbol
		self.lcd.create_char(4,[0,8,8,9,5,3,15,0]) #Loading symbol. Down-right facing arrow.
		self.lcd.create_char(5,[31,31,31,31,31,31,31,31]) # Block symbol for volume bar
		
	def start(self,line1,line2):
		self.lcd.set_color(1,0,0) #backlight on for white/blue 16x2
		self.messageFlag.set()	
		self.running = True			
		self.blistener.start()		
		self.smessage(line1,clear=True)
		self.smessage(line2,line=1)
	
	def buttonListener(self):
		#buttons = ((LCD.SELECT,False),(LCD.UP,False),(LCD.DOWN,False),(LCD.LEFT,False),(LCD.RIGHT,False))
		self.buttons = (LCD.SELECT,LCD.UP,LCD.DOWN,LCD.LEFT,LCD.RIGHT)
		while self.running:			
			for button in self.buttons:
				if self.lcd.is_pressed(button):					
					#Wait for release
					time = 0
					while self.lcd.is_pressed(button) and self.wait_for_release:						
						sleep(0.1)
						if button == LCD.SELECT:
							time += 0.1
							if time >= 5:
								self.lcd.clear()
					#button released, fire events											
					if button == LCD.SELECT:
						self.select.set()						
					elif button == LCD.UP:
						self.up.set()
					elif button == LCD.DOWN:
						self.down.set()
					elif button == LCD.LEFT:
						self.left.set()
					elif button == LCD.RIGHT:
						self.right.set()
					self.pressed.set()
				else:
					sleep(0.01)
		self.pressed.set() #needed to exit .wait() in waitForButton cleanly
	
	def waitForButton(self,timeout=None,release=True):
		self.wait_for_release = release
		self.pressedButton = -1 #quit signal
		self.pressed.wait(timeout)	
		if self.right.is_set():
			self.pressedButton=LCD.RIGHT
		elif self.left.is_set():
			self.pressedButton=LCD.LEFT
		elif self.up.is_set():
			self.pressedButton=LCD.UP
		elif self.down.is_set():
			self.pressedButton=LCD.DOWN
		elif self.select.is_set():
			self.pressedButton=LCD.SELECT
		self.pressed.clear()
		self.up.clear()
		self.select.clear()
		self.down.clear()
		self.left.clear()
		self.right.clear()
		return self.pressedButton						
				
	def message(self,line1,line2):
		#TODO: get rid of this old function			
		self.lcd.clear()		
		self.lcd.message(line1 + "\n" + line2)
		logger.error("Old display used: " +line1+" " +line2)
	def clear(self):
		self.lcd.clear()
	def smessage(self,text,clear=False,whitespace=True,col=0,line=0):
		#whitespace will fill message with " " if text < 16 chars to erase old text
		try:
			try:
				msg = text.encode("ascii",'ignore')
			except:
				logger.error("Error pushing to display: unable to decode string")
				msg = text
			self.messageFlag.wait()
			self.messageFlag.clear() #attempt to stop screen from pushing garbage when multiple messages get sent
			if clear:
				self.lcd.clear()		
			if whitespace:
				self.lcd.message(msg.ljust(16),col,line)
			else:
				self.lcd.message(msg,col,line)
			self.messageFlag.set()
		except:
			logger.error("error updating display in smessage")
			traceback.print_exc()
			
			
	def stop(self):	
		self.running = False
		self.pressed.set() 
		sleep(0.2) #wait for waitforbutton to stop
		self.lcd.set_color(0,0,0) #backlight off for white/blue 16x2
		self.lcd.clear()

