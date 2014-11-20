#!/Library/Frameworks/Python.framework/Versions/3.4/bin/python3.4
# -*- coding: UTF-8 -*-

"""
Из kamiken_0_1_3 импортируются все необходимые кнстанты. В принципе, можно их и
сюда вынести, особенно BOARD_H/W, чтобы сделать доску изменяемой. А WINDOW_H/W,
в принципе, зависят от размера доски, так что тоже сюда перейдут.
pyglet.app.run тоже нужно импортировать в ланчере, так как иначе он не знает этой команды.
"""

from kamiken_0_1_4 import Board, BOARD_W, BOARD_H, MSG, TILE_SIZE, FONT

from CLIENT_0_0_3 import Client
from SERVER_0_0_3 import GameServer
from pyglet.app import run

if __name__ == "__main__":
	window = Board(BOARD_W, BOARD_H, MSG, TILE_SIZE, FONT)
	client = Client(window)
	def on_reqconnect():
		client.send('c','sett')
	def on_mademove(player,x1,y1):
		client.send((player,x1,y1),'move')
	window.on_mademove = on_mademove
	window.on_reqconnect = on_reqconnect
	run()	
	client.send('disconnect','connection')