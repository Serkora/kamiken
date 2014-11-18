#!/Library/Frameworks/Python.framework/Versions/3.4/bin/python3.4
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  3 18:08:29 2014

@author: arichi
"""

import string
import os
import re
import numpy as np
import pickle
import socket
import select
import random
import time
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from numpy import arange, sin, pi
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
# implement the default mpl key bindings
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import sys
if sys.version_info[0] < 3:
    import Tkinter as Tk
else:
    import tkinter as Tk
#    import tkinter.tkSimpleDialog
import tkinter as tkinter
#from tkinter import *

from multiprocessing import Process

import tkinter.scrolledtext
from tkinter import font

from threading import Thread
import threading
import subprocess

serverip='127.0.0.1'
#serverip="25.65.255.143"
#serverip="25.64.15.244"
myip='127.0.0.1'
#myip="25.64.15.244"
enc='UTF-8'

#listnerip="25.64.15.244"
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

class Launcher(object):
	def __init__(self, addr=serverip,serverport=9009):
		self.clientport = random.randrange(8000, 8999)
#		self.clientport = 8500
		self.conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		# Bind to localhost - set to external ip to connect from other computers
		self.conn.bind((myip,self.clientport))
		self.conn.setblocking(0)
		self.addr = addr
		self.serverport = serverport
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
			dest=(self.addr,self.serverport)
		else:
			dest=destination
		
			
		if not pcklobj and dtype!="pickle" and dtype!="pckl" and dtype!="obj" and dtype!="object":
			dtype="__"+dtype[0:4].upper()+"__"
		else:
			pcklobj=True
		
		if not pcklobj:
			self.conn.sendto((dtype+str(items)).encode(enc),dest)
		else:
			self.conn.sendto(pickel.dumps(items),dest)
	
	def receive(self,source='server',size=128,notstring=False):
#		readable, writable, exceptional = (select.select(self.read_list, self.write_list,[]))
		try:
			msg,addr=self.conn.recvfrom(size)
			print(msg)
		except socket.error:
			msg="empty"
			return msg
#		print(len(msg))
		if notstring:# or msg is None:
#			print(msg)
			return msg
		return msg.decode(enc)

	def settings(self,setting):
		if len(setting)==2 and setting[0]=="p":
			character.player=int(setting[1])
			Appgui.updbtn()
			print("YOU ARE PLAYER"+str(character.player))
		elif re.search('^board',setting):
			self.board=int(setting[5:])
		elif re.search('^komi',setting):
			self.komi=int(setting[4])
		elif re.search('^mode',setting):
			self.mode=setting[4:]
		elif re.search('turn',setting):
			print("HASDHASDHKJASDHJKSAD")
			if int(setting[4:])%2 == character.player-1:
				self.turn="your"
				print("ooooooooo")
			else:
				self.turn="opp"
				print("HHHHHHH")
		elif re.search('ready',setting):
#			self.game
			Appgui.update_text(setting[3:])
			Appgui.button_start.configure(state='normal')
		elif re.search('creation',setting):
			#Appgui.board_creation()
			pass
		elif re.search("gogo",setting):
			lnchr.gamestate="playing"
			Appgui.berehit()

class App(object):

		#### Essential ####
	def __init__(self, master):
		self.root=master
		self.root.wm_title("Kamiken")
		self.root.geometry('{}x{}'.format(1100,300))
		self.root.configure(background='white')
		self.create_base_elements()				# call functions to build all base GUI elements
#		self.draw_board(lnchr.board)

	def _quit(self):			
		self.root.quit()    # stop mainloop
		self.root.destroy()	# destroy window just in case	
		
	def nw_listen(self):	# network listener
		msg=lnchr.receive()
		if msg=="empty":						# if no message, try again in 150ms
			self.root.after(150,self.nw_listen) 
		else:									# if there is, send it to message classifier
			self.message_classifier(msg)			# for further use

	def message_classifier(self,msg):

			# determine the type of data received based in it's prefix
		if re.search('^__MOVE__',msg):
			if self.action_validation(msg[8:]):
				self.refresh_fig(msg[8],msg[9:])
		if re.search('^__INFO__',msg):
			self.update_text(msg[8:])
		if re.search('^__SETT__',msg):
			print("got some settings")
			lnchr.settings(msg[8:])	
		if re.search('^__CHAT__',msg):
			self.update_chat(msg[8:],'stranger')

		self.nw_listen()	# start the network listener again
		
	def create_base_elements(self):					# creates all base GUI elements

					#main figure and canvas
		self.fig=plt.figure(figsize=(5,3.2))
		self.field=self.fig.add_subplot(111)
		self.canvas = FigureCanvasTkAgg(self.fig, master = self.root)
		self.canvas.mpl_connect('key_press_event', self.on_key_event)

					# main text field
		self.text=Tk.scrolledtext.ScrolledText(master=self.root,height=8,width=40)
		self.text.place(relx=0.3, rely=0.9, anchor="se")
#		self.text.bind('<1>',self.text.configure(state="normal"))
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
		self.ChatEntry=Tk.Entry(master=self.root,textvariable=self.ChatInput,width=41)
		self.ChatEntry.place(relx=1,rely=0.9,anchor='se')
		self.ChatEntry.bind('<Return>',self.on_key_event_ChatEntry)
	
					#buttons
		self.button_quit = Tk.Button(master=self.root, text='Quit', width='10', command=self._quit)
		self.button_quit.place(relx=.06, rely=.3, anchor="c")
#		self.button_refresh = Tk.Button(master=self.root, text='Refresh', width='10', command=lambda:self.refresh_fig(5*np.random.rand(1),5*np.random.rand(1)))
		self.button_refresh = Tk.Button(master=self.root, text='Refresh', width='10', command=self.start_server)
		self.button_refresh.place(relx=.06, rely=.2, anchor="c")
		self.button_start = Tk.Button(master=self.root, text='Start', width='10', command=self.start)
		self.button_start.place(relx=.06, rely=.1, anchor="c")			
		
	def draw_board(self,board):		# draw the game board
		#board=lnchr.board
		if hasattr(self,'canvasSur'):						# if surrender canvas was present
			self.canvasSur.get_tk_widget().place_forget()	# remove it
		self.canvas.show()
		self.canvas.get_tk_widget().place(relx=0.68,rely=0.5,anchor="e") # place it
		
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

		#### Figure and text field updates ####
	def refresh_fig(self,x,y):
		x=float(x)+0.5
		y=float(y)-0.5	
		bkx,whx=x,x
		bky,why=y,y
		if character.player==1:
			if lnchr.turn=="your":
				whhx,whhy=self.make_hits(x,y,1)			
				plt.scatter(whx,why,c='grey',s=300)				
				plt.scatter(whhx,whhy,c='red',s=50)
			if lnchr.turn=="opp":
				bkhx,bkhy=self.make_hits(x,y,2)			
				plt.scatter(bkhx,bkhy,c='blue',s=50)
				plt.scatter(bkx,bky,c='black',s=300)
		
		elif character.player==2:
			if lnchr.turn=="opp":
				whhx,whhy=self.make_hits(x,y,1)			
				plt.scatter(whx,why,c='grey',s=300)				
				plt.scatter(whhx,whhy,c='red',s=50)
			if lnchr.turn=="your":
				bkhx,bkhy=self.make_hits(x,y,2)
				plt.scatter(bkhx,bkhy,c='blue',s=50)
				plt.scatter(bkx,bky,c='black',s=300)
			
		self.canvas.show()
		if lnchr.turn=="opp":
			lnchr.turn="your"	

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
		self.ChatInput.set('')
		self.highlight_chat("YOU: ",'red')
		self.highlight_chat("STRANGER: ",'blue')
		self.Chat.configure(state="disabled")

		#### On key events ####
	def on_key_event(self,event):
		print(event.key)

	def on_key_event_MainEntry(self,trash):
		s=self.MainInput.get()
		self.MainInput.set('')
		if s=="stop" or s=="save" or s=="skip" or s=="syshalt":
			lnchr.send(s,'move')
		elif lnchr.gamestate=="playing" and lnchr.turn=="your" and self.action_validation(s):
			print(lnchr.turn)
			self.refresh_fig(s[0],s[1:])
			print(lnchr.turn)
			lnchr.send(s,"move")
			print(lnchr.turn)
			lnchr.turn="opp"
		elif lnchr.gamestate=="playing" and lnchr.turn=="your" and not self.action_validation(s):
			self.update_text("Not a valid move.")
		elif lnchr.gamestate=="playing" and lnchr.turn=="opp":
			self.update_text("Not your turn!")
		elif lnchr.gamestate=="playing":
			self.MainInput.set(s)
		elif lnchr.gamestate!="playing":
			lnchr.send(s,"settings")
			
	def on_key_event_ChatEntry(self,text):
		text=self.ChatInput.get()
		self.update_chat(text,'you')
		lnchr.send(text,'chat')

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
					lnchr.send(s,"settings")
				n+=1
			if n==1:
				self.update_text("choose komi value")
				if not isinstance(s,int) or not isinstance(s,float):
					self.update_text("Not a valid komi value, must be int or float")
				else:
					lnchr.send(s,"settings")
				n+=1
			if n==2:
				self.update_text("Choose game mode")
				lnchr.send(s,"settings")
				settings="set"
			
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
    
		return crdhx,crdhy
		
	def action_validation(self,action):
#		if action=="save" or action=="stop" or action=="syshalt" or action=="skip":
#			return True
		try:
			x=int(action[0])
			y=int(action[1:])
			return True
		except:
			return False
	
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
			self.Chat.tag_add(tag, "matchStart","matchEnd")
			
	def start(self):
		lnchr.send("c",'data')
		self.nw_listen()
	
	def updbtn(self):
#		time.sleep(0.5)
		print("ASHDKJASJKHSD - "+str(character.player))
#		while character.player<1:
		if character.player==1:
			self.button_start.configure(command=self.get_board,text='Create Board',state="disabled")
		elif character.player==2:		
			self.button_start.configure(command=self.get_board,text='Waiting...',state="disabled")
		self.nw_listen()
	
	def get_board(self):
		lnchr.send("start","settings")
		self.button_start.configure(command=self.berehit,state="disabled")
#		lnchr.gamestate="playing"
		print("YOU ARE ARE PLAYER "+str(character.player))
	
	def berehit(self):
#		lnchr.send("start","settings")
		self.draw_board(lnchr.board)
		self.button_start.destroy()
		self.button_surrender = Tk.Button(master=self.root, text='Surrender', width='10', command=self.surrender)
		self.button_surrender.place(relx=.06, rely=.1, anchor="c")

#		lnchr.send("c",'data')
		self.nw_listen()
	
	def start_server(self):
		pr1=Process(self.start_server2())
		pr1.start()
		
	def start_server2(self):
		print("STARTING")
		g=GameServer()
		print("MADE STHE SRER")
		turn=g.start()
		print("GOT TUR")
		print("RUNNIGNG")
		g.run(turn)
		print("stopped?")
		
			
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
		self.button_start = Tk.Button(master=self.root, text='Start', width='10', command=lambda:self.draw_graph(board))
		self.button_start.place(relx=.1, rely=.1, anchor="c")
		self.update_text("Game over. Wanna go again?")
		lnchr.send('maketa','data')


def run_server(serv):
	print("started server")
	turn=serv.start()
	serv.run(turn)

lnchr=Launcher()
character=Player()	
ser=GameServer()
Appgui=App(Tk.Tk())
Tk.mainloop()



#main()