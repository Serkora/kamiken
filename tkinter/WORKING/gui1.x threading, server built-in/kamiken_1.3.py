#!/Library/Frameworks/Python.framework/Versions/3.4/bin/python3.4
# -*- coding: utf-8 -*-
"""
Ver 1.3
	Multithreading
	Built-in server
	Board reset
	'Matplotlib plot grid' board
	Only Client and Server, no Launcher anymore
	Action validation
	Message receive confirmation
	Automatic scoring
	On-going scoreboard

Special commands:
	syshaltabortabort	— stops the server
	switchplayers 		— changes player number (will be useful when loading the game)
	skip 				— skips your turn
	save				— save the game


Things to do:
DONE1. Make proper action_validation function:
DONE	1.1 Check if the square already contains opponent's stone or has been hit by it
	2. Allow different gameplay settings (currently everything is hardcoded)
DONE3. Automatic score counting
DONE	3.1 and on-going scoreboard
DONE4. Restart only clears the board, board.turn stays the same — need fix (probably related
		to custom settings at startup)
	5. Improve widget placement and size to allow the main window to be properly resizable
DONE6. Integrate GameLauncher into GameClient — it's only 3 functions anyway.
	7. Update chat colouring to only search the beginning of the last added line
	8. Nicknames in chat, maybe?
	9. Extend Player class (currently only player number is used)
		possibly get rid of it, since everything happens on board anyway, and 
		player number can be kept in Client
DONE10. Add Board class
PART11. Add saves, skips
	12. Add reset_board prompt
	13. Improve startup — why have start, create_board and berehit?
	14. Rethink the placing/hitting/validating strategy (i.e. get rid of [1,2].remove(player))
	15. Possibly implement a dictionary for ishi placement storage
		—————————— Nah, lists work fine
DONE16. Turn indication
	17. Server storing last N messages

Bugs:
	1. Only manual restart works. Memory leak occurs if restart function is called when
		received restart message. Memory leaks at "self.fig=plt.figure(figsize=(5,3.2))".
		Same thing happened when self.draw_board() contained self.fig and was called 
		externally.	———————— Fixed by not reassigning self.fig to plt.figure, as fig.clf()
								only clears the figure and not closes it, so only 
								the field subplot needs to be added again
	2. Can't change client's listener ip address ——————— Don't event need to bind client's
														socket to any IP address ir port,
														it works as it is.
	3. "You've already placed a stone there" prints twice. ———— action_validation was simply
																called twice for if and elif
	4. Something's wrong with chat: 
		sometimes breaks down and a few lines at the bottom are kept below every new message
		—————— Happens when game window is not in focus and messages are being sent often:
				(UPDATE CHAT is printed at the beginning of update_chat function)
				(Proper sequence should be b'__CHAT__msg' -> ('ip',port) -> UDPATE CHAT)
						b'__CHAT__ad'
						('25.64.15.244', 59313)
						UPDATE CHAT
						b'__CHAT__f'
						('25.64.15.244', 59313)
						b'__CHAT__a'
						('25.64.15.244', 59313)
						b'__CHAT__d'
						('25.64.15.244', 59313)
						b'__CHAT__f'
						('25.64.15.244', 59313)
						b'__CHAT__a'
						('25.64.15.244', 59313)
						UPDATE CHAT
						UPDATE CHAT
						UPDATE CHAT
						UPDATE CHAT
						UPDATE CHAT
			Probably happens only when I start two clients on the same computer and 
			it lags a bit, just like confirmation sometimes is not received
"""


import os
import sys
import time
from threading import Thread
from threading import active_count

import re
import string
import pickle
import socket
import select
import random

import tkinter as Tk
import tkinter.scrolledtext
from tkinter import font

import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from numpy import arange, sin, pi
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.backend_bases import key_press_handler # implement the default mpl key bindings
from matplotlib.figure import Figure

#    import tkinter.tkSimpleDialog
#import tkinter as tkinter
#from tkinter import *


		#### Constants ####
#serverip='127.0.0.1'
serverip="25.64.15.244"
#serverip="25.65.255.143"
myip='127.0.0.1'
#myip="25.64.15.244"
enc='UTF-8'

#global listenerip
listenerip="25.64.15.244"
#listenerip="127.0.0.1"

alphabetU = string.ascii_uppercase
alphabetL = string.ascii_lowercase

