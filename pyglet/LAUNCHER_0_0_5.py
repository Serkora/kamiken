#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

'''
KAMIKEN Network Launcher Version 0.0.5
'''

"""
Из kamiken_0_3_0 импортируются все необходимые константы.
из Клиента/Сервера импортируются нужны классы.
pyglet.app.run тоже нужно импортировать в ланчере, так как иначе он не знает этой команды.
"""

from kamiken_0_3_0 import Board, BOARD_W, BOARD_H, WINDOW_W, WINDOW_H, MSG, TILE_SIZE, SQUARE_SIZE, FONT

from CLIENT_0_0_5 import Client
from SERVER_0_0_5 import GameServer
from pyglet import app, clock

if __name__ == "__main__":
	window = Board(BOARD_W, BOARD_H, WINDOW_W, WINDOW_H, MSG, TILE_SIZE, SQUARE_SIZE, FONT)
	client = Client(window)
	def on_reqconnect():
		client.send('connect','connection')
	def on_disconnect():
		client.send('disconnect','connection')
	def on_mademove(player,x1,y1):
		client.send((player,x1,y1),'move')
	window.on_reqconnect = on_reqconnect
	window.on_disconnect = on_disconnect
	window.on_mademove = on_mademove
	clock.schedule_interval(lambda _: None, 1/60) # 60 Hz refresh rate
	app.run()	