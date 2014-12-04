#!/usr/bin/env python3

'''
Kamiken Asyncio Server 0.1.0
'''

import asyncio
import numpy as np
from string import ascii_letters, digits

class GameServer(object):
	"""
	Основной сервер-ретранслятор и обработчик соединений.
	Вкратце: получает сообщение через asyncio.Protocol, отправляет его на разделочную
	доску, где сообщение делится на 4 группы: заголовок, айди игрока, айди игры.
	В зависимости от заголовка затем выполняются различные действия.
	Благодаря введению айди игрока/игры, возможен реконнект!
	Подробнее в каждой из функций.
	
	'''
	self.future — для отложенных/затратных комманд, асинхронность.
	self.connections — количество подключенных игроков.
	self.connected — словарь подлюкченных людей. {player_id: (ip,port)}
	self.running_games — количество идущих игр
	self.games — словарь игр. {game_id: [player1_id, player2_id]}
	self.lobby — словарь созданных, но не начатых игр. {game_id: player_id}
	self.ntwtransport — сетевой транспорт, сокет.
	self.ntwserver — сетевой сервер.
	'''
	"""
	def __init__(self):
		self.future = asyncio.Future()
		self.connections = 0
		self.connected = {}
		self.running_games = 0
		self.lobby = {}
		self.games = {}

	def start(self,transport,ntwserver):
		"""
		Сюда просто передаются транспорт, чтобы отправлять сообщения,
		и сам сетевой сервер, на всякий случай.
		"""
		self.ntwtransport = transport
		self.ntwserver = ntwserver
	
	def send(self,data,header,type,player_id,pickle=False):
		"""
		Стандартная функция отправки сообщений. Из заголовка берутся четыре первых 
		символа (для понятного написания, например, self.send(data,'connection',...)),
		ставятся подчёркивание вокруг, добавляется тип данных (подгруппа, как бы),
		и сами данные, конечно. Затем это всё отправляется по адресу.
		Пока что pickle не используется, но при загрузке/реконнекте будет.
		"""
		addr = self.connected[player_id]
		if not pickle:
			header = "__"+header[0:4]+"__"
			msg = header+type+data
			msg = msg.encode()
			self.ntwtransport.sendto(msg,addr)
	
	def split_data(self,data):
		"""
		Делит данные на 4 части.
		8 байт отводятся на главный заголовок, по 4 на айди игрока/игры.
		В exception'ы потом будут вписаны диагностирующе функции, возможно.
		"""
		header = None
		gamekey = None
		player_id = None
		rdata = None
		
		try:
			header = data[0:8].decode()
		except:
			pass
		try:
			player_id = data[8:12].decode()
		except:
			pass
		try:
			gamekey = data[12:16].decode()
		except:
			pass
		try:
			rdata = data[16:].decode()
		except:
			pass
		
		return header, player_id, gamekey, rdata

	def generate_id(self,type):
		"""
		Генерирует уникальный четырёхсимвольный айди для игрока или игры.
		"""
		symbols = ascii_letters+digits
		while True:
			idlist = np.random.choice(list(symbols),4,replace=True)
			id = "".join(idlist)
			if type == "player":
				if id not in self.connected:
					break
			if type == "game":
				if id not in self.games:
					break
		print(id)
		return id

	def message_classifier(self,data,addr):
		"""
		Классификатор сообщений. В зависимости от заголовка делает разные действия.
		manage_lobby и manage_games вызываются только в случае нахождения
		игрока/игры в списке подключённых/созданных игр, во избежание KeyError'ов.
		"""
		header, player_id, gamekey, data = self.split_data(data)
		if header == None or data == None: return
		
		if header == "__conn__":
			self.manage_connections(data,player_id,addr)
		elif header == "__lbby__":
			if player_id in self.connected:
				self.manage_lobby(data,player_id,gamekey)
		elif header == "__game__":
			if player_id in self.connected and gamekey in self.games:
				self.manage_games(data,player_id,gamekey)
	
	def manage_connections(self,data,player_id,addr):
		"""
		Обработчик подключений. 
		Изначально в клиенте стоит id игрока p489
		Если текст сообщений "connect" и присланный id p489, то проверяет, не находится
		ли уже этот адрес в списке подключённых. Если находится — высылает ему его айди.
		Если нет, то генерируется айди игрока и высылается.
		Если пришло "disconnect", то id/ip удаляются из словаря подключений.
		
		TODO:
			добавить проверку на совпадение id/ip в словаре подключений на случай, 
			если в середине игры сменится порт/айпи.		
		"""
		if data == "connect" and addr in self.connected.values():
			for key, value in self.connected.items():
				if value == addr:
					self.send(key,'connection','plid',key)
		elif data == "connect" and player_id == "p489":
			self.connections += 1
			new_id = self.generate_id("player")
			self.connected[new_id] = addr
			self.send(new_id,'connection','plid',new_id)
		if data == "disconnect" and player_id in self.connected:
			self.connections -= 1
			self.connected.pop(player_id,None)
	
	def manage_lobby(self,data,player_id,gamekey):
		"""
		Лобби. Можно получить список созданных игр, создать игру, подключиться
		или закончить.
		При подключении второго игрока игра переносится из self.lobby в self.games.
		
		TODO:
			Невозможность подключиться (вторым игроком) к своей же игре.
			Удаление игры из списка при выходе игрока (в manage_connections)
			Подтверждение второго игрока перед началом игры при подклчении (если
			пропало подключение, например).
		"""
		if data == "getgames":
			self.send(" ".join(self.lobby.keys()),'lbby','glst',player_id)
		if data == "creategame":
			gamekey = self.generate_id("game")
			self.send(gamekey,'lbby','gmcr',player_id)
			self.lobby[gamekey]=[player_id]
		if data == "joingame":
			self.lobby[gamekey].append(player_id)
			self.games[gamekey] = self.lobby[gamekey].copy()
			for player in self.games[gamekey]:
				self.send('gamestart','lbby','game',player)
			self.lobby.pop(gamekey,None)
			self.running_games += 1
			print(self.games)
		if data == "stopgame":
			for player in self.games[gamekey]:
				self.send('gamestop','lbby','game',player)
			self.games.pop(gamekey,None)
			self.running_games -= 1
	
	def manage_games(self,data,player_id,gamekey):
		"""
		Первые 4 символа — тип действия (move, skip, rsrt [restart]).
		Остальные данные будут либо (p1,x,y) в случае move, либо просто номер игрока.
		По ключу игры получает айди игроков, убирает из списка себя, и отправляет
		второму игроку. 
		Затем высылает подтверждение, что ход был обработан (при неполучении
		этого в течение какого-то промежутка времени в клиенте будет убран
		последний поставленный камень). !ОТКЛЮЧЕНО!
		4 разных значений данных, при которых функция завершается — заготовка на 
		будущее. Три из них очевидны.
		verify — Проверка соответствия доски между игроками. Если доски разные,
		то будет заружена та, которая была у второго игрока, а не того, кто вызвал
		команду проверки.
		"""
		if data == "restart": return
		if data == "verify": return
		if data == "load": return
		if data == "save": return
		try:
			type = data[0:4]
			data = data[4:]
		except:
			return
		print(self.games[gamekey])
		players = self.games[gamekey].copy()
		print(players)
		players.remove(player_id)
		print(players)
		recipient = players[0]
		print(recipient)
		self.send(data,'game',type,recipient)
# 		self.send('ok','game',type,player_id)
		return

class NetworkServer:
	"""
	Сам сетевой сервер. Получает сообщений, отправляет его в классификатор.
	"""
	def __init__(self, server):
		self.server = server
		
	def connection_made(self, transport):
		self.transport = transport
		self.server.start(self.transport,self)

	def datagram_received(self, data, addr):
		message = data.decode()
		print('Received %r from %s' % (message, addr))
		self.server.message_classifier(data,addr)

if __name__ == "__main__":
	loop = asyncio.get_event_loop()
	print("Starting Kamiken UDP Server")
	game_server = GameServer()
	network_server = NetworkServer(game_server)
	
	listen = loop.create_datagram_endpoint(lambda:network_server, local_addr=('0.0.0.0', 9010))
	transport, protocol = loop.run_until_complete(listen)
	
	try:
		loop.run_forever()
	except KeyboardInterrupt:
		pass
	
	transport.close()
	loop.close()