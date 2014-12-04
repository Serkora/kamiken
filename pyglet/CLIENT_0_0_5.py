#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

'''
KAMIKEN Network Client Version 0.0.5
'''

import socket
import time
from threading import Thread
from random import randint
from configparser import ConfigParser
from pyglet.window import key
from pyglet import clock

config = ConfigParser()
config.readfp(open("config.ini"))

serverip = config.get('network','serverip')
serverport = int(config.get('network','serverport'))
#serverip = '127.0.0.1'
#myip = '127.0.0.1'
myip = '0.0.0.0'
myport = randint(8000,9000)
enc = 'utf-8'

class Client(object):
	def __init__(self,game):
		self.serverip = serverip
		self.serverport = serverport
		self.myip = myip
		self.myport = myport
		self.conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.conn.bind((self.myip, self.myport))
		self.game = game
		self.lastsentmsg = ""							# last sent message
		self.lastrecmsg = ""							# last received message
		global ThrListen								# make it global to force-stop
		ThrListen=Thread(target=self.nw_listen,args=())	# create a network listener thread
		ThrListen.setDaemon(True)
		ThrListen.start()

	def nw_listen(self):						# network listener
		while True:								# infinite loop
			self.receive()						# waits for message		

	def send(self,items,dtype):
		"""
		Ensures that only 1 copy of the message is printed in console.
		"""
		if items == self.lastsentmsg:
			dest=(self.serverip,self.serverport)	# set the destination. Currently		
			dtype="__"+dtype[0:4].upper()+"__"		# add dtype header to message
			self.conn.sendto((dtype+str(items)).encode(enc),dest)
		
		else:
			print("Client is trying to send")
			dest=(self.serverip,self.serverport)	# set the destination. Currently		
			dtype="__"+dtype[0:4].upper()+"__"		# add dtype header to message
		
			print('"',items,'"')
			self.conn.sendto((dtype+str(items)).encode(enc),dest)
			print("-----------")
			self.lastsentmsg = items
	
	def receive(self,size=512):	
		""" 
		Only does something if the received message is different from the last one. 
		May be needed to be reworked in future if transmission of identical
		messages can happen for reasons other than redundancy.
		"""
		msg,addr=self.conn.recvfrom(size)	# receive first datagram
		if msg == self.lastrecmsg: return
		self.lastrecmsg = msg
		print("Client received")			# verbose output 	
		print(msg)							
		print('received text')
		print("-----------")
		data = msg.decode(enc)[9:-1]
		if data[0] in "012":
			player = int(data.split(",")[0])
			x = int(data.split(",")[1])
			y = int(data.split(",")[2])
			clock.schedule_once(lambda _: self.game.dispatch_event(
								'on_movereceive',self.game,player,x,y), 0.1
			)