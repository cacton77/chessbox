#chessbox_states.py

from state import State

class Startup(State):

	def on_event(self, event):
		if event == 'WaitForOpponentMove':
			return WaitForOpponentMove()
		elif event == 'MoveReady':
			return MoveReady()

class LogIn(State):

	def on_event(self, event):
		pass

class MainMenu(State):

	def on_event(self, event):
		if event == 'load_game':
			return LoadGame()
		elif event == 'get_user_data':
			return GetUserData()
		elif event == 'sign_out':
			return LogIn()
		elif event == 'exit':
			return Exit()
		else:
			return MainMenu()

class LoadGame(State):

	def on_event(self, event):
		pass

class GameLoaded(State):

	def on_event(self, event):
		pass

class Idle(State):

	def on_event(self, event):
		pass

class GetUserData(State):

	def on_event(self, event):
		pass

class WaitForOpponentMove(State):

	def on_event(self, event):
		if event == 'opponent_move_executed':
			return MoveReady()

class MoveReady(State):

	def on_event(self, event):
		if event == 'move_executed':
			return WaitForOpponentMove()

class Exit(State):
	
	def on_event(self, event):
		pass