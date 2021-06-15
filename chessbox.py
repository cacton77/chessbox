#chessbox.py

import re
import json
import chess
from chess import Board
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

		while True:
			if not user_data["p1"]:
				"""
				If primary user isn't saved, ask for login.
				"""
				self.chessbox_welcome()
				print("Please enter chess.com user information:")
				username = input("username: ")
				while self.check_valid_username(username) == False:
					print("Invalid username.")
					username = input("username: ")

				password = input("password: ")
				while self.check_valid_password(password) == False:
					print("Incorrect password.")
					username = input("password: ")

				user_data["p1"] = username
				user_data["p1_password"] = password
				self.save_state(user_data)
				break
			else:
				"""
				If primary user is saved, ask if player would like to play as this user.
				"""
				yn = input("Play as " + user_data["p1"] + "? [y/n]: ") 
				if yn == 'y':
					break
				elif yn == 'n':
					user_data["p1"] = ""
					user_data["p1_password"] = ""
					user_data["p2"] = ""
					user_data["p2_password"] = ""
					user_data["curr_game"] = ""
					continue
				else:
					continue

		self.player_1 = User(user_data["p1"], user_data["p1_password"])

		while True:
			if not user_data["curr_game_url"]:
				"""
				If game isn't saved, select game and save p2 username.
				"""
				games_wb_url = self.player_1.print_games_wb()
				while True:
					try:
						index = int(input("Please select a game by its index: "))
					except ValueError:
						print("Select one of the above games.")
						continue
					if index < len(games_wb_url['w']):
						player_white = games_wb_url['w'][index]
						player_black = games_wb_url['b'][index]
						if player_white == self.player_1.username:
							user_data["p2"] = player_black
						else:
							user_data["p2"] = player_white
						user_data["curr_game_url"] = games_wb_url['url'][index]
						user_data["fen"] = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
						break
					else:
						print("Select one of the above games.")
						continue
				"""
				Ask for p2 login.
				"""
				while True:
					yn = input(user_data["p2"] + " playing on same board? [y/n]: ")
					if yn == 'y':
						password = input("password: ")
						if self.check_valid_password(password) == False:
							print("Incorrect password.")
							continue
						user_data["p2_password"] = password
						break
					elif yn == 'n':
						password = ""
						user_data["p2_password"] = password
						break
					else:
						continue
				self.save_state(user_data)
				break
			else:
				"""
				If game is saved, ask if player wants to continue the game.
				"""
				print(self.player_1.get_game_wb_by_url(user_data["curr_game_url"]))
				yn = input("Continue game? [y/n]: ")
				if yn == 'y':
					break
				elif yn == 'n':
					user_data["curr_game_url"] = ""
					continue
				else:
					continue

		self.player_2 = User(user_data["p2"], user_data["p2_password"])

		self.game = Game(self.player_1, self.player_2, user_data["curr_game_url"], user_data["fen"])


	def chessbox_welcome(self):
		"""
		Welcome screen for chessbox
		"""
		print("Welcome to chessbox live!")

	def check_valid_username(self, username : str):
		"""
		Checks user exists. Implement later.
		"""
		return True

	def check_valid_password(self, password : str):
		"""
		Checks password is valid. Implement later.
		"""
		return True

	def is_opponent_online(self):
		return self.game.is_opponent_online()

	def is_move_ready(self):
		return self.game.is_move_ready()

	def save_state(self):
		user_data = {"p1": self.player_1.username, 
					 "p1_password": self.player_1.password, 
					 "p2": player_2, 
					 "p2_password": player_2.password,
					 "curr_game_url": self.game.url,
					 "fen": self.game.fen}
		with open('user_data.json', 'w') as f:
				json.dump(user_data, f)

	def save_state(self, user_data : dict):
		with open('user_data.json', 'w') as f:
				json.dump(user_data, f)


class User:

	def __init__(self, username : str, password : str):
		
		self.username = username
		self.password = password

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

	def get_game_wb_by_url(self, url : str):
		games_wb_url = self.get_games_wb_url()
		games_w = games_wb_url['w']
		games_b = games_wb_url['b']
		games_url = games_wb_url['url']
		for i in range(0,len(games_url)):
			if games_url[i] == url:
				player_white = games_w[i]
				player_black = games_w[i]
				if player_white == self.username:
					game_wb = "Playing white against " + player_black + "."
				else:
					game_wb = "Playing black against " + player_white + "."
				return game_wb

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

class Game:

	def __init__(self, player_1 : User, player_2 : User, url : str, fen : str):

		self.player_1 = player_1
		self.player_2 = player_2
		self.url = url
		self.fen = self.get_fen()
		print(self.fen)

		self.board = Board(self.fen)

	def get_fen(self):
		game = self.player_1.get_game_by_url(self.url)
		result = re.search("(?<=CurrentPosition\s\").*(?=\")", game["pgn"])
		fen = result.group()
		return fen

	def is_opponent_online(self):
		return is_player_online(self.player_2)

	def is_move_ready(self):
		games = self.get_current_games_to_move_list()
		for game in games:
			if game["url"] == self.url:
				return True
		return False

	def __str__(self) -> str:
		return str(self.board)
