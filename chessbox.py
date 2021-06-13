#chessbox.py

import json
from chessdotcom import ( 
	get_player_profile,
	is_player_online,
	get_player_current_games,
	get_player_current_games_to_move
)
from chessbox_states import Startup

class Chessbox:

	def __init__(self):
		"""
		Initiates Chessbox by looking for user data in user_data.json
		"""
		self.state = Startup()

		with open('user_data.json') as f:
			user_data = json.load(f)

		if not user_data["username"]:
			print("please enter user data:")
			print("username:")
			user_data["username"] = input()
			print("password:")
			user_data["password"] = input()
			with open('user_data.json', 'w') as f:
				json.dump(user_data, f)

		self.username = user_data["username"]
		self.password = user_data["password"]

		if not user_data["curr_opponent"]:
			games_wvb = self.get_games_wvb()
			print("please select game:")
			print(games_wvb)
			while True:
				game_index = input()
				if int(game_index) <= len(games_wvb):
					return
				print("Please select index in range")

		
		self.curr_opponent = user_data["curr_opponent"]
		self.curr_game_url = user_data["curr_game_url"]

	def is_opponent_online(self):
		return is_player_online(self.curr_opponent)

	def is_move_ready(self):
		games = self.get_current_games_to_move_list()
		for game in games:
			if game["url"] == self.curr_game_url:
				return True
		return False

	def get_games_wvb(self):
		"""
		Returns list of games as strings with players associated with colors.
		"""
		games = self.get_current_games_list()
		games_wvb = []
		index = 0
		for game in games:
			white = game["white"]
			black = game["black"]
			player_white = white[33:len(white)]
			player_black = black[33:len(black)]
			if player_white == self.username:
				game_wvb = str(index) + ") Playing white against " + player_black
			else:
				game_wvb = str(index) + ") Playing black against " + player_white
			games_wvb.append(game_wvb)
			index = index + 1

		return games_wvb


	def get_current_games_list(self):
		games_dict = self.get_current_games_dict()
		return games_dict["games"]

	def get_current_games_to_move_list(self):
		games_to_move_dict = self.get_current_games_to_move_dict()
		return games_to_move_dict["games"]

	def get_current_games_dict(self):
		response = get_player_current_games(self.username)
		return response.json

	def get_current_games_to_move_dict(self):
		response = get_player_current_games_to_move(self.username)
		return response.json

	def print_current_games(self):
		games_dict = self.get_current_games_dict() 
		print(json.dumps(games_dict, indent = 4, sort_keys = True))

	def print_current_games_to_move(self):
		games_to_move_dict = self.get_current_games_to_move_dict()
		print(json.dumps(games_to_move_dict, indent = 4, sort_keys= True))
