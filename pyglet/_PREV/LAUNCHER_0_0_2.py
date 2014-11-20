#!/Library/Frameworks/Python.framework/Versions/3.4/bin/python3.4
# -*- coding: UTF-8 -*-

"""
Из kamiken_0_1_0 импортируются все необходимые кнстанты. В принципе, можно их и
сюда вынести, особенно BOARD_H/W, чтобы сделать доску изменяемой. А WINDOW_H/W,
в принципе, зависят от размера доски, так что тоже сюда перейдут.
pyglet.app.run тоже нужно импортировать в ланчере, так как иначе он не знает этой команды.
"""

from kamiken_0_1_3 import Board, WINDOW_W, WINDOW_H, BOARD_W, BOARD_H, \
									MSG, TILE_SIZE, FONT

from CLIENT_0_0_2 import Client
from SERVER_0_0_2 import GameServer
from sys import argv
from pyglet.app import run

# Пока вручную будем тут изменять.
if len(argv)>1:
	PLAYER = int(argv[1][2:])
else: PLAYER = 1.0

if len(argv)>2:
	BOARD_W = int(argv[2][1:])
	BOARD_H = BOARD_W
	WINDOW_W = (BOARD_W+2)*TILE_SIZE
	WINDOW_H = (BOARD_H+2)*TILE_SIZE

if __name__ == "__main__":
	window = Board(WINDOW_W, WINDOW_H, BOARD_W, BOARD_H, MSG, TILE_SIZE,
					FONT, PLAYER)
	client = Client(window)
	def on_reqconnect():
		client.send('c','sett')
	def on_mademove(player,x1,y1):
		client.send((player,x1,y1),'move')
	window.on_mademove = on_mademove
	window.on_reqconnect = on_reqconnect
	run()	