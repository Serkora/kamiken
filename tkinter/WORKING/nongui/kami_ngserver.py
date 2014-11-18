#!/usr/bin/env python3


import socket
import select
import sys
import pickle
import time

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
		
	def send(self,items,player,pcklobj=False):
	
		player=str(player)
		
		if '1' in player:
			if isinstance(items,tuple):			
				for item in items:
					self.listener.sendto(str(item).encode(enc),self.pladdr[0])
			elif pcklobj:
				self.listener.sendto(pickle.dumps(items),self.pladdr[0])
				
			else:
				self.listener.sendto(str(items).encode(enc),self.pladdr[0])
		
		if '2' in player:
			if isinstance(items,tuple):			
				for item in items:
					self.listener.sendto(str(item).encode(enc),self.pladdr[1])
			elif pcklobj:
				self.listener.sendto(pickle.dumps(items),self.pladdr[1])		
			else:
				self.listener.sendto(str(items).encode(enc),self.pladdr[1])		
	

	def receive(self,size=32,source='',address=''):

		readable, writable, exceptional = (select.select(self.read_list, self.write_list,[]))
		msg,addr=readable[0].recvfrom(size)
		if "halt" in msg.decode(enc):
			sys.exit("STOPPED")
		if address:
			return msg.decode(enc), addr
		else:
			return msg.decode(enc)
		
		
	def start(self):
		n=0
		conplrs="not enough"
		print("Waiting for connections.")
		try:
			while conplrs!="enough":
				msg,addr=self.receive(address='yes')					# get message from a connected player
				print(msg)
				if msg=="c" or msg=="y":
					self.pladdr.append(addr)					# add his IP to the list
					if self.players==0:
						print("Player 1 connected!")

						self.send("waiting",1)
						self.send("p1",1) 						# send player marker
						self.send(("Successfully connected."),1)
						self.send("Waiting for other players",1)
						self.send("You are player 1 - white.",1)
						self.send("sent",1)
						"""
						games="running"
						while games=="running":
							turn="wait"
							while turn!="wait":
								msg=self.receive()
								print(msg)
							if msg=="stop":
								games="finish"
							while turn!="finished":
								self.send(input('make turn '),1)
								turn="finished"
						time.sleep(2)
						self.send(55,1)
						time.sleep(2)
						self.send(22,1)
						"""
						p1=Player(1)
						p1.moves=[2,3,2,4,1,5,1,3,5,5,1,3,5,1,3,4,1,3]
						self.send(p1,1,pcklobj=True)
#						self.players+=1
					if self.players==1: #and addr not in self.pladdr:
						print("Player 2 connected!")
						self.send("p2",2)
						self.send("Successfully connected",2)
						self.send("Game will now start",2)
						self.send("You are player 2 - black",2)
						self.send("rdyTwo players present. Do you want to wait for more or 'start' the game?",1)
#						self.players+=1
#					else:
#						self.send("You are already connected!",1)
#						print "works"
					self.players+=1								# increment number of connected players

				if msg=="start" and addr==self.pladdr[0] and self.players==2:		# if P1 sends confirmation to start
					self.send("START",(1,2))										# start the game
					conplrs="enough"										
			
			print("Time to configure the game!")

			#self.send("Choose the board size, komi and game mode, or load previous save",1)	# tell P1 to make a choice
			#self.send("Wait for P1 to set up the game", 2) 										# tell P2 to wait
			
			self.settings="set"
			while self.settings!="set":							# while not all settings have been chosen
				msg,addr=self.receive(address='yes')	# get message
				if addr==self.pladdr[0]:				# if it came from player 1 (just in case)
						if msg=="load":						
							pass						#
						elif n==0:						# set the parameters
							board=msg or "10"			#
						elif n==1:
							komi=msg or "0.5"
						elif n==2:
							mode=msg or "normal"
							self.settings="set"
							self.send("ready",2)
							turn=0
						n+=1


					### send set parameters to both players
			#self.send((board,komi,mode,turn), (1,2))
			turn=0
																
			return turn	# only turn value is need on the server side to keep track of who's turn it is
			
		except KeyboardInterrupt as e:
			print("Shutting down")


	def run(self,turn):
		print("The game begins")
		game="running"
		
		try:							
			while game!="finished":		# while the game is still running
				if turn%2==0:			# even - black's turn
				#	self.send("wait", 1)
				#	self.send("place", 2)
					msg,addr=self.receive(address='yes')	# get the sent coordinates
					if addr == self.pladdr[1]:
						if msg=="stop":					# if it was a "stop" command, the server 
							game="finished"				# also finishes the game		
							self.send(msg,1)
						elif msg=="save":
							self.send("save",1)
							continue
						else:
							self.send(msg, 1)	# and send them to the other player
							turn+=1
        					        				
				if turn%2==1:			# the same for white
				#	self.send("wait", 2)
				#	self.send("place", 1)
					msg,addr=self.receive(address='yes')
					if addr == self.pladdr[0]:
						if msg=="stop":					# if it was a "stop" command, the server 
							game="finished"				# also finishes the game
							self.send(msg,2)		
						elif msg=="save":
							self.send("save",2)
							continue
						else:
							self.send(msg, 2)			# and send them to the other player
							turn+=1
        					
#				turn+=1				# increment 1 turn

		except KeyboardInterrupt as e:
			print("Shutting down")
 		
 		
 		## run the server
if __name__ == "__main__":
	g = GameServer()
	turn=g.start()
	g.run(turn)