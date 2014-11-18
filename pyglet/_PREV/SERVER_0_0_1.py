#!/Library/Frameworks/Python.framework/Versions/3.4/bin/python3.4
import socket
import pickle
import re


listenerip = '0.0.0.0'
enc = 'utf-8'

class GameServer(object):

	def __init__(self, port=9009):
		self.listener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#		self.listenerip = client.listenerip
		self.listenerip = listenerip
		print(self.listenerip)
		self.listener.bind((self.listenerip,port))
		self.read_list = [self.listener]
		self.write_list=[]
		self.shutdown=False
		self.gamestate=''
		self.players=0			# number of connected players
		self.pladdr=[]			# players IPs to distinguish between players 1 and 2
		self.settings="not set"	# to make sure all the settings are set
#		self.modes={"normal" : "Normal mode",
#					"blind" : "You won't see the field until the end of the game",
#					"hardcore" : "You won't even know the score or your opponents moves"} '
	
	def send(self,items,player,type,pcklobj=False,header=''):
		
		player=str(player)
		print("Server is trying to send")				
		
		if not pcklobj and type!="pickle" and type!="pckl" and type!="obj" and type!="object":
			type="__"+type[0:4].upper()+"__"
			print('"',items,'"')
		else:
			print("Pickled Object")
			pcklobj=True

		print("To player(s) ",player)
		
		if '1' in player:
			if isinstance(items,tuple):			
				for item in items:
					self.listener.sendto((type+str(item)).encode(enc),self.pladdr[0])
			elif pcklobj:
				self.send_pickle(items,header,self.pladdr[0])
			else:
				self.listener.sendto((type+str(items)).encode(enc),self.pladdr[0])
	
		if '2' in player:
			if isinstance(items,tuple):			
				for item in items:
					self.listener.sendto((type+str(item)).encode(enc),self.pladdr[1])
			elif pcklobj:
				self.send_pickle(items,header,self.pladdr[1])		
			else:
				self.listener.sendto((type+str(items)).encode(enc),self.pladdr[1])
		print("-----------")

	def send_pickle(self, object, header, destination):
		"""
		For info check 'send_pickle' in the client
		"""
		print("Sending pickled object with header",header)
		message=pickle.dumps(("START",header,object,'END'))
		data,addr=[],[]
		complete=False
		n=0
		for i in range(0,len(message),420):
			data.append(message[i:i+420])		
		while not complete:
			self.listener.sendto(data[n],destination)
			print("Server sent datagram number",n)
			while addr!=destination:
				msg,addr=self.listener.recvfrom(128)
			if msg.decode(enc)[8:]=='next_datagram':
				print("Server received confirmation of datagram",i,"receipt")
				n+=1
				addr,msg='',''
				continue
			elif msg.decode(enc)[8:]=='complete':
				print("Server received confirmation whole message receipt")
				complete=True
				break
		print("Successfully Sent pickled object")		

	def receive(self,size=512,source='',address='yes',dtype='yes'):
		msg,addr=self.listener.recvfrom(size)
		print("Server received")
		print("From ",addr)
		if address=='no' or dtype=='no' or dtype=="pickle":
				print("-----------")
				return msg
		else:
			try:
				if msg.decode(enc)[8:]=="syshaltabortabortabort":
					self.send('serverstoppedserver',(list(range(1,self.players+1))),'settings')
					self.listener.close()
					print("Server shutting down...")
					self.shutdown=True
					sys.exit("exiting")
				elif msg.decode(enc)[8:]=="testcomm":
					pass
				else:
					print(msg)
					print("-----------")
					return msg.decode(enc)[8:], addr, self.action_classifier(msg.decode(enc))
			except:
				if not self.shutdown:
					print("Server is receiving pickle object")
					data=self.receive_pickle(msg,addr)
					print("Sever received pickle object")
					print("-----------")
					return data, addr, 'pickle'
				
	def receive_pickle(self,message,address):
		"""
		For (lots of) info check the "receive_pickle" function in client
		"""
		complete=False
		data=message
		print("Address of sender:",address)
		pnum=self.pladdr.index(address)+1
		while not complete:
			try:
				print("Server trying to 'loads' data")
				pickle.loads(data)
				complete=True
				self.send('complete',pnum,'pack')
			except:										
				print("Unable to 'loads', waiting for the next packet")
				self.send('next_datagram',pnum,'pack')	# self.receive can't be called 
				msg,addr=self.listener.recvfrom(512)	# here because this very function
				data+=msg								# was called from it.
		return data

	def action_classifier(self,msg):
		if re.search('^__MOVE__',msg):
			return "movement"
		if re.search('^__INFO__',msg):
			return "info"
		if re.search('^__SETT__',msg):
			return "settings"
		if re.search('^__CHAT__',msg):
			return "chat"	
		if re.search('^__CONF__',msg):
			return 'confirmation'
		if re.search('^__CONR__',msg):
			return 'confirmation approval'
		
									# Currently different solution is present to allow
									# new/load, but lacks any custom settings setup
									
