#!/usr/bin/env python3

import socket
import select
import random
import time
import pickle
import subprocess

#					readable, writable, exceptional = (select.select(self.read_list, self.write_list,[]))
#					for f in readable:
#						if f is self.conn:
#							msg,addr=f.recvfrom(32)

serverip="127.0.0.1"
#serverip="25.65.255.143"
#serverip="25.64.15.244"

myip="127.0.0.1"
#myip="25.64.15.244"

enc='UTF-8'

#import tempmult.py

#si=subprocess.STARTUPINFO()
#si = subprocess.Popen(["python3", "/users/arichi/documents/python/kamiken_multiplayer/3.4/kami_ngserver.py"], \
#	shell=True, creationflags = "CREATE_NEW_CONSOLE").pid

#pid = subprocess.Popen(args=[
#    "python3", "test2.py"]).pid
#print(pid)


class Player(object):
	def __init__(self,player=1):
		self.player=player
		self.moves=[]
		self.score=0
	
	def move(self,move):
		self.moves.append(move)		


class GameClient(object):
	def __init__(self, addr=serverip,serverport=9009):
		self.clientport = random.randrange(8000, 8999)
		self.conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		# Bind to localhost - set to external ip to connect from other computers
		self.conn.bind((myip,self.clientport))
		self.addr = addr
		self.serverport = serverport
		self.read_list = [self.conn]
		self.write_list = []

	def send(self,string,dest='server'):
		
		if dest=='server':
			self.conn.sendto(string.encode(enc),(self.addr,self.serverport))
	
	def receive(self,source='server',size=32,pcklobj=False):
		readable, writable, exceptional = (select.select(self.read_list, self.write_list,[]))
		msg,addr=readable[0].recvfrom(size)
		
		try:
			msg=pickle.loads(msg)
			return msg
		except pickle.PickleError:
			return msg.decode(enc)


	def start(self):
		game="waiting"
		print("Welcome to Kamiken, the game of the wisest!")
		msg=input('Would you like to connect to the server? [y/n]')
		self.send(msg)
		
		if msg=="y" or msg=="c":
#			self.send('c')		# send confirmation to connect

			while game=="waiting":
				msg=self.receive(size=128)
				print(msg)
				if msg=="p1":
					player=1
				elif msg=="p2":
					player=2
				elif msg[0:3]=="rdy":
					print(msg[3:])
					self.send(input())
				#elif msg=="sent":
				#	player1=pickle.loads(self.receive(size=512,notstring=True))
				#	print(player1)
				elif msg=="START":
					game="setup"
				else:
					print(msg)
												
			if player==2:
				msg=self.receive()
				print(msg)
				while game!="ready":
					msg=self.receive()
					if msg=="ready":					# when P1 has finished setting up the game
						game="ready"					# confirmation of readiness is sent to P2

			elif player==1:
				msg=self.receive(size=256)
				print(msg)
				self.send(input('Set board size (default - 10)'))	# set up
				self.send(input('Set komi value (default - 0.5)'))	# the
				self.send(input('Choose game mode (default - normal)'))	# game
				game="ready"							# ready!
				
		if game=="ready":
			data=[]
			print("All is set, good luck!")
			while len(data)!=4:
				msg=self.receive()		# get all 4 parameters
				data.append(msg)		# into one list
						
			board=int(data[0])			# split them into separate
			komi=float(data[1])			
			mode=data[2]
			turn=int(data[3])

		return board, komi, mode, turn, player # return parameters to use in an actual game
	
	def run(self, board, komi, mode, turn, player):
		print("You are player "+str(player))
		print("board size is "+str(board)+"x"+str(board))		#
		print("komi is set to "+str(komi)+" points")			# temporary
		print("game mode - "+str(mode))							#
		print(str(turn)+" turns have passed")
		game="running"
		
		while game=="running":							# while the game is still not finished
#			readable, writable, exceptional = (select.select(self.read_list, self.write_list,[]))
#			for f in readable:
#				if f is self.conn:
#					msg,addr=f.recvfrom(32)				# depending on turn, either place a stone or wait for opponent
#			msg=self.receive()
#			if msg=="wait":
#				print("Wait for your opponent to make a move")
#			if msg=="place":
#				print("Your turn. Where do you want to place a stone?")

			if player==1:		
			
				if turn%2==1:
					move=input()				# make a move
					self.send(move)				# send move to other player
					if move=="stop":
						game="finished"
					elif move=="save":
						print("Game saved")
						continue
					else:
						make_turn(move)				# game code
						
				if turn%2==0:
					move=self.receive()			# get opponents move
					if move=="stop":
						game="finished"
						continue
					elif move=="save":
						print("Your opponent decided to save the game!")
						continue
					else:
						make_turn_opp(move)		# then also make that move
			
			if player==2:		

				if turn%2==0:
					move=input()				# input coordinates
					self.send(move)				# send them to other player
					if move=="stop":
						game="finished"
						continue
					elif move=="save":
						print("Game saved")
						continue
					else:
						make_turn(move)			# make turn

				if turn%2==1:
					move=self.receive()
					if move=="stop":
						game="finished"
					elif move=="save":
						print("Your opponent decided to save the game!")
						continue
					else:
						make_turn_opp(move)
			
			turn+=1					# increment turn
				
		### Game code begins here		
				
def make_turn(move):
	print("You have placed your stone at "+move)
	
def make_turn_opp(move):
	print("Your opponent have placed your stone at "+move)
				

		## run the game
if __name__ == "__main__":
	g = GameClient()
	board,komi,mode,turn,player=g.start()
	g.run(board,komi,mode,turn,player)