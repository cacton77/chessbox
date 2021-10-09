#chessbox.py

import re
import time
import json
import chess
from chess import Board
from chessdotcom import ( 
	get_player_profile,
	is_player_online,
	get_player_current_games,
	get_player_current_games_to_move
)
import chessbox_states as cs


class Chessbox:

	def __init__(self):
		"""
		Initiates Chessbox by looking for user data in user_data.json
		If data isn't found the user is prompted for inputs.
		"""
		self.user_data = {}
		self.player_1 = None
		self.player_2 = None
		self.game = NullGame()
		self.state = cs.Startup()

	def startup(self):
		with open('user_data.json') as f:
			self.user_data = json.load(f)
		if not self.user_data["p1"]:
			return False
		else:
			self.player_1 = User(self.user_data["p1"], self.user_data["p1_password"])
			return True

	def login(self, username : str, password : str):
		self.user_data["p1"] = username
		self.user_data["p1_password"] = password
		self.player_1 = User(self.user_data["p1"], self.user_data["p1_password"])

	def logout(self):
		self.user_data["p1"] = ""
		self.user_data["p1_password"] = ""
		self.user_data["curr_game_url"] = ""
		self.save_user()

	def load_game_by_url(self, url : str):
		game = self.player_1.get_game_by_url(url)
		white_str = game["white"]
		black_str = game["black"]
		player_white = white_str[33:len(white_str)]
		player_black = black_str[33:len(black_str)]
		if player_white == self.player_1.username:
			self.user_data["p2"] = player_black
		else:
			self.user_data["p2"] = player_white
		self.user_data["curr_game_url"] = game["url"]
		self.user_data["round"] = 1
		self.user_data["turn"] = 'w'
		self.user_data["fen"] = ""
		self.game = Game(self.player_1, self.player_2, self.user_data["curr_game_url"], self.user_data["round"], self.user_data["turn"], self.user_data["fen"])

	def load_game(self):
		"""
		Loads a saved game.
		"""
		while True:
			if not self.user_data["curr_game_url"]:
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
							self.user_data["p2"] = player_black
						else:
							self.user_data["p2"] = player_white
						self.user_data["curr_game_url"] = games_wb_url['url'][index]
						self.user_data["round"] = 1
						self.user_data["turn"] = 'w'
						self.user_data["fen"] = ""
						break
					else:
						print("Select one of the above games.")
						continue
				"""
				Ask for p2 login.
				"""
				while True:
					yn = input(self.user_data["p2"] + " playing on same board? [y/n]: ")
					if yn == 'y':
						password = input("password: ")
						if self.check_valid_password(password) == False:
							print("Incorrect password.")
							continue
						self.user_data["p2_password"] = password
						break
					elif yn == 'n':
						password = ""
						self.user_data["p2_password"] = password
						break
					else:
						continue
				break
			else:
				"""
				If game is saved, ask if player wants to continue the game.
				"""
				print(self.player_1.get_game_wb_by_url(self.user_data["curr_game_url"]))
				yn = input("Continue game? [y/n]: ")
				if yn == 'y':
					break
				elif yn == 'n':
					self.user_data["curr_game_url"] = ""
					continue
				else:
					continue

		self.player_2 = User(self.user_data["p2"], self.user_data["p2_password"])

		self.state = cs.GameLoaded()

		self.game = Game(self.player_1, self.player_2, self.user_data["curr_game_url"], self.user_data["round"], self.user_data["turn"], self.user_data["fen"])
		self.save()
		print()
		print(self.game.url)
		print()
		print(self.game)
		print()

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

	def save_user(self):
		with open('user_data.json', 'w') as f:
			json.dump(self.user_data, f)

	def save(self):
		self.user_data["round"] = self.game.round.round
		self.user_data["turn"] = self.game.round.turn
		self.user_data["fen"] = self.game.round.fen
		with open('user_data.json', 'w') as f:
			json.dump(self.user_data, f)

	def exit(self):
		self.save()
		print("shutting down...")
		exit()


class User:

	def __init__(self, username : str, password : str):
		
		self.username = username
		self.password = password

	def get_games_wb_url(self):
		"""
		Returns dict of arrays including.
			games_w: list of white players
			games_b: list of black players
			games_url: list of urls
			games_wvb: list of strings in format "player_1 playing w/b against player_2"
			games_fen: list of current fen
		"""
		games = self.get_current_games_list()
		games_w = []
		games_b = []
		games_url = []
		games_wvb = []
		games_fen = []
		index = 0
		for game in games:
			white_str = game["white"]
			black_str = game["black"]
			player_white = white_str[33:len(white_str)]
			player_black = black_str[33:len(black_str)]
			if player_white == self.username:
				wvb = "Playing white against " + player_black + "."
			else:
				wvb = "Playing black against " + player_white + "."
			games_w.append(player_white)
			games_b.append(player_black)
			games_url.append(game["url"])
			games_wvb.append(wvb)
			games_fen.append(game["fen"])
		games_wb_url = {'w': games_w, 'b': games_b, 'url': games_url, 'wvb': games_wvb, 'fen': games_fen}
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
				player_black = games_b[i]
				if player_white == self.username:
					game_wb = "Playing white against " + player_black + "."
				else:
					game_wb = "Playing black against " + player_white + "."
				return game_wb
		return "error with get_game_wb_by_url()!"

	def print_games_wb(self):
		"""
		Prints list of games as strings with players associated with colors.
		"""
		print("Loading games...")
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

