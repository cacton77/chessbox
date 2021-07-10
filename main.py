#main.py

from kivy.app import App
from kivy.config import Config
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.uix.carousel import Carousel
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.graphics import Color, Rectangle
from chess import Board
from chessbox import Chessbox

#Builder.load_file('chessbox.kv')

class LoginInput(TextInput):
	def __init__(self, **kwargs):
		super(LoginInput, self).__init__(**kwargs)

class HomeScreenButton(Button):
	def __init__(self, **kwargs):
		super(HomeScreenButton, self).__init__(**kwargs)

class BottomButtons(Widget):
	def __init__(self, **kwargs):
		super(BottomButtons, self).__init__(**kwargs)

class Square(Button):
	def __init__(self, **kwargs):
		super(Square, self).__init__(**kwargs)

class BoardGrid(GridLayout):
	def __init__(self, **kwargs):
		super(BoardGrid, self).__init__(**kwargs)

	def write(self, board_string : str, font_size : int):
		colors = "wbwbwbwbbwbwbwbwwbwbwbwbbwbwbwbwwbwbwbwbbwbwbwbwwbwbwbwbbwbwbwbw"
		for i in range(len(board_string)):
			piece = board_string[i]
			if colors[i] == 'w':
				color = (0.4, 0.6, 0.9, 1)
			else:
				color = (0.1, 0.1, 0.4, 1)
			if piece == "X":
				piece = " "
			square = Square(text=piece, font_name='DejaVuSans', font_size=font_size, background_normal = '', background_color=color)
			self.add_widget(square)

class GameCarouselButton(Button):
	def __init__(self, **kwargs):
		super(GameCarouselButton, self).__init__(**kwargs)

	def write(self, board_string : str, p1vp2 : str, url : str):
		self.ids['board_grid'].write(board_string, font_size = 15)
		self.ids['p1vp2'].text = p1vp2
		self.url = url

	def press(self):
		return self.url

class GameCarousel(Carousel):
	def __init__(self, **kwargs):
		super(GameCarousel, self).__init__(**kwargs)		

	def load(self, game_dict):
		self.fens = game_dict['fen']
		self.p1vp2s = game_dict['wvb']
		self.urls = game_dict['url']
		for i in range(0, len(self.p1vp2s)):
			board = Board(self.fens[i])
			board_string = board.unicode(invert_color = True, empty_square = "X").replace("\n", "").replace(" ", "")
			p1vp2 = self.p1vp2s[i]
			url = self.urls[i]
			button = GameCarouselButton()
			button.write(board_string, p1vp2, url)
			self.add_widget(button)

class GameBoard(Widget):
	def __init__(self, **kwargs):
		super(GameBoard, self).__init__(**kwargs)
		self.board = Board("rnbqkbnr/ppppppp1/7p/1p1p1p1p/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
		self.strboard = self.board.unicode(invert_color = True, empty_square = "   ")
		#self.label = Label(text=ascii(self.strboard))
		self.label = Label(text=self.strboard)
		self.label.font_name = 'DejaVuSans'
		self.label.font_size = 20
		self.board_background = Image(source='images/chessboard.jpg')
		#self.add_widget(self.board_background)
		self.add_widget(self.label)


class LoginScreen(Screen):
	def __init__(self, chessbox : Chessbox(), **kwargs):
		super(LoginScreen, self).__init__(**kwargs)
		self.chessbox = chessbox

	def login_press(self):
		if self.username.text == "":
			self.username.hint_text = "enter username"
			self.username.hint_text_color = [170/255.0, 38/255.0, 38/255.0, 0.75]
			return
		else:
			self.username.hint_text = "username"
			self.username.hint_text_color = [0.5, 0.5, 0.5, 1.0]
		if self.password.text == "":
			self.password.hint_text = "enter password"
			self.password.hint_text_color = [170/255.0, 38/255.0, 38/255.0, 0.75]
			return
		else:
			self.password.hint_text = "password"
			self.password.hint_text_color = [0.5, 0.5, 0.5, 1.0]

		if (self.check_valid_username(self.username.text) == False or 
		    self.check_valid_password(self.password.text) == False):
			print("Bad bad user info!")
		else:
			self.chessbox.login(self.username.text, self.password.text)
		self.chessbox.save_user()
		self.manager.current = "home"

	def press(self):
		print(self.chessbox.user_data)

	def check_valid_username(self, username : str):
		"""
		Implement later
		"""
		return True

	def check_valid_password(self, password : str):
		"""
		Implement later
		"""
		return True

class HomeScreen(Screen):
	def __init__(self, chessbox : Chessbox(), **kwargs):
		super(HomeScreen, self).__init__(**kwargs)
		self.chessbox = chessbox		

	def accept(self):
		pass

	def cancel(self):
		pass

	def press(self):
		print("Under construction.")

	def logout_press(self):
		self.chessbox.logout()
		self.manager.current = "login"

class LoadScreen(Screen):
	def __init__(self, chessbox : Chessbox(), **kwargs):
		super(LoadScreen, self).__init__(**kwargs)
		self.chessbox = chessbox

	def on_pre_enter(self):
		games = self.chessbox.player_1.get_games_wb_url()
		self.ids['game_carousel'].load(games)

	def accept(self):
		pass

	def cancel(self):
		pass

	def load_game(self, thing : str):
		url = self.ids['game_carousel'].current_slide.press()
		self.chessbox.load_game_by_url(url)
		self.chessbox.save()
		self.manager.current = "game"

class GameScreen(Screen):
	def __init__(self, chessbox : Chessbox(), **kwargs):
		super(GameScreen, self).__init__(**kwargs)
		self.chessbox = chessbox

	def on_pre_enter(self):
		board_string = self.chessbox.game.board.unicode(invert_color = True, empty_square = "X").replace("\n", "").replace(" ", "")
		self.ids['board_grid'].write(board_string, font_size = 20)

	def update(self):
		pass
		

class ChessboxApp(App):
	def build(self):
		Config.set('graphics', 'resizable', '0')
		Config.set('graphics', 'width', '320')
		Config.set('graphics', 'height', '240')
		sm = ScreenManager()
		self.chessbox = Chessbox()
		user_loaded = self.chessbox.startup()
		if user_loaded == True:
			sm.add_widget(HomeScreen(self.chessbox, name='home'))
			sm.add_widget(LoginScreen(self.chessbox, name='login'))
		else:
			sm.add_widget(LoginScreen(self.chessbox, name='login'))
			sm.add_widget(HomeScreen(self.chessbox, name='home'))
		sm.add_widget(LoadScreen(self.chessbox, name='load'))
		sm.add_widget(GameScreen(self.chessbox, name='game'))
		return sm

		"""

				root.manager.transition.direction = 'down'
            	root.manager.current = 'home'
		"""

if __name__ == '__main__':
	ChessboxApp().run()