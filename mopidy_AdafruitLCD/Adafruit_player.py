import logging
import traceback
import pykka
import mopidy
from mopidy import core
import threading

import Adafruit_CharLCD as LCD
from .Adafruit_LCD_plate import LCDplate
from .Adafruit_player_menus import menus

logger = logging.getLogger(__name__)

class AdafruitPlayer():
	def __init__(self,core):
		self.core = core
		self.track = None
		self.state = [None,None] #old,new
		self.inMenus = False
		self.plate = LCDplate()
		self.plate.start("Starting".center(16),"Mopidy LCD".center(16))
		self.running = False
		self.resumeFlag = False
		self.thread = threading.Thread(target=self.buttonLoop)
		self.tracklist_change_ignore = []
		self.core.playback.volume = 50
		self.menus=menus(core,self,self.plate)

		
	def run(self):
		self.running = True
		self.thread.start()
		traceback.print_exc()
		
	def buttonLoop(self):		
		while self.running:			
			self.newbutton = self.plate.waitForButton()
			if self.newbutton == LCD.UP or self.newbutton == LCD.DOWN:
				#volume change
				self.plate.clear()
				self.menus.volume_change()
			elif self.newbutton == LCD.LEFT:
				self.togglePause()
			elif self.newbutton == LCD.RIGHT:
				self.nextTrack()
			elif self.newbutton ==LCD.SELECT:
				self.menus.menu()				
			elif self.newbutton == -1:
				self.plate.clear()
				
	def togglePause(self):
		if self.state[1] == "playing":
			self.core.playback.pause()
			self.updatePlaybackState("playing","paused") # will update again later, but this will update instantly.
		elif self.state[1] == "paused":
			if self.resumeFlag:
				#track was changed during pause
				self.core.playback.play(self.core.playback.current_tl_track.get())
				self.resumeFlag = False
			else:
				self.core.playback.resume()
			self.updatePlaybackState("paused","playing")
			
	def nextTrack(self):
		# Skip to next song				
		nextTrack = self.core.tracklist.next_track(self.core.playback.current_tl_track.get()).get()
		if nextTrack == None:
			self.plate.smessage("    Playlist",line=0)
			self.plate.smessage("    finished",line=1)
		else:					
			self.updateCurrentTrack(nextTrack.track,screenUpdate=False)			
			#Show loading symbol &next track in ~3second downtime until mopidy sends info.
			self.displaySongInfo(forceSymbol="\x04")
			#add track to ignore list so that player ignores the late track_changed event
			self.tracklist_change_ignore.append(nextTrack.track)
		#for some reason, playback.next() won't move to the next song if this one is paused.				
		
		if self.state[1] == "paused":
			self.resumeFlag = True
		self.core.playback.next()

		

					

	def changePlayback(self,newState):
		#todo: remove?
		if newState == "playing":
			self.state[0] = "playing"
			self.state[1] = "paused"
	def compareTracks(self,track1,track2):
		return track1.uri==track2.uri

	def updateCurrentTrack(self,track,screenUpdate=True):
		if self.track == None or self.track.uri != track.uri:
			if len(self.tracklist_change_ignore) != 0 and self.compareTracks(track,self.tracklist_change_ignore[0]):
				self.tracklist_change_ignore.pop(0)
			else:
				#not a redundant update	
				self.track = track		
				if not self.inMenus and screenUpdate:
					self.displaySongInfo()
		elif len(self.tracklist_change_ignore) != 0 and self.track.uri == track.uri:			
			if self.compareTracks(track,self.tracklist_change_ignore[0]):
				self.tracklist_change_ignore.pop(0)

			
	def track_playback_ended(self,track):
		#called when skipping songs when paused, so clear tracklist_change_ignore
		if self.compareTracks(track,self.tracklist_change_ignore[0]):
			self.tracklist_change_ignore.pop(0)

	def updatePlaybackState(self,old,new):
		if self.state[0] != old or self.state[1] != new:
			#new playback state
			self.state[0] = old
			self.state[1] = new
			if not self.inMenus:
				self.plate.smessage(self.getPlaybackSymbol(),whitespace=False)
			
	def getArtistsAsString(self,artists):
		self.artistsString = ""
		for artist in artists:
			self.artistsString += artist.name
			if len(artists)>1:
				self.artistsString +=","
		return self.artistsString
		
	def getPlaybackSymbol(self):
		if self.state[1] == "playing":
			return "\x01"
		elif self.state[1] == "paused":
			return "\x02"
		elif self.state[1] == "stopped" and self.state[0] != "playing": #loading symbol instead
			if self.track == None:
				return ""
			else:
				return "\x03"
		elif self.state[1] == "stopped" and self.state[0] == "playing":
			return "\x04"
		elif self.state[1] == None:
			return ""
		else:
			logger.error("[ALCD] Unknown playback State: " + str(self.state[1]))
			

	def displaySongInfo(self,forceSymbol=""):
		if forceSymbol == "":
			self.plate.smessage(self.getPlaybackSymbol()+self.track.name)			
		else:
			self.plate.smessage(forceSymbol+self.track.name)	
		self.plate.smessage(self.getArtistsAsString(self.track.artists),line=1)

	def stop(self):		
		self.running = False
		self.plate.stop()
	

		