class Round:

	def __init__(self, round_ : int, turn : str, fen : str):
		self.round = round_
		self.turn = turn
		self.fen = fen

	def get_round(self):
		return self.round

	def get_turn(self):
		return self.turn

	def get_fen(self):
		return self.fen

	def __str__(self) -> str:
		return str(self.round) + self.turn + ") " + self.fen

class Game:

	def __init__(self, player_1 : User, player_2 : User, url : str, round_ : int, turn : str, fen : str):

		self.player_1 = player_1
		self.player_2 = player_2
		self.url = url
		if round_ == 1 and turn == 'w':
			fen = self.get_starting_fen()
		self.round = Round(round_, turn, fen)
		self.board = Board(fen)		

	def update(self):
		game_data = self.get_game_data()
		last_round = self.round
		curr_fen = self.get_current_fen()
		if curr_fen != last_round.fen:
			curr_round = self.get_round(curr_fen)
			curr_turn = self.get_turn(curr_fen)
			curr_round = Round(curr_round, curr_turn, curr_fen)
			moves_rounds_turns = self.get_moves(last_round, curr_round)
			rounds_turns = moves_rounds_turns["rounds_turns"]
			moves = moves_rounds_turns["moves"]
			for i in range(0, len(moves)):
				round_turn = rounds_turns[i]
				move = moves[i]
				print(round_turn + str(self.board.parse_san(move)))
				self.board.push(self.board.parse_san(move))
				print(self.board.unicode(invert_color = True, empty_square = "  "))
				input()
			self.round = curr_round
			self.save()

	def get_game_data(self):
		return self.player_1.get_game_by_url(self.url)

	def get_round(self, fen: str):
		result = re.search("\d*$", fen)
		round_ = result.group()
		return int(round_)

	def get_turn(self, fen : str):
		result = re.search("(?<=\s)[wb]{1}(?=\s)", fen)
		turn = result.group()
		return turn

	def get_starting_fen(self):
		game_data = self.get_game_data()
		result = re.search("(?<=\[FEN\s\").*(?=\")", game_data["pgn"])
		if result is None:
			fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
		else:
			fen = result.group()
		return fen

	def get_current_fen(self):
		game_data = self.get_game_data()
		result = re.search("(?<=CurrentPosition\s\").*(?=\")", game_data["pgn"])
		fen = result.group()
		return fen

	def get_moves(self, round_i : Round, round_o : Round):
		game_data = self.get_game_data()
		rounds_turns = []
		moves = []
		result = re.search("(?<=\n\n).*", game_data["pgn"])
		move_string = result.group()
		#print(move_string)
		round_i_num = round_i.round
		round_i_turn = round_i.turn
		round_o_num = round_o.round
		round_o_turn = round_o.turn
		turn = round_i_turn
		for r in range(round_i_num, round_o_num + 1):
			if r == round_o_num and round_o_turn == 'w':
					return {"rounds_turns": rounds_turns, "moves": moves}
			if turn == 'w':
				rounds_turns.append(str(r) + turn + ". ")
				move = self.get_move(r, 'w', move_string)
				moves.append(move)
				turn = 'b'
			if r == round_o_num and round_o_turn == 'b':
				return {"rounds_turns": rounds_turns, "moves": moves}
			if turn == 'b':
				rounds_turns.append(str(r) + turn + ". ")
				move = self.get_move(r, 'b', move_string)
				moves.append(move)
				turn = 'w'

	def get_move(self, round_ : int, turn : str, move_string : str):
		if round_ == 1:
			if turn == 'w':
				round_ = str(round_) + "\."
			elif turn == 'b':
				round_ = str(round_) + "\.\.\."
		else:
			if turn == 'w':
				round_ = "\s" + str(round_) + "\."
			elif turn == 'b':
				round_ = "\s" + str(round_) + "\.\.\."
		result = re.search("(?<=" + round_ + "\s)\S*", move_string)
		move = result.group()
		return move

	def print_pgn(self):
		game = self.player_1.get_game_by_url(self.url)
		print(game["pgn"])

	def is_opponent_online(self):
		return is_player_online(self.player_2)

	def is_move_ready(self):
		games_to_move = self.get_current_games_to_move_list()
		for game in games_to_move:
			if game["url"] == self.url:
				return True
		return False

	def save(self):
		with open('user_data.json') as f:
			user_data = json.load(f)

		user_data['round'] = self.round.round
		user_data['turn'] = self.round.turn
		user_data['fen'] = self.round.fen

		with open('user_data.json', 'w') as f:
				json.dump(user_data, f)

	def __str__(self) -> str:
		return self.board.unicode(invert_color = True, empty_square = "  ")

class NullRound(Round):

	def __init__(self):
		self.round = 0
		self.turn = ""
		self.fen = ""

class NullGame(Game):

	def __init__(self):
		self.round = NullRound()
