import socket
import select
import sys

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


# addr = ('127.0.0.1', 8902)
#f.recvfrom(32) = ("msg",addr)


class GameServer(object):
	def __init__(self, port=9009):
		self.listener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.listener.bind(("127.0.0.1",port))
		self.read_list = [self.listener]
		self.write_list=[]
		self.players=0			# number of connected players
		self.pladdr=[]			# players IPs to distinguish between players 1 and 2
		self.settings="not set"	# to make sure all the settings are set
#		self.modes={"normal" : "Normal mode",
#					"blind" : "You won't see the field until the end of the game",
#					"hardcore" : "You won't even know the score or your opponents moves"} 
		
	def start(self):
		n=0
		print "Waiting for connections."
		try:
			while self.players<2:
				readable, writable, exceptional = (
          		select.select(self.read_list, self.write_list, [])		# makes it possible to receive messages.
          		)														# magically.
				for f in readable:
					if f is self.listener:
						msg,addr = f.recvfrom(32)						# get message from first connected player
						if msg=="c":
							self.pladdr.append(addr)					# add his IP to the list
							if self.players==0:
								print "Player 1 connected!"
								self.listener.sendto("p1",self.pladdr[0])			# send p1 marker to let the client know
								self.listener.sendto("Successfully connected.",self.pladdr[0])
								self.listener.sendto("Waiting for other players",self.pladdr[0])
								self.listener.sendto("You are player 1 - white.",self.pladdr[0])
#								self.players+=1
							if self.players==1: #and addr not in self.pladdr:
								print "Player 2 connected!"	
								self.listener.sendto("p2",self.pladdr[1])
								self.listener.sendto("Successfully connected",self.pladdr[1])
								self.listener.sendto("Game will now start",self.pladdr[1])
								self.listener.sendto("You are player 2 - black",self.pladdr[1])
								self.listener.sendto("start",self.pladdr[0])
								self.listener.sendto("start",self.pladdr[1])
#								self.players+=1
#							else:
#								self.listener.sendto("You are already connected!",self.pladdr[0])
#								print "works"

							self.players+=1								# increment number of connected players
			
			print "Time to configure the game!"

			self.listener.sendto("Wait for P1 to set up the game",self.pladdr[1]) 	# tell P2 to wait
			self.listener.sendto("Choose the board size, kami and",self.pladdr[0])	# tell P1 to make a choice
			self.listener.sendto("game mode, or load previous save",self.pladdr[0])
			
			while self.settings!="set":												# whiel not all settings have been chosen
				readable, writable, exceptional = (select.select(self.read_list, self.write_list,[]))
				for f in readable:
					if f is self.listener:
						msg,addr = f.recvfrom(32)			# get current message
						if addr==self.pladdr[0]:			# if it came from player 1 (just in case)
							if msg=="load":						
								pass						#
							elif n==0:						# set the parameters
								board=msg					#
							elif n==1:
								komi=msg
							elif n==2:
								mode=msg
								self.settings="set"
								self.listener.sendto("ready",self.pladdr[1])
								turn=0
							n+=1


					### send set parameters to both players
			self.listener.sendto(board, self.pladdr[0])
			self.listener.sendto(komi, self.pladdr[0])
			self.listener.sendto(mode, self.pladdr[0])	
			self.listener.sendto(str(turn), self.pladdr[0])
			self.listener.sendto(board, self.pladdr[1])
			self.listener.sendto(komi, self.pladdr[1])
			self.listener.sendto(mode, self.pladdr[1])
			self.listener.sendto(str(turn), self.pladdr[1])
																
			return turn	# only turn value is need on the server side to keep track of who's turn it is
			
		except KeyboardInterrupt as e:
			print "Shutting down"

	def run(self,turn):
		print "Game begins"
		game="running"
		
		try:							
			while game!="finished":		# while game is still running
				if turn%2==0:			# even - black's turn
					self.listener.sendto("wait", self.pladdr[0])
					self.listener.sendto("place", self.pladdr[1])
					readable, writable, exceptional = (select.select(self.read_list, self.write_list, []))
					for f in readable:
						if f is self.listener:
							msg,addr = f.recvfrom(32)		# read the sent coordinates
							if addr == self.pladdr[1]:
								self.listener.sendto(msg, self.pladdr[0])	# and send them to other player
								if msg=="stop":				# if it was "stop" command, the server 
									game="finished"			# also finished the game		
        				
				if turn%2==1:
					self.listener.sendto("wait", self.pladdr[1])
					self.listener.sendto("place", self.pladdr[0])
					readable, writable, exceptional = (select.select(self.read_list, self.write_list, []))
					for f in readable:
						if f is self.listener:
							msg,addr = f.recvfrom(32)
							if addr == self.pladdr[0]:
								self.listener.sendto(msg, self.pladdr[1])        										
								if msg=="stop":
									game="finished"
        					
 				turn+=1					# increment 1 turn

		except KeyboardInterrupt as e:
			print "Shutting down"
 		
 		
 		## run the server
if __name__ == "__main__":
	g = GameServer()
	turn=g.start()
	g.run(turn)