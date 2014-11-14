from mopidy.models import Playlist
import Adafruit_CharLCD as LCD
from netifaces import interfaces, ifaddresses, AF_INET
from time import sleep
import logging
import re
import pickle
logger = logging.getLogger(__name__)


	


class menus():
	def __init__(self,core,player,plate):
		self.player=player
		self.core = core
		self.plate = plate 
		
	def cPlaylist(self,name="temp",tracks=[]):
		#new_playlist = self.core.playlists.create(name).get()
		#print(type(new_playlist))
		return Playlist(uri="local:playlist:"+name,tracks=tracks,name=name)
		
	def menu(self):
		self.player.inMenus = True
		list = ["Playlists","Browse Media","Settings"]
		while True:
			result,index = self.create_menu(list)
			if result:
				if index == -1:
					break
				elif index == 0:
					if self.menu_playlists():
						break
				elif index == 1:
					if self.menu_browse():
						break
				elif index == 2:
					if self.menu_settings():
						break
			else:
				self.player.displaySongInfo()
				break
		self.player.inMenus = False
		
	def menu_settings(self):
		def rjust_bool(bool,text):
			if bool:
				return (text+"ON".rjust(15-(len(text))))
			else:
				return (text+"OFF".rjust(15-(len(text))))
				
		list = ["","","Get IP Address"]

		while True:
			random = self.core.tracklist.random.get()
			repeat = self.core.tracklist.repeat.get()
			list[0] = rjust_bool(random,"Shuffle")
			list[1] = rjust_bool(repeat,"Repeat")			
			result,index = self.create_menu(list)
			if result:
				if index == -1:
					return
				elif index == 0:
					self.core.tracklist.random = not self.core.tracklist.random.get()
				elif index == 1:
					self.core.tracklist.repeat = not self.core.tracklist.repeat.get()
				elif index == 2:
					address=[]
					for ifaceName in interfaces():
						addresses = [i['addr'] for i in ifaddresses(ifaceName).setdefault(AF_INET, [{'addr':'No IP addr'}] )]
						address.append("".join(addresses))
					if self.create_menu(address):
						return True

			else:
				return
	def menu_playlists(self):		
		while True:
			playlist_list = self.core.playlists.playlists.get()			
			result,index = self.create_menu(self.get_menu_list(playlist_list))
			if result:
				if index == -1:
					return True
				else:
					#playlist selection
					if self.menu_playback(playlist_list[index]):
						return True
			else:
				return False

	def menu_playback(self,playlist):
		while True:
			if playlist.length>1:
				list = ["Play "+str(playlist.length)+" Tracks","Add "+str(playlist.length)+" Tracks","Save Playlist","Select Track"]
			elif playlist.length==1:
				list = ["Play "+playlist.tracks[0].name,"Add to Tracklist","Save Playlist"]
			else:
				logger.error("passed zero length playlist! impossibru!")
			result,index = self.create_menu(list)
			if result:
				if index == -1:
					return True
				elif index==0:				
					self.core.tracklist.clear()
					self.core.tracklist.add(tracks=playlist.tracks)
					self.core.playback.play()
					self.player.updateCurrentTrack(self.core.playback.current_tl_track.get().track,screenUpdate=False)			
					self.player.displaySongInfo(forceSymbol="\x04")
					return True
				elif index==1:
					self.core.tracklist.add(tracks=playlist.tracks)
					return True
				elif index==3:
					#TODO
					return True
				elif index==2:
					if self.core.playlists.save(playlist) == None:
						print("PLAYLIST NOT SAVED")
					else:
						print("Something was returned")
			else:
				return False
				
	def menu_browse(self,uri=None,forceTracklist=False,Name="Parent"):
		list = self.core.library.browse(uri).get()
		tracklist = []
		for media in list:
			if media.type == "track":
				tracklist.append(self.core.library.lookup(media.uri).get()[0])
		if len(tracklist)>0 and not forceTracklist:
			#have tracks in folder, create playlist to send to menu_playback()
			if re.match('tunein:',uri):
				return self.menu_browse(uri=uri,forceTracklist=True,Name=Name)
			else:
				return self.menu_playback(self.cPlaylist(name=Name, tracks=tracklist))
		else:
			while True:			
				result,index = self.create_menu(self.get_menu_list(list))
				if result:
					if index == -1:
						return True
					else:
						if list[index].type == "directory":
							if self.menu_browse(uri=list[index].uri,Name=list[index].name):
								return True
						if list[index].type == "track":
							if self.menu_playback(self.cPlaylist(name=Name, tracks=[self.core.library.lookup(list[index].uri).get()[0]])):
								return True
				else:
					return False
					
	def volume_change(self):
		vol_bar = "".ljust(16*self.core.playback.volume.get()/100,"\x05")
		self.plate.smessage(vol_bar,line=1)
		self.plate.smessage("Volume".center(16))
		while True:
			#self.plate.smessage(vol_bar,line=1)
			sleep(0.01)
			button = self.plate.waitForButton(timeout=5,release=False)
			if button == LCD.UP:
				if self.core.playback.volume.get() < 100:
					if 16*self.core.playback.volume.get()/100 != 16*(self.core.playback.volume.get()+10)/100:
						self.plate.smessage("\x05\x05",line=1,col=(16*(self.core.playback.volume.get())/100)-1)
					else:
						self.plate.smessage("\x05",line=1,col=(16*(self.core.playback.volume.get()+10)/100)-1)
					self.core.playback.volume = self.core.playback.volume.get()+10					
			elif button == LCD.DOWN:
				if self.core.playback.volume.get() > 0:
					if 16*self.core.playback.volume.get()/100 != 16*(self.core.playback.volume.get()-10)/100:
						self.plate.smessage("",line=1,col=(16*(self.core.playback.volume.get())/100)-1)
					self.core.playback.volume = self.core.playback.volume.get()-10
			else:
				self.plate.clear()
				self.player.displaySongInfo()
				break
				
	def create_menu(self,list,index=0,timeout=15,nil="nothing found"):
		#Returns:
		#  True,index: selection made (or timeout: index=-1)
		#  False,index: Go up a menu
		while True:
			if len(list) > index:
				self.plate.smessage('\x01'+list[index])
			else:
				self.plate.smessage(nil)
			if len(list) > index+1:
				self.plate.smessage(list[index+1],line=1)
			else:
				self.plate.smessage("",line=1)
			button = self.plate.waitForButton(timeout=timeout)
			if button == LCD.DOWN:
				if index < len(list)-1:
					index +=1
			elif button == LCD.UP:
				if index > 0:
					index -=1
			elif button == LCD.LEFT or button == LCD.RIGHT:
				self.plate.smessage('\x04',whitespace=False)
				return True,index
			elif button == LCD.SELECT:
				return False,index
			else:
				self.player.displaySongInfo()
				return True,-1 #Timeout

	def get_menu_list(self,list):
		retList = []
		for item in list:
			retList.append(item.name)
		return retList
