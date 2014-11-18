#!/Library/Frameworks/Python.framework/Versions/3.4/bin/python3.4
# -*- coding: utf-8 -*-
"""
Ver 1.1
	Multithreading
	Built-in server

Things to do:
	1. Make proper action_validation function:
		1.1 Accept "LetNum(Num)" moves
		1.2 Check if the square already contains opponent's stone or has been hit by it
	2. Subsequently, update refresh_fig function to properly draw graph form such moves
	3. Allow different gameplay settings (currently everything is hardcoded)
	4. Automatic score counting
	5. Restart the game without the need to restart the whole application
	8. Improve widget placement and size to allow the main window to be properly resizable
	6. Update chat colouring to only search the beginning of the last added line
	7. Nicknames in chat, maybe?

Bugs:
	1. Can't change client's listener ip address
	2. Something's wrong with chat: 
		sometimes breaks down and a few lines at the bottom are kept below every new message
		
"""


import os
import sys
import time
from threading import Thread

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
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.backend_bases import key_press_handler # implement the default mpl key bindings
from matplotlib.figure import Figure

#    import tkinter.tkSimpleDialog
#import tkinter as tkinter
#from tkinter import *


		#### Constants ####
serverip='127.0.0.1'
#serverip="25.65.255.143"
#serverip="25.64.15.244"
myip='127.0.0.1'
#myip="25.64.15.244"
enc='UTF-8'

#listnerip="25.64.15.244"
#global listenerip
listenerip="127.0.0.1"

alphabetU=list(string.ascii_uppercase)
alphabetL=list(string.ascii_lowercase)

class Player(object):
	def __init__(self,player=0):
		self.player=player
		self.moves=[]
		self.score=0
	
	def move(self,move):
		self.moves.append(move)	

class GameLauncher(object):
	def __init__(self, serverip=serverip, listenerip=listenerip, serverport=9009,myip=myip):
		self.myip = myip
		self.clientport = random.randrange(8000, 8999)
		self.serverip = serverip
		self.serverport = serverport
		self.listenerip = listenerip
		self.conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.conn.bind((self.myip,self.clientport))
		# Bind to localhost - set to external ip to connect from other computers
		self.conn.setblocking(1)
		self.read_list = [self.conn]
		self.write_list = []
		
		self.turn=''
		self.gamestate=''
		self.board=5
		self.turn=0
		self.komi=0.5
		self.mode='normal'
		
	def send(self,items,dtype,pcklobj=False,destination='server'):

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
	
	def receive(self,source='server',size=128,notstring=False):
		msg,addr=self.conn.recvfrom(size)
		try:
			return msg.decode(enc)
		except:
			return msg

	def settings(self,setting):
		if len(setting)==2 and setting[0]=="p":
			character.player=int(setting[1])
		elif re.search('^board',setting):
			self.board=int(setting[5:])
		elif re.search('^komi',setting):
			self.komi=int(setting[4])
		elif re.search('^mode',setting):
			self.mode=setting[4:]
		elif re.search('turn',setting):
			if int(setting[4:])%2 == character.player-1:
				self.turn="your"
			else:
				self.turn="opp"
		elif re.search('ready',setting):
			client.update_text(setting[3:])
			client.button_start.configure(state='normal')
		elif re.search('creation',setting):
			#client.board_creation()
			pass
		elif re.search("gogo",setting):
			launcher.gamestate="playing"
			client.berehit()
						
class GameServer(object):

	def __init__(self, listenerip, port=9009):
		self.listener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.listenerip = listenerip
		self.listener.bind((self.listenerip,port))
		self.read_list = [self.listener]
		self.write_list=[]
		self.players=0			# number of connected players
		self.pladdr=[]			# players IPs to distinguish between players 1 and 2
		self.settings="not set"	# to make sure all the settings are set
