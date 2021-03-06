#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

'''
KAMIKEN Network Server Version 0.0.5
'''

import socket
import re
import time

listenerip = '0.0.0.0'
enc = 'utf-8'

class GameServer(object):

	def __init__(self, port=9010):
		self.listener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.listenerip = listenerip
		print(self.listenerip)
		self.listener.bind((self.listenerip,port))
		self.shutdown=False
		self.gamestate=''
		self.players=0			# number of connected players
		self.pladdr=[]			# players IPs to distinguish between players 1 and 2
		self.settings="not set"	# to make sure all the settings are set
		self.lastsentmsg = ""
		self.lastrecmsg = ""
	
	def send(self,items,player,type):
		"""
		As with client, only prints 1 copy of sent message.
		"""
		if items == self.lastsentmsg:
			player=str(player)
			type="__"+type[0:4].upper()+"__"
			if '1' in player:
				self.listener.sendto((type+str(items)).encode(enc),self.pladdr[0])
			if '2' in player:
				self.listener.sendto((type+str(items)).encode(enc),self.pladdr[1])
		else:
			player=str(player)
			print("Server is trying to send")				
			type="__"+type[0:4].upper()+"__"
			print('"',items,'"')
			print("To player(s) ",player)
			if '1' in player:
				self.listener.sendto((type+str(items)).encode(enc),self.pladdr[0])
	
			if '2' in player:
				self.listener.sendto((type+str(items)).encode(enc),self.pladdr[1])
			print("-----------")
			self.lastsentmsg = items

	def receive(self,size=512,source='',address='yes',dtype='yes'):
		""" same as send() """
		msg,addr=self.listener.recvfrom(size)
		if msg == self.lastrecmsg:
			return msg.decode(enc)[8:], addr, self.action_classifier(msg.decode(enc))
		print("Server received")
		print("From ",addr)
		print(msg)
		print("-----------")
		self.lastrecmsg = msg
		return msg.decode(enc)[8:], addr, self.action_classifier(msg.decode(enc))
				
	def action_classifier(self,msg):
		if re.search('^__MOVE__',msg):
			return "movement"
		if re.search('^__SETT__',msg):
			return "settings"
		if re.search('^__CONN__',msg):
			return "connection"
	
	def manage_connections(self,msg,addr):
		if msg == "connect":
			self.players += 1
			self.pladdr.append(addr)
		if msg == "disconnect":
			if self.players>0:
				self.players -= 1
				self.pladdr.remove(addr)
			if self.players == 0:
				self.gamestate = ""
		elif msg=="stop":
			self.gamestate = ""
			self.players = 0
			self.pladdr = []
		elif msg=="shutdown":
			self.gamestate = ""
			self.shutdown = True

	def start(self):
		print("waiting for connections.")
		try:
			while self.players<2:
				msg,addr,dtype=self.receive()
				if msg=="connect":
					self.manage_connections(msg,addr)
			self.send((0,1,1),(1,2),'sett')		# костыли-костылики. Передаёт 3-tuple
												# чтобы клиентский receive() не ругался.
			
			self.gamestate='running'
			self.running()
												
		except KeyboardInterrupt:
			self.shutdown = True
			print("Shutting down")

	def running(self):
		print("started")
		try:		
			while self.gamestate=="running":
				msg,addr,dtype=self.receive()
				recind=self.pladdr.index(addr)+1
				sndind=list(range(1,self.players+1))
				sndind.remove(recind)
				if dtype=="movement":
					self.send(msg,sndind,'move')
				elif dtype=="connection":
					self.manage_connections(msg,addr)
					
		except KeyboardInterrupt:
			self.shutdown = True
			print("Shutting down")

if __name__ == "__main__":
	serv = GameServer()
	while not serv.shutdown:
		serv.start()
