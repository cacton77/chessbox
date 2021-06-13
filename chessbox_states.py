#chessbox_states.py

from state import State

class Startup(State):

	def on_event(self, event):
		if event == 'WaitForOpponentMove':
			return WaitForOpponentMove()
		elif event == 'MoveReady':
			return MoveReady()

class WaitForOpponentMove(State):

	def on_event(self, event):
		if event == 'opponent_move_executed':
			return MoveReady()

class MoveReady(State):

	def on_event(self, event):
		if event == 'move_executed':
			return WaitForOpponentMove()