#		self.modes={"normal" : "Normal mode",
#					"blind" : "You won't see the field until the end of the game",
#					"hardcore" : "You won't even know the score or your opponents moves"} 
		
	def send(self,items,player,type,pcklobj=False):
	
		player=str(player)
		
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


	def receive(self,size=128,source='',address='yes',dtype='yes'):

		readable, writable, exceptional = (select.select(self.read_list, self.write_list,[]))
		msg,addr=readable[0].recvfrom(size)
		print(msg)
		if address=='no' or dtype=='no' or dtype=="pickle":
				return msg
		else:
			if msg.decode(enc)[8:]=="syshalt":
				sys.exit("exiting")
			else:
				return msg[8:].decode(enc), addr, self.action_classifier(msg.decode(enc))

	def action_classifier(self,msg):
		if re.search('^__MOVE__',msg):
			return "movement"
		if re.search('^__INFO__',msg):
			return "info"
		if re.search('^__SETT__',msg):
			return "settings"
		if re.search('^__CHAT__',msg):
			return "chat"	
		
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
					if self.players==1: #and addr not in self.pladdr:
						print("Player 2 connected!")
						self.send("p2",2,"settings")
						self.send("Successfully connected",2,"info")
						self.send("Game will now start",2,"info")
						self.send("You are player 2 - black",2,"info")
						self.send("ready",1,"settings")
						self.send("Two players present. Do you want \
									to wait for more or start the game?",1,"info")
						self.send("Wait for P1 to set up the game", 2,'info')
					self.players+=1					# increment number of connected players
				print("twotwo")
				if msg=="start" and addr==self.pladdr[0] and self.players==2:		
														# if P1 sends confirmation to start
					self.send("ready",(1,2),'settings')	
					print("sdsf")									# start the game
					conplrs="enough"										
			
			print("Time to configure the game!")

			self.send("Choose the board size, komi and game mode, \
						or load previous save",1,'info')		# tell P1 to make a choice
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
						n+=1		## NOT BEING USED

					### send set parameters to both players
			board=7
			komi=0.5
			mode='normal'
			turn=0
			self.send((('board'+str(board)),('komi'+str(komi)),\
						'mode'+mode,'turn'+str(turn)), (1,2),'settings')
			self.send("gogo",(1,2),"settings")
																
			return turn	# only turn value is need on the server side to keep track of who's turn it is
			
		except KeyboardInterrupt as e:
			print("Shutting down")


	def run(self,turn):
		game="running"
		
		try:		
			while game=="running":
				msg,addr,dtype=self.receive()
				recind=self.pladdr.index(addr)+1
				sndind=list(range(1,self.players+1))
				sndind.remove(recind)
				if dtype=="chat":
					self.send(msg,sndind,'chat')
				if dtype=="movement":
					self.send(msg,sndind,'move')
				if dtype=="settings":
					self.send(msg,sndind,'settings')

		except KeyboardInterrupt as e:
			print("Shutting down")

class GameClient(object):

		#### Essential ####
	def __init__(self, master):
		self.root=master
		self.root.wm_title("Kamiken")
		self.root.geometry('{}x{}'.format(1100,300))
		self.root.configure(background='white')
		self.create_base_elements()						# build base GUI elements