class Board(object):
	def __init__(self):
		self.size=8
		self.komi=0.5
		self.turndef=1
		self.turn=1
		self.mode='normal'	# NOT IN USE YET
		self.turnorder='bw'	# order of turns. 'bw' - black goes first, 'wb' - white. NOT IN USE YET
			# score, placed ishi and hit squares storage
		self.score=[0,0]
		self.ishiA=[]
		self.ishiB=[]
		self.hitsA=[[99,99]]
		self.hitsB=[[99,99]]
		
	def validate(self,ishi,player):
		x=int(string.ascii_lowercase.index((ishi[0].lower())))+0.5
		y=int(ishi[1:])-0.5
		ishi=[[x,y],[x+1,y],[x-1,y],[x,y+1],[x,y-1]]
		if player==1:
			if ishi[0] in self.ishiA:
				client.update_text("You've already placed a stone there!")
				return False
			elif not any(ishi[i] in self.ishiB for i in range(0,5)):
				return True
			else:
				return False
		elif player==2:
			if ishi[0] in self.ishiB:
				client.update_text("You've already placed a stone there!")
				return False
			elif not any(ishi[i] in self.ishiA for i in range(0,5)):
				return True
			else:
				return False
				
	def store_ishi(self,x,y,player):
		if player==1:
			self.ishiA.append([x,y])
		elif player==2:
			self.ishiB.append([x,y])				
			
	def store_hits(self,hx,hy,player):
		if player==1:								# since hx and hy are lists,
			for i in range(0,len(hx)):			# and this will probably be then used
				self.hitsA.append([hx[i],hy[i]]) 	# used to plot, after loading game,
		elif player==2:								# for example, each [x,y] is appended 
			for i in range(0,len(hx)):			# separately to have two lists
				self.hitsB.append([hx[i],hy[i]])	# one for each player
				
	def make_hits(self,x,y,player):
			# create 4 markers around stone
		hx=[x,x,x+1,x-1]
		hy=[y+1,y-1,y,y]
			# store their coordinates
		self.store_hits(hx,hy,player)
			# adjust the position for plotting
		if player==1:
			hy=list(np.array(hy)-0.1)
		elif player==2:
			hy=list(np.array(hy)+0.1)	
		return hx, hy
	
	def count_score(self):
		
		indA=[self.hitsA[i] not in self.ishiA for i in range(0,len(self.hitsA))]
		htA=[self.hitsA[i] for i in [index for index,value in enumerate(indA) if value]]
		htA=np.array(htA)
		a=htA[:,0]>0
		b=htA[:,0]<=self.size
		c=htA[:,1]>0
		d=htA[:,1]<=self.size		
		htA=htA[a&b&c&d]
		htAu=unique_rows(htA)

		indB=[self.hitsB[i] not in self.ishiB for i in range(0,len(self.hitsB))]
		htB=[self.hitsB[i] for i in [index for index,value in enumerate(indB) if value]]
		htB=np.array(htB)
		a=htB[:,0]>0
		b=htB[:,0]<=self.size
		c=htB[:,1]>0
		d=htB[:,1]<=self.size			
		htB=htB[a&b&c&d]
		htBu=unique_rows(htB)

		comb=np.vstack((htAu,htBu))
		combu=unique_rows(comb)
		both=len(comb)-len(combu)
		Ascore=len(htAu)-both
		Bscore=len(htBu)-both
		self.score=[Ascore,Bscore]
#		if self.turndef==1:
#			self.score=[Ascore,float(Bscore)+self.komi]
#		elif self.turndef==2:
#			self.score=[float(Ascore)+self.komi,Bscore]

class Player(object):
	def __init__(self):
		self.player=0
		self.moves=[]
		self.score=0
	
	def move(self,move):
		self.moves.append(move)	

class GameServer(object):

	def __init__(self, listenerip, port=9009):
		self.listener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.listenerip = client.listenerip
		print(self.listenerip)
		self.listener.bind((self.listenerip,port))
		self.read_list = [self.listener]
		self.write_list=[]
		self.players=0			# number of connected players
		self.pladdr=[]			# players IPs to distinguish between players 1 and 2
		self.settings="not set"	# to make sure all the settings are set
