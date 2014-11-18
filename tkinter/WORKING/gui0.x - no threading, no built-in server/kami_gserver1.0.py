#!/Library/Frameworks/Python.framework/Versions/3.4/bin/python3.4

import socket
import select
import sys
import pickle
import time
import string
import re

# Messages:
#  Client->Server
#   One or two characters. First character is the command:
#     c: connect
#     u: update position
#     d: disconnect
#   Second character only applies to position and specifies direction (udlr)
#
#  Server->Client
#   '|' delimited pairs of positions to draw the players (there is no
#     distinction between the players - not even the client knows where its
#     player is.


# addr = ('1227.0.0.1', 8902)
#f.recvfrom(32) = ("msg",addr)


#listnerip="25.64.15.244"
listenerip="127.0.0.1"

enc='UTF-8'


class Player(object):
	def __init__(self,player=1):
		self.player=player
		self.moves=[]
		self.score=0
	
	def move(self,move):
		self.moves.append(move)	

class GameServer(object):
	def __init__(self, port=9009):
		self.listener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.listener.bind((listenerip,port))
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
				msg,addr,dtype=self.receive()					# get message from a connected player
				print(msg)
				if msg=="c" or msg=="y":
					self.pladdr.append(addr)					# add his IP to the list
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
						self.send("Two players present. Do you want to wait for more or start the game?",1,"info")
						self.send("Wait for P1 to set up the game", 2,'info')
					self.players+=1								# increment number of connected players
				print("twotwo")
				if msg=="start" and addr==self.pladdr[0] and self.players==2:		# if P1 sends confirmation to start
					self.send("ready",(1,2),'settings')	
					print("sdsf")									# start the game
					conplrs="enough"										
			
			print("Time to configure the game!")

			self.send("Choose the board size, komi and game mode, or load previous save",1,'info')	# tell P1 to make a choice
#			self.send("creation",1,'settings')
			self.send("Wait for P1 to set up the game", 2,'info') 			# tell P2 to wait

			
			self.settings="set"
			while self.settings!="set":							# while not all settings have been chosen
				msg,addr,dtype=self.receive(address='yes')	# get message
				if addr==self.pladdr[0]:					# if it came from player 1 (just in case)
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
			board=7
			komi=0.5
			mode='normal'
			turn=0
			self.send((('board'+str(board)),('komi'+str(komi)),'mode'+mode,'turn'+str(turn)), (1,2),'settings')
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
 		
 		
 		## run the server
if __name__ == "__main__":
	g = GameServer()
	turn=g.start()
	g.run(turn)