#		self.draw_board(launcher.board)
		global ThrListen								# make it global to force-stop
		ThrListen=Thread(target=self.nw_listen,args=())	# create a network listener thread
		ThrListen.setDaemon(True)
		ThrListen.start()
		self.draw_board(launcher.board)

	def _quit(self):			
		self.root.quit()    # stop mainloop
		self.root.destroy()	# destroy window just in case	
				
	def nw_listen(self):						# network listener
		while True:								# infinite loop
			msg=launcher.receive()				# waits for message
			self.message_classifier(msg)		# sends the message to classifier
			
	def message_classifier(self,msg):

			# determine the type of data received based in it's prefix
		if re.search('^__MOVE__',msg):
			if self.action_validation(msg[8:]):
				self.refresh_fig(msg[8],msg[9:])
		if re.search('^__INFO__',msg):
			self.update_text(msg[8:])
		if re.search('^__SETT__',msg):
			print("got some settings")
			launcher.settings(msg[8:])	
		if re.search('^__CHAT__',msg):
			self.update_chat(msg[8:],'stranger')
		
	def create_base_elements(self):					# creates all base GUI elements

					#main figure and canvas
		self.fig=plt.figure(figsize=(5,3.2))
		self.field=self.fig.add_subplot(111)
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
		self.button_startserv = Tk.Button(master=self.root, text='Start server', 
									width='10', command=self.start_server)
		self.button_startserv.place(relx=.17, rely=.1, anchor='c')
				
	def settings_menu(self):

		def save_set():		# save all changed settings
			launcher.serverip = self.servip_var.get()
			launcher.myip = self.myip_var.get()
			launcher.conn.bind((launcher.myip,launcher.clientport))
			global listenerip
			listenerip = self.myip_var.get()
			if 'server' in globals():
				serv.listenerip = self.myip_var.get()
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
		self.button_save = Tk.Button(master=self.window_settings, command = save_set,
			text="Save and close", width='15',state='normal')
		self.button_save.place(relx=.3, rely=.85, anchor='c')
				# create input fields
		self.servip_var = Tk.StringVar()
		self.servip_var.set(launcher.serverip)
		self.servip_inp = Tk.Entry(master=self.window_settings, 	# entry with server ip
									textvariable=self.servip_var, width='15')
		self.servip_inp.place(relx=.5, rely=.15, anchor='nw')
		self.servip_inp.bind('<KeyRelease>',self.on_key_event_Settings)	# invoke settings
																# event on key release
		self.myip_var = Tk.StringVar()				# entry with listener ip
		self.myip_var.set(launcher.listenerip)		
		self.myip_inp = Tk.Entry(master=self.window_settings, 
									textvariable=self.myip_var, width='15')
		self.myip_inp.place(relx=.5, rely=.36, anchor='nw')
		self.myip_inp.bind('<KeyRelease>',self.on_key_event_Settings)	
				# add text description
		self.servip_txt = Tk.Text(master=self.window_settings, height='1', width='9')
		self.servip_txt.place(relx=.2, rely=.15, anchor='nw')
		self.servip_txt.insert(Tk.INSERT,"Server IP")	# server ip input field description
		self.servip_txt.configure(state='disabled')	
		self.servip_txt = Tk.Text(master=self.window_settings, height='1', width='11')
		self.servip_txt.place(relx=.2, rely=.36, anchor='nw')
		self.servip_txt.insert(Tk.INSERT,"Listener IP")	# listener ip input field description
		self.servip_txt.configure(state='disabled')
			
	def draw_board(self,board):		# draw the game board
		#board=launcher.board
		if hasattr(self,'canvasSur'):						# if surrender canvas was present
			self.canvasSur.get_tk_widget().place_forget()	# remove it
		self.canvas.show()
		self.canvas.get_tk_widget().place(relx=0.68,rely=0.5,anchor="e") # place it
		self.canvas.get_tk_widget().pack(expand='yes',fill='y')
		
			# main plot axes, tick, range, etc, etc.
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

	def start_server(self):
		global ThrServer				# make it global to force-stop
		ThrServer=Thread(target=Run_Server,args=())
		ThrServer.setDaemon(True)		# make daemon stop when client closes
		ThrServer.start()				# run server thread
		self.button_startserv.configure(text="Running...",state="disabled")

	def dummy(self):
		pass

		#### Figure and text field updates ####
	def refresh_fig(self,x,y):
		x=float(x)+0.5
		y=float(y)-0.5	
		bkx,whx=x,x
		bky,why=y,y
		if character.player==1:
			if launcher.turn=="your":
				whhx,whhy=self.make_hits(x,y,1)			
				plt.scatter(whx,why,c='grey',s=300)				
				plt.scatter(whhx,whhy,c='red',s=50)
			if launcher.turn=="opp":
				bkhx,bkhy=self.make_hits(x,y,2)			
				plt.scatter(bkhx,bkhy,c='blue',s=50)
				plt.scatter(bkx,bky,c='black',s=300)
		
		elif character.player==2:
			if launcher.turn=="opp":
				whhx,whhy=self.make_hits(x,y,1)			
				plt.scatter(whx,why,c='grey',s=300)				
				plt.scatter(whhx,whhy,c='red',s=50)
			if launcher.turn=="your":
				bkhx,bkhy=self.make_hits(x,y,2)
				plt.scatter(bkhx,bkhy,c='blue',s=50)
				plt.scatter(bkx,bky,c='black',s=300)
			
		self.canvas.show()
		if launcher.turn=="opp":
			launcher.turn="your"	## NEEDS REWRITING AND COMMENTS

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
		self.Chat.configure(state="disabled") ## NEEDS REWRITING AND COMMENTS

	def clear_chat(self):
		self.Chat.configure(state="normal")
		self.Chat.delete(1.0,Tk.END)
		self.Chat.configure(state="disabled")
	
		#### On key events ####
	def on_key_event_MainEntry(self,event):
		s=self.MainInput.get()				# get whatever what in the field
		self.MainInput.set('')				# empty the field
		if launcher.gamestate!="playing" or s=="stop" or s=="save" or s=="skip" or s=="syshalt":
			launcher.send(s,'settings')		# sends commands as settings
		elif launcher.gamestate=="playing" and launcher.turn=="your" and self.action_validation(s):
			self.refresh_fig(s[0],s[1:])	# if your turn, refreshes the figure
			launcher.send(s,"move")			# sends your move
			launcher.turn="opp"				# and sets the turn to "opponent"
		elif launcher.gamestate=="playing" and launcher.turn=="your" and not self.action_validation(s):
			self.update_text("Not a valid move.")
		elif launcher.gamestate=="playing" and launcher.turn=="opp":
			self.update_text("Not your turn!")
		elif launcher.gamestate=="playing":
			self.MainInput.set("Something went really wrong") # shouldn't get to this
			
	def on_key_event_ChatEntry(self,event):
		text=self.ChatInput.get()
		self.ChatInput.set('')			# empty entry line
		if text=='': return				# if nothing was written, don't update/send
		self.update_chat(text,'you')
		launcher.send(text,'chat')

	def on_key_event_Settings(self,event):
		if self.servip_var.get()!=launcher.serverip or self.myip_var.get()!=launcher.myip:
			self.button_save.configure(state='normal')
		if self.servip_var.get()==launcher.serverip and self.myip_var.get()==launcher.myip:
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
				settings="set"	## NOT WORKING, NOT BEING USED, NEEDS REWRITING
			
	def make_hits(self,crdx,crdy,player):
    
		crdy=list((crdy,0))
		crdx=list((crdx,0))
		crdhx,crdhy=[],[]
		cnt=0
		
		print(type(crdx))
		print(type(crdy))
		print(type(crdhx))
		print(type(crdx[0]))
		print(type(crdy[0]))

			# 4 x axis positions of markers
		crdhx.append(crdx[cnt])
		crdhx.append(crdx[cnt])
		crdhx.append(crdx[cnt]-1)
		crdhx.append(crdx[cnt]+1)
        
        	# 4 y axis positions for respective x axis positions
		if player==1: 
			crdhy.append(crdy[cnt]+0.9)
			crdhy.append(crdy[cnt]-1.1)
			crdhy.append(crdy[cnt]-0.1)        
			crdhy.append(crdy[cnt]-0.1)   
		elif player==2:
			crdhy.append(crdy[cnt]+1.1)
			crdhy.append(crdy[cnt]-0.9)
			crdhy.append(crdy[cnt]+0.1)        
			crdhy.append(crdy[cnt]+0.1)           
    
		return crdhx,crdhy # NEEDS COMMENTS AND POSSIBLE REWRITING, BECAUSE UGLY
		
	def action_validation(self,action):
		try:
			x=int(action[0])
			y=int(action[1:])
			return True
		except:
			return False	## NEEDS REWRITING FOR 'LetNum(Num)'-type turn
	
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
			self.Chat.tag_add(tag, "matchStart","matchEnd") ## NEEDS CHANGES TO SEARCH LAST LINE ONLY
			
	def start(self):
		launcher.send("c","settings")
		rec=False
		num=0
		while rec==False: # infinite loop until player.num received
			if character.player==1:
				self.button_start.configure(command=self.create_board,
											text='Create Board',state="disabled")
				rec=True
			elif character.player==2:		
				self.button_start.configure(command=self.dummy,text='Waiting...',
											state="disabled")
				rec=True
				self.button_startserv.config(text='Connected',state='disabled')
			if num==20:
				self.update_text("Couldn't connect to the server or no response")
				return
			num+=1
			time.sleep(0.1)
	
	def create_board(self):
		launcher.send("start","settings")
		self.button_start.configure(command=self.berehit,state="disabled")
	
	def berehit(self):
		self.draw_board(launcher.board)
		self.button_start.configure(text="Surrender",command=self.surrender)
			
	def surrender(self):
		self.canvas.get_tk_widget().place_forget()	
		self.fig2=plt.figure(figsize=(7,3.2))