#		self.modes={"normal" : "Normal mode",
#					"blind" : "You won't see the field until the end of the game",
#					"hardcore" : "You won't even know the score or your opponents moves"} '
	
	def send(self,items,player,type,pcklobj=False):
		
		player=str(player)
		
		print("Server is trying to send")
		print('"',items,'"')
		print("To player(s) ",player)
		
		if not pcklobj and type!="pickle" and type!="pckl" and type!="obj" and type!="object":
			type="__"+type[0:4].upper()+"__"
		else:
			pcklobj=True
		
		if '1' in player:
			if isinstance(items,tuple):			
				for item in items:
					self.listener.sendto((type+str(item)).encode(enc),self.pladdr[0])
			elif pcklobj:
				self.listener.sendto(pickle.dumps(items),self.pladdr[0])
			elif type=="__TEST__":
				self.listener.sendto(str(items).encode(enc),self.pladdr[0])
			else:
				self.listener.sendto((type+str(items)).encode(enc),self.pladdr[0])
	
		if '2' in player:
			if isinstance(items,tuple):			
				for item in items:
					self.listener.sendto((type+str(item)).encode(enc),self.pladdr[1])
			elif pcklobj:
				self.listener.sendto(pickle.dumps(items),self.pladdr[1])		
			else:
				self.listener.sendto((type+str(items)).encode(enc),self.pladdr[1])
		print("-----------")

	def receive(self,size=128,source='',address='yes',dtype='yes'):

		readable, writable, exceptional = (select.select(self.read_list, self.write_list,[]))
		msg,addr=readable[0].recvfrom(size)
		print("Server received")
		print(msg)
		print("From ",addr)
		if address=='no' or dtype=='no' or dtype=="pickle":
				return msg
		else:
			if msg.decode(enc)[8:]=="syshaltabortabortabort":
				self.send('serverstoppedserver',(list(range(1,self.players+1))),'settings')
				self.listener.close()
				sys.exit("exiting")
			else:
				return msg[8:].decode(enc), addr, self.action_classifier(msg.decode(enc))
		print("-----------")

	def action_classifier(self,msg):
		if re.search('^__MOVE__',msg):
			return "movement"
		if re.search('^__INFO__',msg):
			return "info"
		if re.search('^__SETT__',msg):
			return "settings"
		if re.search('^__CHAT__',msg):
			return "chat"	
		if re.search('__CONF__',msg):
			return 'confirmation'
		
	def start(self):
		n=0
		conplrs="not enough"
		print("Waiting for connections.")
		try:
			while conplrs!="enough":
				msg,addr,dtype=self.receive()		# get message from a connected player
				print(msg)
				if msg=="c" or msg=="y":
					self.pladdr.append(addr)		# add his IP to the list
					if self.players==0:
						print("Player 1 connected!")
						self.send("p1",1,"settings") 				# send player marker
						self.send("Successfully connected.",1,"info")
						self.send("Waiting for other players",1,"info")
						self.send("You are player 1 - white.",1,"info")
						self.players+=1					# add a player
					elif self.players==1: #and addr not in self.pladdr:
						print("Player 2 connected!")
						self.send("p2",2,"settings")
						self.send("Successfully connected",2,"info")
						self.send("Game will now start",2,"info")
						self.send("You are player 2 - black",2,"info")
						self.send("ready",1,"settings")
						self.send("Two players present. Do you want " \
									"to wait for more or start the game?",1,"info")
						self.send("Wait for P1 to set up the game", 2,'info')
						self.players+=1					# increment number of connected players
				print("twotwo")
				if msg=="start" and addr==self.pladdr[0] and self.players==2:		
														# if P1 sends confirmation to start
					self.send("ready",(1,2),'settings')	
					print("sdsf")									# start the game
					conplrs="enough"										
			
			print("Time to configure the game!")

			self.send("Choose the board size, komi and game mode, "\
						"or load previous save",1,'info')		# tell P1 to make a choice
#			self.send("creation",1,'settings')
			self.send("Wait for P1 to set up the game", 2,'info') # tell P2 to wait

			
			self.settings="set"
			while self.settings!="set":						# while not all settings have been chosen
				msg,addr,dtype=self.receive(address='yes')	# get message
				if addr==self.pladdr[0]:					# if it came from player 1
						if msg=="load":						
							pass						#
						elif n==0:						# set the parameters
							board=msg or "10"			#
						elif n==1:
							komi=msg or "0.5"
						elif n==2:
							mode=msg or "normal"
							self.settings="set"
							self.send("ready",2,'settings')
							turn=0
						n+=1


					### send set parameters to both players
			board=8
			komi=0.5
			mode='normal'
			turn=goban.turn
			self.send((('board'+str(board)),('komi'+str(komi)),\
						'mode'+mode,'turn'+str(turn)), (1,2),'settings')
			self.send("gogo",(1,2),"settings")
																
			return turn	# only turn value is need on the server side to keep track of who's turn it is
			
		except KeyboardInterrupt as e:
			print("Shutting down")

	def running(self,turn):
		game="running"
		
		try:		
			while game=="running":
				msg,addr,dtype=self.receive()
				recind=self.pladdr.index(addr)+1
# 				self.send('servreceived',recind)
				sndind=list(range(1,self.players+1))
				sndind.remove(recind)
				if dtype=="chat":
					self.send(msg,sndind,'chat')
				if dtype=="movement":
					self.send(msg,sndind,'move')
				if dtype=="settings":
					self.send("serv"+msg,list(range(1,self.players+1)),'settings')
				if dtype=='confirmation':
					self.send(msg,sndind,'confirmation')
#				if dtype=='confirmation request':
#					self.send(msg,sndind,'

		except KeyboardInterrupt as e:
			print("Shutting down")

