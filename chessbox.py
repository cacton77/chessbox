#chessbox.py

import re
import json
import chess
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
		If data isn't found the user is prompted for inputs.
		"""
		self.state = Startup()

		with open('user_data.json') as f:
			user_data = json.load(f)

		if not user_data["username"]:
			print("please enter user data:")
			user_data["username"] = input("username: ")
			user_data["password"] = input("password: ")
			with open('user_data.json', 'w') as f:
				json.dump(user_data, f)

		self.username = user_data["username"]
		self.password = user_data["password"]

		if not user_data["curr_opponent"]:
			games_wb_url = self.print_games_wb()
			while True:
				try:
					index = int(input("Please select a game: "))
				except ValueError:
					print("Input a number in the above range.")
					continue
				if index < len(games_wb_url['w']):
					player_white = games_wb_url['w'][index]
					player_black = games_wb_url['b'][index]
					if player_white == self.username:
						user_data["curr_opponent"] = player_black
					else:
						user_data["curr_opponent"] = player_white
					user_data["curr_game_url"] = games_wb_url['url'][index]
					break
				else:
					print("Input a number in the above range.")
					continue
			with open('user_data.json', 'w') as f:
				json.dump(user_data, f)

		self.curr_opponent = user_data["curr_opponent"]
		self.curr_game_url = user_data["curr_game_url"]

		if not user_data["fen"]:
			game = self.get_game_by_url(self.curr_game_url)
			result = re.search("(?<=CurrentPosition\s\").*(?=\")", game["pgn"])
			user_data["fen"] = result.group()
			with open('user_data.json', 'w') as f:
				json.dump(user_data, f)

		self.fen = user_data["fen"]


	def is_opponent_online(self):
		return is_player_online(self.curr_opponent)

	def is_move_ready(self):
		games = self.get_current_games_to_move_list()
		for game in games:
			if game["url"] == self.curr_game_url:
				return True
		return False

	def get_games_wb_url(self):
		"""
		Returns list of games as strings with players associated with colors.
		"""
		games = self.get_current_games_list()
		games_w = []
		games_b = []
		games_url = []
		index = 0
		for game in games:
			white_str = game["white"]
			black_str = game["black"]
			player_white = white_str[33:len(white_str)]
			player_black = black_str[33:len(black_str)]
			games_w.append(player_white)
			games_b.append(player_black)
			games_url.append(game["url"])

		games_wb_url = {'w': games_w, 'b': games_b, 'url': games_url}
		return games_wb_url

	def get_game_by_url(self, url : str):
		games = self.get_current_games_list()
		for game in games:
			if game["url"] == url:
				return game

	def print_games_wb(self):
		"""
		Prints list of games as strings with players associated with colors.
		"""
		games_wb_url = self.get_games_wb_url()
		games_w = games_wb_url['w']
		games_b = games_wb_url['b']

		for i  in range(0,len(games_w)):
			player_white = games_w[i]
			player_black = games_b[i]
			if player_white == self.username:
				print(str(i) + ") Playing white against " + player_black + ".")
			else:
				print(str(i) + ") Playing black against " + player_white + ".")
		return games_wb_url

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