# 	def start2(self):
# 		n=0
# 		conplrs="not enough"
# 		print("Waiting for connections.")
# 		try:
# 			while conplrs!="enough":
# 				msg,addr,dtype=self.receive()		# get message from a connected player
# 				if dtype=='pickle':
# 					continue
# 				print(msg)
# 				if msg=="c" or msg=="y":
# 					self.pladdr.append(addr)		# add his IP to the list
# 					if self.players==0:
# 						print("Player 1 connected!")
# 						self.send("p1",1,"settings") 				# send player marker
# 						self.send("Successfully connected.",1,"info")
# 						self.send("Waiting for other players",1,"info")
# 						self.send("You are player 1 - white.",1,"info")
# 						self.players+=1					# add a player
# 					elif self.players==1: #and addr not in self.pladdr:
# 						print("Player 2 connected!")
# 						self.send("p2",2,"settings")
# 						self.send("Successfully connected",2,"info")
# 						self.send("Game will now start",2,"info")
# 						self.send("You are player 2 - black",2,"info")
# 						self.send("ready",1,"settings")
# 						self.send("Two players present. Do you want " \
# 									"to wait for more or start the game?",1,"info")
# 						self.send("Wait for P1 to set up the game", 2,'info')
# 						self.players+=1					# increment number of connected players
# 				if msg=="start" and addr==self.pladdr[0] and self.players==2:		
# 														# if P1 sends confirmation to start
# 					self.send("ready",(1,2),'settings')	
# 					print("sdsf")									# start the game
# 					conplrs="enough"										
# 			
# 			print("Time to configure the game!")
# 
# 			self.send("Choose the board size, komi and game mode, "\
# 						"or load previous save",1,'info')		# tell P1 to make a choice
# #			self.send("creation",1,'settings')
# 			self.send("Wait for P1 to set up the game", 2,'info') # tell P2 to wait
# 
# 			
# 			self.settings="set"
# 			while self.settings!="set":						# while not all settings have been chosen
# 				msg,addr,dtype=self.receive(address='yes')	# get message
# 				if addr==self.pladdr[0]:					# if it came from player 1
# 						if msg=="load":						
# 							pass						#
# 						elif n==0:						# set the parameters
# 							board=msg or "10"			#
# 						elif n==1:
# 							komi=msg or "0.5"
# 						elif n==2:
# 							mode=msg or "normal"
# 							self.settings="set"
# 							self.send("ready",2,'settings')
# 							turn=0
# 						n+=1
# 
# 
# 					### send set parameters to both players
# 			board=14
# 			komi=0.5
# 			mode='normal'
# 			turn=goban.turn
# 			self.send((('board'+str(board)),('komi'+str(komi)),\
# 						'mode'+mode,'turn'+str(turn)), (1,2),'settings')
# 			self.send("gogo",(1,2),"settings")
# 																
# 			return turn	# only turn value is need on the server side to keep track of who's turn it is
# 			
# 		except KeyboardInterrupt as e:
# 			print("Shutting down")

	def start(self):
		print(self.listener)
		print("waiting for connections.")
		try:
			while self.players<2:
				msg,addr,dtype=self.receive()
				if dtype=='pickle':
					continue
				elif msg=="c" or msg=="y":
					self.pladdr.append(addr)
					if self.players==0:
						print('Player 1 connected!')
# 						self.send('p1',1,'settings')
# 						self.send(("Successfully connected. Wating for other players\n"\
# 									"You are player 1 - white."),1,'info')
						self.players+=1
					elif self.players==1:
						print('Player2 connected!')
# 						self.send('p2',2,'settings')
# 						self.send(("Successfully connected. You are player 2 - black.\n"\
# 									"Wait for player 1 to set up the game"),2,'info')
						self.players+=1
# 						self.send('gamesetup',1,'settings')
# 						self.send(("Do you want to start a new game or load previously"\
# 									" saved?"),1,'info')
			
# 			while self.gamestate!="running":
# 				msg,addr,dtype=self.receive()
# 				if dtype=="pickle":
# 					continue
# 				elif msg=="newgame":
# 					board,komi,turn=goban.size,goban.komi,goban.turn
# 					self.send((('board'+str(board)),('komi'+str(komi)),\
# 	 							'turn'+str(turn)), (1,2),'settings')
# 					self.send('startnewgame',(1,2),'settings')
# 					self.gamestate="running"
# 				elif msg=="loadgame":
# 					self.gamestate="running"
# 					self.send('startnewgame',(1,2),'settings')
# 					self.send('sendsave',1,'settings')
			self.gamestate='running'
			self.running()
												
		except KeyboardInterrupt:
			print("Shutting down")
			self.listener.sendto('syshaltabortabort'.encode(enc),(self.listenerip,9009))
			
				
		pass		

	def running(self):
		print("started")
		try:		
			while self.gamestate=="running":
				msg,addr,dtype=self.receive()
				recind=self.pladdr.index(addr)+1
				sndind=list(range(1,self.players+1))
				sndind.remove(recind)
				if dtype=='pickle':
					data=pickle.loads(msg)
					self.send(data[2],sndind,'pckl',header=data[1])
				if dtype=="chat":
					self.send(msg,sndind,'chat')
				if dtype=="movement":
					self.send(msg,sndind,'move')
				if dtype=="settings":
					self.send("serv"+msg,list(range(1,self.players+1)),'settings')
				if dtype=='confirmation':
					self.send(msg,sndind,'confirmation')
				if dtype=='confirmation approval':
					print("Confirmation approved")
					print("---------------------")

		except KeyboardInterrupt:
			print("Shutting down")
			self.listener.sendto('syshaltabortabort'.encode(enc),(self.listenerip,9009))

if __name__ == "__main__":
	serv = GameServer()
	serv.start()