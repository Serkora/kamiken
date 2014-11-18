#!/Library/Frameworks/Python.framework/Versions/3.4/bin/python3.4
# -*- coding: UTF-8 -*-

import socket
import time
from threading import Thread
from random import randint


#serverip = '54.68.244.173'
serverport = 9009
serverip = '127.0.0.1'
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
		while True:								# infinite loop
			self.receive()						# waits for message		

	def send(self,items,dtype):
		print("Client is trying to send")
		dest=(self.serverip,self.serverport)	# set the destination. Currently		
		dtype="__"+dtype[0:4].upper()+"__"		# add dtype header to message
		
		print('"',items,'"')
		for i in range(0,1):	# Посылает 5 раз. Сервер по 1 разу пересылает каждое из сообщений
			self.conn.sendto((dtype+str(items)).encode(enc),dest)	# send string
#			time.sleep(0.2)		# Будет зависать интерфейс. Можно отдельный тред опять...
		print("-----------")
	
	def receive(self,size=512):		
		msg,addr=self.conn.recvfrom(size)	# receive first datagram
		print("Client received")			# verbose output 	
		print(msg)							
		print('received text')
		print("-----------")
		data = msg.decode(enc)[9:-1]
		if data[0] in "012":
			player = int(data.split(",")[0])
			x = int(data.split(",")[1])
			y = int(data.split(",")[2])
			self.game.dispatch_event('on_movereceive',self.game,player,x,y)