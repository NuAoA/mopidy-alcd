#!/usr/bin/env python

import logging
import traceback
import pykka
import mopidy
import sys
import re #todo: remove
import threading
from time import sleep
from mopidy import core

from .Adafruit_player import AdafruitPlayer
logger = logging.getLogger(__name__)

class AdafruitLCD(pykka.ThreadingActor, core.CoreListener):
	def __init__(self,config,core):
		super(AdafruitLCD,self).__init__()
		self.core = core
		self.player = AdafruitPlayer(core)
		self.startup = threading.Thread(target=self.media_scan)
		#self.player.run()
	
	def media_scan(self):
		media_list = []
		timeout = 0
		self.player.plate.smessage("Loading Media...")
		sleep(2)
		while self.player.running:
			if timeout>=50 or self.player.inMenus:
				if not self.player.inMenus:
					if len(media_list)==0:					
						self.player.plate.smessage("No Media Found",line=1)
					elif self.player.track!=None:
						self.player.displaySongInfo()
				break
			update = False
			list = self.core.library.browse(None).get()
			for media in list:
				if media.name in media_list:
					pass
				else:
					media_list.append(media.name)
					update = True
					break
			if not self.player.inMenus:
				if len(media_list) > 0:
					if update:
						str = ""
						for item in media_list:
							if str != "":
								str = item+", "+str
							else:
								str = item					
						self.player.plate.smessage(str.ljust(16),line=1)
						sleep(1)
				else:
					
					sleep(5)
			else:
				sleep(5)
			timeout+=1
					
	def on_start(self):		
		logger.info("[ALCD] Starting AdafruitLCD")
		self.player.start()
		self.startup.start()
			
	def on_stop(self):
		logger.info("[ALCD] Stopping AdafruitLCD")
		self.player.stop()	
		
	def track_playback_ended(self,tl_track, time_position):
		logger.info("[ALCD] track playback ended")
		self.player.track_playback_ended(tl_track.track)
		
	def track_playback_started(self,tl_track):		
		try:			
			logger.info("[ALCD] Now playing:")
			try:
				for artist in tl_track.track.artists:					
					logger.info("[ALCD]  >"+tl_track.track.name+ " by " +artist.name)
			except:
				traceback.print_exc()
			self.player.updateCurrentTrack(tl_track.track)
		except:
			traceback.print_exc()
		
	def playback_state_changed(self,old_state,new_state):		
		try:		
			#logger.info("[ALCD] Playback state changed from " + old_state + " to " + new_state)
			self.player.updatePlaybackState(old_state,new_state)
		except:
			traceback.print_exc()		
		
	def print_tracks(self,tl_track_list):
		for tltrack in tl_track_list:
			logger.info("[ALCD] " + tltrack.track.name)
			

"""			
	def playlists_loaded(self):
		logger.info("[ALCD] Playlists:")
		try:			
			for playlist in self.core.playlists.playlists.get():				
				if re.search("spotify:user:spotify",playlist.uri):					
					self.core.tracklist.add(tracks=playlist.tracks)
					self.core.playback.play()				
		except:
			traceback.print_exc()

		

		
	def tracklist_changed(self):
		logger.info("[ALCD] Tracklist updated")		
		print("  Total: "+str(len(self.core.tracklist.tl_tracks.get())))
		#self.print_tracks(self.core.tracklist.tl_tracks.get())
	
	def track_playback_ended(self,tl_track,time_position):
		logger.info("[ALCD]  Playback Ended")

"""
			
	
			