#		self.field=self.fig.add_subplot(111)
		self.canvasSur = FigureCanvasTkAgg(self.fig2, master = self.root)
		self.plotSur=plt
		y=np.hstack((np.arange(2,16),np.ceil(np.random.rand(5))))
		x=np.hstack((np.ceil(np.random.rand(14)),np.arange(1,2.25,0.25)))
		self.plotSur.scatter(x,y,c='red',s=500)
		self.plot.xlim(0,5)
		self.canvasSur.get_tk_widget().place(relx=0.99,rely=0.5,anchor="e")
		self.canvasSur.show()
		self.button_surrender.destroy()
		self.button_start = Tk.Button(master=self.root, text='Start', width='10', 
									command=lambda:self.draw_graph(board))
		self.button_start.place(relx=.1, rely=.1, anchor="c")
		self.update_text("Game over. Wanna go again?")
		launcher.send('maketa','data')	## PROBABLY NEEDS TO BE DELETED, but whatever

def Run_Server():
	print("started server")
	global listenerip
	global server
	server=GameServer(listenerip)
	turn=server.start()
	server.run(turn)

def main():
	global launcher
	launcher=GameLauncher()
	global character
	character=Player()
	global client
	client=GameClient(Tk.Tk())
	Tk.mainloop()

if __name__=="__main__":
	main()