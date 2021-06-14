#testbox.py

from chessbox import Chessbox
import chess

ql_box = Chessbox()

board = chess.Board(ql_box.fen)
print(board)