class GameClient(object):

		#### Essential ####
	def __init__(self, master):
				# main window initialisation
		self.root=master
		self.root.wm_title("Kamiken")
		self.root.geometry('{}x{}'.format(1100,300))
		self.root.configure(background='white')
		self.create_base_elements()						# build base GUI elements
		self.hasserver='no'								# whether the server was started
		self.connected='no'								# if connected to a server		
				# networking stuff
		self.myip = myip
		self.clientport = random.randrange(8000, 8999)
		self.serverip = serverip
		self.serverport = 9009
		self.listenerip = listenerip
		self.conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		if sys.platform=='win32':
			self.conn.bind('25.96.141.197',8550)
				# network listener
		global ThrListen								# make it global to force-stop
		ThrListen=Thread(target=self.nw_listen,args=())	# create a network listener thread
		ThrListen.setDaemon(True)
		ThrListen.start()
				# Gameplay default values and board/player init
		global goban
		global character
		goban=Board()
		character=Player()
		self.gamestate=''
		self.mode='normal'

	def _quit(self):			
		self.root.quit()    # stop mainloop
		self.root.destroy()	# destroy window just in case	
				
	def nw_listen(self):						# network listener
		while True:								# infinite loop
			msg=self.receive()				# waits for message
			self.message_classifier(msg)		# sends the message to classifier
			
	def nw_confirmation(self):
		n=0
		self.confirmed=False
#		self.send('confirmpls','conr')
		while self.confirmed!=True:
			time.sleep(0.05)
			n+=1
			if n==20:
				return False
		if self.confirmed==True:
			return True
						
	def message_classifier(self,msg):

			# determine the type of data received based in it's prefix
		if re.search('^__MOVE__',msg):
			player=goban.turn
#			player.remove(character.player)
#			player=int(player[0])
			if self.action_validation(msg[8:],player):
				self.send('move received','confirmation')
				self.make_move(msg[8:],player)
		if re.search('^__INFO__',msg):
			self.update_text(msg[8:])
		if re.search('^__SETT__',msg):
			print("got some settings")
			self.settings(msg[8:])	
		if re.search('^__CHAT__',msg):
			self.update_chat(msg[8:],'stranger')
		if re.search('^__CONF__',msg):
			self.confirmed=True
		
	def create_base_elements(self):					# creates all base GUI elements
					# main figure and canvas
		self.fig=plt.figure(figsize=(5,3.2))
		self.canvas = FigureCanvasTkAgg(self.fig, master = self.root)
	
					# main text field
		self.text=Tk.scrolledtext.ScrolledText(master=self.root,height=8,width=40)
		self.text.place(relx=0.3, rely=0.9, anchor="se")
