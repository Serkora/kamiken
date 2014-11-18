#!/Library/Frameworks/Python.framework/Versions/3.4/bin/python3.4
# -*- coding: UTF-8 -*-

import kamiken_0_1_0 as kamiken
from kamiken_0_1_0 import WINDOW_W, WINDOW_H, BOARD_W, BOARD_H, \
									MSG, TILE_SIZE, FONT, ALL_STONES#, PLAYER
from CLIENT import Client
from SERVER import GameServer
from sys import argv
from pyglet.app import run


# Пока вручную будем тут изменять.
#if argv[1]=="-p1": PLAYER = 1.0
#if argv[1]=="-p2": PLAYER = 2.0
PLAYER = 1.0

if __name__ == "__main__":
	window = kamiken.Board(WINDOW_W, WINDOW_H, BOARD_W, BOARD_H, MSG, TILE_SIZE,
					FONT, ALL_STONES, PLAYER)
	client = Client(window)
	def on_reqconnect():
		client.send('c','sett')
	def on_mademove(x1,y1):
		client.send((x1,y1),'move')
	window.on_mademove = on_mademove
	window.on_reqconnect = on_reqconnect
	run()	