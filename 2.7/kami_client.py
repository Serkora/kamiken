#import pygame
#import pygame.locals
import socket
import select
import random
import time


class GameClient(object):
	def __init__(self, addr="127.0.0.1",serverport=9009):
		self.clientport = random.randrange(8000, 8999)
		self.conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		# Bind to localhost - set to external ip to connect from other computers
		self.conn.bind(("127.0.0.1",self.clientport))
		self.addr = addr
		self.serverport = serverport
		self.read_list = [self.conn]
		self.write_list = []

	def start(self):
		game="waiting"
		print "Welcome to Kamiken, the game of the wisest!"
		msg=raw_input('Would you like to connect to server? [y/n]')

		if msg=="y" or msg=="c":
			self.conn.sendto("c", (self.addr, self.serverport))		# send confirmation to connect

			while game=="waiting":
				readable, writable, exceptional = (select.select(self.read_list, self.write_list,[]))
				for f in readable:
					if f is self.conn:
						msg,addr=f.recvfrom(32)			# receive player marker or 
						if msg=="p1":					# persmission to start
							player=1
						elif msg=="p2":
							player=2
						elif msg=="start":				# start the game when received "start"
							game="setup"				# confirming two players on server
						else:
							print msg
							
			readable, writable, exceptional = (select.select(self.read_list, self.write_list,[]))
			if player==2:
				for f in readable:
					if f is self.conn:
						msg,addr=f.recvfrom(32)			# get some introductory info
						print msg
				while game!="ready":
					readable, writable, exceptional = (select.select(self.read_list, self.write_list,[]))
					for f in readable:
						if f is self.conn:
							msg,addr=f.recvfrom(32)
							if msg=="ready":			# when P1 has finished setting up the game
								game="ready"			# confirmation of readiness is sent to P2

			elif player==1:
				for i in range(0,2):
					readable, writable, exceptional = (select.select(self.read_list, self.write_list,[]))
					for f in readable:
						if f is self.conn:
							msg,addr=f.recvfrom(32)		# receive the info of being the chosen one
							print msg
				self.conn.sendto(raw_input('Choose board size '),(self.addr,self.serverport))	# set up
				self.conn.sendto(raw_input('Choose kami value '),(self.addr,self.serverport))	# the
				self.conn.sendto(raw_input('Choose game mode '),(self.addr,self.serverport))	# game
				game="ready"							# ready!
				
		if game=="ready":
			data=[]
			print "All is set, good luck!"
			while len(data)!=4:
				readable, writable, exceptional = (select.select(self.read_list, self.write_list,[]))
				for f in readable:
					if f is self.conn:
						msg,addr = f.recvfrom(32)		# get all 4 parameters
						data.append(msg)				# into one list
						
			board=int(data[0])			# split them into separate
			kami=float(data[1])			
			mode=data[2]
			turn=int(data[3])

		return board, kami, mode, turn, player # return parameters to use in an actual game
	
	def run(self, board, kami, mode, turn, player):
		print "You are player "+str(player)
		print "board size is "+str(board)+"x"+str(board)		#
		print "kami is set to "+str(kami)+" points"				# temporary
		print "game mode - "+str(mode)							#
		print str(turn)+" turns have passed"
		game="running"
		
		while game=="running":							# while the game is still not finished
			readable, writable, exceptional = (select.select(self.read_list, self.write_list,[]))
			for f in readable:
				if f is self.conn:
					msg,addr=f.recvfrom(32)				# depending on turn, either place a stone or wait for opponent
					if msg=="wait":
						print "Wait for your opponent to make a move"
					if msg=="place":
						print "Your turn. Where do you want to place a stone?"

			if player==1:		
				if turn%2==1:
					move=raw_input()										# make a move
					self.conn.sendto(move,(self.addr,self.serverport))		# send move to other plaey
					make_turn(move)											# game code
				if turn%2==0:
					readable, writable, exceptional = (select.select(self.read_list, self.write_list,[]))
					for f in readable:
						if f is self.conn:
							msg,addr=f.recvfrom(32)							# if opponents turn
							move=msg										# receive his move
					print "Your opponent placed a stone at "+move			# then also make that move
			
			if player==2:		
				if turn%2==0:
					move=raw_input()
					self.conn.sendto(move,(self.addr,self.serverport))
					make_turn(move)
				if turn%2==1:
					readable, writable, exceptional = (select.select(self.read_list, self.write_list,[]))
					for f in readable:
						if f is self.conn:
							msg,addr=f.recvfrom(32)
							move=msg
					print "Your opponent placed a stone at "+move
			
			turn+=1					# increment turn
				
		### Game code begins here		
				
def make_turn(move):
	print "you have placed your stone at "+move
				

		## run the game
if __name__ == "__main__":
	g = GameClient()
	board,kami,mode,turn,player=g.start()
	g.run(board,kami,mode,turn,player)