#		self.text.bind('<1>',self.undisable_text)
		self.text.insert(Tk.INSERT, "POEHALEE?\n")
		self.text.configure(state="disabled")

					#main entry
		self.MainInput = Tk.StringVar()
		self.MainEntry = Tk.Entry(master=self.root, textvariable=self.MainInput)
		self.MainEntry.place(relx=0.12,rely=0.41,anchor="c")
		self.MainEntry.bind("<Return>",self.on_key_event_MainEntry)	

					# chat		
		self.Chat=Tk.scrolledtext.ScrolledText(master=self.root,height=15,width=45)
		self.Chat.place(relx=1, rely=0.78, anchor='se')
		self.Chat.tag_configure("red",foreground="red")
		self.Chat.tag_configure("blue",foreground='blue')
		self.Chat.configure(state='disabled')
		self.ChatInput=Tk.StringVar()
		self.ChatEntry=Tk.Entry(master=self.root,textvariable=self.ChatInput,width=34)
		self.ChatEntry.place(relx=0.82,rely=0.9,anchor='s')
		self.ChatEntry.bind('<Return>',self.on_key_event_ChatEntry)
		self.ChatClear = Tk.Button(master=self.root, text="clear",width='3', 
									command=self.clear_chat)
		self.ChatClear.place(relx=1, rely=0.9, anchor='se')
	
					# Scoreboard and turn indicator
		self.turnindicator = Tk.Text(master=self.root, height=1,width='25')
		self.turnindicator.configure(background='black')
		self.turnindicator.bind("<Enter>",lambda x:self.update_turnind('score'))	
		self.turnindicator.bind("<Leave>",self.update_turnind)	
	
					#buttons
		self.button_quit = Tk.Button(master=self.root, text='Quit', 
									width='10', command=self._quit)
		self.button_quit.place(relx=.17, rely=.2, anchor='c')
		self.button_start = Tk.Button(master=self.root, text='Join game', 
									width='10', command=self.start)
		self.button_start.place(relx=.06, rely=.1, anchor='c')	
		self.button_settings = Tk.Button(master=self.root, text='Settings', 
									width='10', command=self.settings_menu)
		self.button_settings.place(relx=.06, rely=.2, anchor='c')
		self.button_server = Tk.Button(master=self.root, text='Start server', 
									width='10', command=self.start_server)
		self.button_server.place(relx=.17, rely=.1, anchor='c')
		self.button_server.bind('<Enter>',self.servertimedbutton)	# calls function to
		self.button_server.bind('<Leave>',self.servertimedbutton)	# wait 1 sec and change
		self.sercurs=['','']				# state/text if mouse is still over the button
		self.button_testing = Tk.Button(master=self.root, text='Test button',
									width='10', command=self.test_fun)
		self.button_testing.place(relx=0.12, rely=0.3, anchor='c')

	def settings(self,setting):
		if setting=="servserverstoppedserver":
			if self.hasserver=='no':
				self.update_text("Server was shut down")
			if client.connected=='yes':
				self.disconnect()
		elif setting=='servinitrestart':
			self.reset_board('finrestart')
		elif len(setting)==2 and setting[0]=="p":
			character.player=int(setting[1])
		elif re.search('^board',setting):
			goban.size=int(setting[5:])
		elif re.search('^komi',setting):
			goban.komi=int(setting[4])
		elif re.search('^mode',setting):
			goban.mode=setting[4:]
		elif re.search('turn',setting):
			goban.turn=int(setting[4:])
		elif re.search('ready',setting):
			self.update_text(setting[3:])
			self.button_start.configure(state='normal')
		elif re.search('creation',setting):
			#client.board_creation()
			pass
		elif re.search("gogo",setting):
			self.gamestate="playing"
			self.berehit()
		if setting=="servskip":
			goban.turn=goban.turn*2%3
			client.update_turnind()
		if setting=="servswitchplayers":
			character.player=character.player*2%3
		if setting=="servstop":
			self.gamestate="stopped"
			self.update_text('THE GAME HAS ENDED!')
			if goban.score[0]>goban.score[1]:
				if character.player==1:
					self.update_text("You've won the game!")
				else:
					self.update_text("You've lost the game!")
			else:
				if character.player==2:
					self.update_text("You've won the game!")
				else:
					self.update_text("You've lost the game!")

			self.update_turnind()
		
	def settings_menu(self):
				# save all changed settings
		def save_settings():
			self.serverip = self.servip_var.get()
			self.listenerip = self.listenip_var.get()
			self.window_settings.destroy()
				# create window
		self.window_settings = Tk.Toplevel()
		self.window_settings.geometry('{}x{}'.format(300,120))
		self.window_settings.resizable(0,0)
				# create buttons
		self.button_close = Tk.Button(master=self.window_settings, 
									command=lambda:self.window_settings.destroy(), 
									text="Close", width='10')
		self.button_close.place(relx=.75, rely=.85, anchor='c')
		self.button_save = Tk.Button(master=self.window_settings, command = save_settings,
									text="Save and close", width='15', height='100',state='disabled')
		self.button_save.place(relx=.3, rely=.85, anchor='c')
				# create input fields
		self.servip_var = Tk.StringVar()
		self.servip_var.set(self.serverip)
		self.servip_inp = Tk.Entry(master=self.window_settings, 	# entry with server ip
									textvariable=self.servip_var, width='15')
		self.servip_inp.place(relx=.5, rely=.15, anchor='nw')
		self.servip_inp.bind('<KeyRelease>',self.on_key_event_Settings)	# invoke settings
																	# event on key release
		self.listenip_var = Tk.StringVar()					# entry with listener ip
		self.listenip_var.set(self.listenerip)		
		self.listenip_inp = Tk.Entry(master=self.window_settings, 
									textvariable=self.listenip_var, width='15')
		self.listenip_inp.place(relx=.5, rely=.36, anchor='nw')
		self.listenip_inp.bind('<KeyRelease>',self.on_key_event_Settings)	
				# add text description
		self.servip_txt = Tk.Text(master=self.window_settings, height='1', width='9')
		self.servip_txt.place(relx=.2, rely=.15, anchor='nw')
		self.servip_txt.insert(Tk.INSERT,"Server IP")	# server ip input field description
		self.servip_txt.configure(state='disabled')	
		self.servip_txt = Tk.Text(master=self.window_settings, height='1', width='11')
		self.servip_txt.place(relx=.2, rely=.36, anchor='nw')
		self.servip_txt.insert(Tk.INSERT,"Listener IP")	# listener ip input field description
		self.servip_txt.configure(state='disabled')
			
	def draw_board(self,board):		
					# field subplot and canvas placement
		self.field=self.fig.add_subplot(111)
		self.canvas.get_tk_widget().place(relx=.68,rely=.5,anchor="e") # place it
		self.canvas.get_tk_widget().pack(expand='yes',fill='y')
					# main plot axes, ticks, range, etc, etc.
		xtcks=list(np.array(range(0,board))+0.5)
		ytcks=list(np.array(range(0,board+1))-0.5)
		self.plot=plt
		self.plot.grid(b=True)
		self.plot.xlim(0,board)
		self.plot.ylim(0,board)
		self.plot.yticks(range(0,board))
		self.plot.xticks(np.array(range(0,board)),alphabetU)
		self.field.set_xticklabels([])
		self.field.set_yticklabels([])
		self.field.xaxis.set_minor_locator(plt.FixedLocator(xtcks))
		self.field.xaxis.set_minor_formatter(plt.FixedFormatter(alphabetU))
		self.field.yaxis.set_minor_locator(plt.FixedLocator(ytcks))
		self.field.yaxis.set_minor_formatter(plt.FixedFormatter(range(0,board+1)))
		self.plot.tick_params(axis="x",which="minor",bottom="on",top="on")
		self.canvas.show()

	def start_server(self):
		global ThrServer				# make it global to force-stop
		ThrServer=Thread(target=Run_Server,args=())
		ThrServer.setDaemon(True)		# make daemon stop when client closes
		ThrServer.start()				# run server thread
		self.hasserver='yes'
		self.button_server.configure(text="Running...",state="disabled",command=self.dummy)

	def stop_server(self):
		if 'ThrServer' in globals():
			ThrServer._tstate_lock=None
			ThrServer._stop()
			self.send('syshaltabortabortabort','settings')
			self.disconnect()
			self.hasserver='no'
			self.update_text("Server was shut down")
			self.button_server.configure(text='Start server', state='normal',
										command=self.start_server)
		else:
			print("not running")

	def disconnect(self):
		self.button_server.config(command=self.start_server, text='Start server',
									state='normal')
		self.button_start.config(command=self.start, text='Join game', 
									state='normal')
		self.connected='no'
		character.player=0
		self.reset_board('finrestart')

	def dummy(self):
		pass

	def test_fun(self):
		"""
		self.gamestate='playing'
		character.player=1
		goban.turn=1
		goban.size=8
		self.turnindicator.pack(side=Tk.TOP)
		self.draw_board(goban.size)
		"""
		pass

		#### ex-Launcher ####
	def send(self,items,dtype,pcklobj=False,destination='server'):
		print("Client is trying to send")
		print('"',items,'"')
		if destination=='server':
			dest=(self.serverip,self.serverport)
		else:
			dest=destination
		
		if not pcklobj and dtype!="pickle" and dtype!="pckl" \
						and dtype!="obj" and dtype!="object":
			dtype="__"+dtype[0:4].upper()+"__"
		else:
			pcklobj=True
		
		if not pcklobj:
			self.conn.sendto((dtype+str(items)).encode(enc),dest)
		else:
			self.conn.sendto(pickel.dumps(items),dest)
		print("-----------")
	
	def receive(self,source='server',size=128,notstring=False):
		msg,addr=self.conn.recvfrom(size)
		print("Client received")
		print(msg)
		try:
			return msg.decode(enc)
		except:
			return msg
		print("-----------")

		#### Figure and text field updates ####
	def refresh_figure(self,x,y,hx,hy,player):
		if player==1:
			colour=['grey','red']		# sets the colours depending
			x=np.array(goban.ishiA)[:,0]
			y=np.array(goban.ishiA)[:,1]
		elif player==2:					# on who is placing the stone
			colour=['black','blue']
			x=np.array(goban.ishiB)[:,0]
			y=np.array(goban.ishiB)[:,1]
		else:
			return
		plt.scatter(hx,hy,c=colour[1],s=50)			# place hits
		plt.scatter(x,y,c=colour[0],s=300)			# place stone
		self.canvas.show()							# show updated board
		goban.turn=goban.turn*2%3					# change turn
		goban.count_score()							# update the score
		self.update_turnind()						# update indicator
		
	def update_text(self,msg):
		self.text.configure(state="normal")
		self.text.insert(Tk.END,str(msg)+'\n')	# pretty much self-explanatory
		self.text.configure(state="disabled")
		self.text.see('end')					# scrolls to the last character

	def update_chat(self,text,who):
		print("UPDATE CHAT")
		self.Chat.configure(state="normal")
		if who=="you":
			self.Chat.insert(Tk.INSERT,"YOU: "+text+"\n")
		elif who=="stranger":
			self.Chat.insert(Tk.INSERT,"STRANGER: "+text+"\n")
		self.highlight_chat("YOU: ",'red')
		self.highlight_chat("STRANGER: ",'blue')
		self.Chat.see('end')					# scroll to the bottom
		self.Chat.configure(state="disabled") # NEEDS REWRITING AND COMMENTS

	def clear_chat(self):
		self.Chat.configure(state="normal")
		self.Chat.delete(1.0,Tk.END)
		self.Chat.configure(state="disabled")
	
	def update_turnind(self,type='turn'):
		self.turnindicator.configure(state='normal')
		if type=='score' or self.gamestate=="stopped":
			self.turnindicator.delete("1.0",Tk.END)
			self.turnindicator.configure(foreground="red")
			self.turnindicator.insert("1.0","White:"+str(goban.score[0])+"    Black:"+str(goban.score[1])+".5")
		elif goban.turn==character.player:
			self.turnindicator.delete("1.0",Tk.END)
			self.turnindicator.configure(foreground="red")
			self.turnindicator.insert("1.0","Your turn!\n")
		else:
			self.turnindicator.delete("1.0",Tk.END)
			self.turnindicator.configure(foreground="blue")
			self.turnindicator.insert("1.0","Waiting for opponent...\n")			
		self.turnindicator.configure(state='disabled')
	
		#### On key events ####
	def on_key_event_MainEntry(self,event):
		s=self.MainInput.get()					# get whatever what in the field
		self.MainInput.set('')					# empty the field
		if self.gamestate!="playing" or len(s)>3:
			if s!="skip":
				self.send(s,'settings')				# sends commands as settings
			if s=="skip" and goban.turn==character.player:
				self.update_text('Skipped! But why?..')
				self.send(s,'settings')
			else:
				self.update_text("Not your turn!")
		elif self.gamestate=="playing" and goban.turn==character.player:
			if self.action_validation(s,character.player):
				self.send(s,"move")							# send your move
				if self.nw_confirmation():					# check if other player received
					self.make_move(s,character.player)		# if your turn, updates board.
				else:
					self.update_text("Connection problems. Try again")
			else:
				self.update_text("Not a valid move.")
		elif self.gamestate=="playing" and goban.turn!=character.player:
			self.update_text("Not your turn!")
		elif self.gamestate=="playing":
			self.update_text("Something went really wrong") # shouldn't get to this
			
	def on_key_event_ChatEntry(self,event):
		text=self.ChatInput.get()
		if text=='': return				# if nothing was written, don't update/send
		self.ChatInput.set('')
		self.update_chat(text,'you')
		self.send(text,'chat')

	def on_key_event_Settings(self,event):
		if self.servip_var.get()!=self.serverip or self.listenip_var.get()!=self.listenerip:
			self.button_save.configure(state='normal')
		if self.servip_var.get()==self.serverip and self.listenip_var.get()==self.listenerip:
			self.button_save.configure(state='disabled')

		#### Gameplay-related functions ####
	def board_creation(self):
		settings="not set"
		n=0
		self.update_text("Enter board size")
		s=self.MainInput.get()
		self.MainInput.set('')
		print("got to here")
		while settings!="set":
			s=self.MainInput.get()
			self.MainInput.set('')
			if n==0:
				if not isinstance(s,int):
					self.update_text("Not a valid board size, must be int")
				else:
					launcher.send(s,"settings")
				n+=1
			if n==1:
				self.update_text("choose komi value")
				if not isinstance(s,int) or not isinstance(s,float):
					self.update_text("Not a valid komi value, must be int or float")
				else:
					launcher.send(s,"settings")
				n+=1
			if n==2:
				self.update_text("Choose game mode")
				launcher.send(s,"settings")
				settings="set"	# NOT WORKING, NOT BEING USED, NEEDS REWRITING
					
	def action_validation(self,action,player):
		if len(action)<=3 and action[0] in string.ascii_letters:
			try:						# if the first value is in alphabet,
				int(action[1:])			# check if the rest are integers,
				if (string.ascii_lowercase.index(action[0].lower())>=goban.size or \
														int(action[1:])>goban.size):
					self.update_text("Trying to play outside the board, eh?")
					return False									
				if goban.validate(action,player):	# and if the move is not prohibited by
					return True						# the rules of the game
				else:
					return False
			except:
				return False
	
	def make_move(self,move,player):
		x=float(string.ascii_lowercase.index(move[0].lower()))+0.5	# get index of the letter
		y=float(move[1:])-0.5										# with A/a being 0.
		goban.store_ishi(x,y,player)								# store placed ishi
		hx,hy=goban.make_hits(x,y,player)							# make 4 hits around ishi
		self.refresh_figure(x,y,hx,hy,player)						# and refresh board
			
		#### Other supporting functions ####
	def highlight_chat(self, pattern, tag, start="1.0", end="end", regexp=False):
		'''
		Apply the given tag to all text that matches the given pattern

		If 'regexp' is set to True, pattern will be treated as a regular expression
		'''
		start = self.Chat.index(start)
		end = self.Chat.index(end)
		self.Chat.mark_set("matchStart",start)
		self.Chat.mark_set("matchEnd",start)
		self.Chat.mark_set("searchLimit", end)

		count = Tk.IntVar()
		while True:
			index = self.Chat.search(pattern, "matchEnd","searchLimit",
                                count=count, regexp=regexp)
			if index == "": break
			self.Chat.mark_set("matchStart", index)
			self.Chat.mark_set("matchEnd", "%s+%sc" % (index,count.get()))	
			self.Chat.tag_add(tag, "matchStart","matchEnd") # NEEDS FIXING TO SEARCH LAST LINE ONLY
			
	def start(self):
		self.send("c","settings")
		rec=False
		num=0
		while rec==False: # infinite loop until player.num received or 2 seconds have passed
			if character.player==1:
				self.button_start.configure(command=self.create_board,
											text='Create Board', state="disabled")
				rec=True
			elif character.player>1:		
				self.button_start.configure(command=self.dummy, text='Waiting...',
											state="disabled")
				self.button_server.config(command=self.dummy, text='Connected',
											state='disabled')
				rec=True
			if self.hasserver=='no':
				self.connected='yes'
			if num==20:
				self.update_text("Couldn't connect to the server or no response")
				return
			num+=1
			time.sleep(0.1)
	
	def create_board(self):
		self.send("start","settings")
		self.button_start.configure(command=self.berehit,state="disabled")
	
	def berehit(self):
		self.turnindicator.pack(side=Tk.TOP)
		self.draw_board(goban.size)
		self.update_turnind()
		self.button_start.configure(text="Restart",command=lambda:self.reset_board('initrestart'))
			
	def reset_board(self,var):
		if var=="initrestart":
			self.send("initrestart",'settings')
		elif var=='finrestart':
			self.fig.clf(keep_observers=False)
			self.draw_board(goban.size)
		goban.hitsA,goban.hitsB,goban.ishiA,goban.ishiB=[[99,99]],[[99,99]],[],[]
		goban.turn=goban.turndef
		self.update_turnind()
		'''
		if var=='initrestart':
			launcher.send('finrestart','settings')
			self.restart('finrestart')
		
		elif var=='initrestart2':						# initialise restart
			launcher.send('initrestart','settings')		# send the message to server
			self.window_restart = Tk.Toplevel()			# and wait fot other player 
			self.window_restart.geometry('{}x{}'.format(400,50))	# to accept
			self.window_restart.resizable(0,0)
			self.rsttxt=Tk.Text(master=self.window_restart, height='2',width='50')
			self.rsttxt.pack(expand='yes', fill='both')
			self.rsttxt.insert(Tk.INSERT,"Waiting for other player to accept the restart")
		elif var=='receivedrestart':					# if got the message about restart
			self.window_restart = Tk.Toplevel()			# pop-up to accept/decline
			self.window_restart.geometry('{}x{}'.format(100,100))
			self.window_restart.resizable(0,0)
			self.rsttxt=Tk.Text(master=self.window_restart, height='2',width='50')
			self.rsttxt.insert(Tk.INSERT,"Do you want to restart the game?")
			self.rstbutton = Tk.Button(master=self.window_restart, 
									command=lambda:launcher.send('acceptrestart','settings'))
			self.rstbutton.place(relx=.5, rely=.7, anchor='c')
		elif var=='finrestart':							# when accepted
			pass
			self.fig.clf()								# close figure
			print('1')
			self.canvas.get_tk_widget().pack_forget()	# remove canvas for the new one
			print('2')
			self.fig=plt.figure(figsize=(5,3.2))
			print('3')
#			self.field=self.fig.add_subplot(111)
#			self.canvas = FigureCanvasTkAgg(self.fig, master = self.root)
#			self.draw_board(launcher.board)				# redraw the board
#			self.window_restart.destroy()				# close message window
		'''

	def servertimedbutton(self,event):
		""" 
		Called either by an event or from inside itself. If event was "mouse over",
		it is called again in 1 second with argument "change". If the cursor 
		haven't left the button by that time, button is changed to either "Stop server"
		for player running the server, or "Disconnect" for everyone else.
		At every "mouse leave" event the button is (mostly redundantly) changed
		back to "Running..." if the server was started by that player, or "Connected"
		for all other players.
		"""
		if event=='change' and self.sercurs[0]!='restart':
			if self.sercurs[1]=='over' and self.hasserver=='yes':
				self.button_server.configure(state='normal',text='Stop server',command=self.stop_server)
			elif self.sercurs[1]=='over' and self.hasserver=='no' and self.connected=='yes':
				self.button_server.configure(state='normal',text='Disconnect',command=self.disconnect)
		elif event=='dontchange':
			if self.hasserver=='yes':
				self.button_server.configure(state='disabled',text='Running...',command=self.dummy)		
			elif self.hasserver=='no' and self.connected=='yes':
				self.button_server.configure(state='disabled',text='Connected',command=self.dummy)
		elif not isinstance(event,str) and event.type=='7':
			self.sercurs=['','over']
			self.root.after(1000,lambda:self.servertimedbutton('change'))
		elif not isinstance(event,str) and event.type=='8':
			self.sercurs=['restart','left']
			self.servertimedbutton('dontchange')

def Run_Server():
	print("started server")
	global listenerip
	global server
	server=GameServer(listenerip)
	turn=server.start()
	server.running(turn)

def unique_rows(data):
    uniq = np.unique(data.view(data.dtype.descr * data.shape[1]))
    return uniq.view(data.dtype).reshape(-1, data.shape[1])

def unique_cols(data):
    uniq = np.unique(data.view(data.dtype.descr * data.shape[0]))
    return uniq.view(data.dtype).reshape(-1, data.shape[0]) 

def main():
	global client
	client=GameClient(Tk.Tk())
	Tk.mainloop()
	
#if __name__=="__main__":
#	main()
main()