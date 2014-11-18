#!/Library/Frameworks/Python.framework/Versions/3.4/bin/python3.4
# -*- coding: UTF-8 -*-

import socket
import pickle
from threading import Thread
from random import randint


serverip = '54.68.244.173'
serverport = 9009
myip = '25.64.15.244'
myport = randint(8000,9000)
enc = 'utf-8'

class Client(object):
	def __init__(self,game):
		self.serverip = serverip
		self.serverport = serverport
		self.myip = myip
		self.myport = myport
		self.conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#		self.conn.bind((self.myip, self.myport))
		self.game = game
		global ThrListen								# make it global to force-stop
		ThrListen=Thread(target=self.nw_listen,args=())	# create a network listener thread
		ThrListen.setDaemon(True)
		ThrListen.start()

	def nw_listen(self):						# network listener
		self.packets=False
		while True:									# infinite loop
			if not self.packets:					
				dtype,msg=self.receive()			# waits for message		
#				self.message_classifier(dtype, msg)	# sends the message to classifier

	def send(self,items,dtype,pcklobj=False,header='',destination='server'):
		print("Client is trying to send")
		if destination=='server':
			dest=(self.serverip,self.serverport)	# set the destination. Currently
		else:										# only client<->server is possible,
			dest=destination						# but maybe in future
		
		if not pcklobj and dtype!="pickle" and dtype!="pckl" \
						and dtype!="obj" and dtype!="object":	
			dtype="__"+dtype[0:4].upper()+"__"		# add dtype header to message
		else:
			pcklobj=True							# or set pcklobj if packeted transmission
		
		if not pcklobj:
			print('"',items,'"')
			self.conn.sendto((dtype+str(items)).encode(enc),dest)	# send string
		else:														# or invoke packeted
			self.send_pickle(items, header, dest)					# transmission function
		print("-----------")
	
	def send_pickle(self, object, header, destination):
		"""
		Creates a tuple with header and two start/end positions. For every such 
		piece it then sends the data to recipient and waits for response from that
		address only. When receives confirmation, goes on to another 'packet'.
		"Break" is sort of unnecessary, since it will already be the last part
		anyway, but this loop will in future be improved to enable different
		transmission types even during this process, so 'complete' flag will
		definitely be used
		##	In theory, data can be picked with a size/number of packets placeholder,
			then have it's size calculated and pickled again with appropriate values
			that can be decoded as UTF-8 by the recipient at the establishment of
			the connection.
		"""
		self.conn.sendto('sending pickle'.encode(enc),(self.myip,self.myport))
		time.sleep(0.5)
		message=pickle.dumps(("START",header,object,'END'))
		data,addr=[],[]
		complete=False
		n=0
		for i in range(0,len(message),420):
			data.append(message[i:i+420])
		print("Sending pickled object with header",header,"and length of",n,"packets")
		while not complete:
			print("SENDING INDEX",n)
			self.conn.sendto(data[n],destination)
			while addr!=destination:						# wait for the message from the
				msg,addr=self.receive(packets=True)			# same address you are trying
				print("CLIENTRECEIVED",msg)
			if msg.decode(enc)[8:]=='next_datagram':		# to send the message to
				n+=1										# if successful — next packet
				msg,addr='',''
				print("Client received 'next_datagram'. Incremented index, cleared msg and addr")
				continue									
			elif msg.decode(enc)[8:]=='complete':
				print("COMPLETED SENDING")
				complete=True
				break
			addr=''
		self.packets=False
		print("Client Sent pickled object")		
		
	def receive(self,source='server',size=512, packets=False):		
		msg,addr=self.conn.recvfrom(size)	# receive first datagram
		data = msg.decode(enc)[9:-1]
		x = int(data.split(",")[0])
		y = int(data.split(",")[1])
		self.game.dispatch_event('on_movereceive',self.game,x,y)
		if packets: 
			print("IN PACKET MODE")
			return msg,addr					# if currently receiving packets - return
		print("Client received")			# verbose output 
		try:								
			msg.decode(enc)					# try to see if it is plain text
			print(msg)							
			print('received text')
			print("-----------")
			if msg.decode(enc)=="sending pickle":
				self.packets=True
			return 'text', msg.decode(enc)
		except:									# if not - it's a pickled object (or something
			data=self.receive_pickle(msg,addr)	# went horrendously wrong). Since it can be
			print('Client received pickle')	# large, the separate looped function is
			print("-----------")				# going to take care of the process
			return 'pickle', data
	
	def receive_pickle(self,message,address):
		"""
		"msg" argument is the first part of the data to be received (can also be last).
		Server sends the data in a more or less 512 byte chunks which are combined here.
		At every loop repetition the 'data' variable is checked if it can be depickled,
		and if not — send the message to the server to send next part which is then
		received and added to the end of all previous. This is done so that every part is
		received in the correct order to avoid the need for packet numbering.
		If the data is complete, then the corresponding message is sent to the server 
		so it can proceed with it's usual business. The received data will have four 
		messages: "start", "header/type of data", the object itself, "end". 
		##	If any one of those are missing, client will ask to repeat
			the transmission of the whole object again //not in this version, though
		## 	Since there is no way to tell what kind of data is received during this
			process, server can only accept "more"/"complete" messages from this client,
			thus not allowing other data to be transmitted between two players (e.g. chat)
			Just in a case a "if plain text" is still implemented if something goes wrong,
			but in future this can be improved to allow plain text (moves, chat, commands)
			transmission during pickle object receipt. Although, if two pickle objects
			are transmitted at once —  there is no way to tell the two apart. (Or, at
			least, not that I know of/tried.)
		## 	'pckl' dtype in sent message is currently redundant as the message classifier
			function is not invoked during this process, but may be used in future for
			improved functionality.
		##	Max number of iteration / timeout for complete message might be a good idea
			to not allow the infinite looping.
		## 	All bytes except for the first one can be actually decoded by UTF-8, so
			number of packets, size, etc can be passed in headers at specified positions
		"""
		complete=False
		data=message
#		self.conn.sendto('sending pickle'.encode(enc),(self.myip,self.myport))
		while not complete:
			try:
				print("Client trying to 'loads' data")
				pickle.loads(data)
				complete=True
				self.send('complete','pack')
			except:							
				print("Unable to 'loads', waiting for the next packet")	
				self.send('next_datagram','pack')	# self.receive is called with 
				msg,addr=self.receive(packets=True)	# 'packet' argument to always return
				data+=msg							# received message straight away
#		self.packets=False
		return data									
