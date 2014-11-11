#!/usr/bin/env python

import logging
import traceback
import pykka
import mopidy
import sys
import re #todo: remove
from mopidy import core
from .Adafruit_player import AdafruitPlayer
logger = logging.getLogger(__name__)

class AdafruitLCD(pykka.ThreadingActor, core.CoreListener):
	def __init__(self,config,core):
		super(AdafruitLCD,self).__init__()
		self.core = core
		self.player = AdafruitPlayer(core)
		#self.player.run()
	
	def on_start(self):
		self.player.run()
		logger.info("[ALCD] Starting AdafruitLCD")				

			
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
			self.player.updateCurrentTrack(tl_track.track) #todo: call on any playback state and not just when playback starts.
		except:
			traceback.print_exc()
		
	def playback_state_changed(self,old_state,new_state):		
		try:		
			logger.info("[ALCD] Playback state changed from " + old_state + " to " + new_state)
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
			
	
			
