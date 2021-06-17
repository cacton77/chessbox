#testbox.py

from chessbox import Chessbox
import chess
import time

ql_box = Chessbox()
while True:
	ql_box.game.update()
	time.sleep(1)
