#main.py

from kivy.app import App
from kivy.config import Config
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.carousel import Carousel
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty
from kivy.properties import StringProperty
from kivy.lang import Builder
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

class LoginScreen(Screen):
	text_color = (0, 0, 0, 1)
	button_color = (0.1, 0.1, 0.1, 0.5)

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
	button_text_color = (0.9, 0.9, 0.9, 1)
	button_background_color = (0.1, 0.1, 0.1, 0.8)
	button_font_size = 18

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
	button_text_color = (0.9, 0.9, 0.9, 1)
	button_background_color = (0.1, 0.1, 0.1, 0.8)
	button_font_size = 20

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
	button_text_color = (0.9, 0.9, 0.9, 1)
	button_background_color = (0.1, 0.1, 0.1, 0.8)
	button_font_size = 20

	def __init__(self, chessbox : Chessbox(), **kwargs):
		super(GameScreen, self).__init__(**kwargs)
		self.chessbox = chessbox

	def on_pre_enter(self):
		board_string = self.chessbox.game.board.unicode(invert_color = True, empty_square = "X").replace("\n", "").replace(" ", "")
		self.ids['board_grid'].write(board_string, font_size = 20)

	def on_leave(self):
		for child in [child for child in self.ids['board_grid'].children]:
			self.ids['board_grid'].remove_widget(child)

	def update(self):
		pass

class SettingsScreen(Screen):
	button_text_color = (0.9, 0.9, 0.9, 1)
	button_background_color = (0.1, 0.1, 0.1, 0.8)
	button_font_size = 20

	def __init__(self, chessbox : Chessbox(), **kwargs):
		super(SettingsScreen, self).__init__(**kwargs)
		self.chessbox = chessbox
		

class ChessboxApp(App):
	login_background_image = "images/green_background.png"
	background_image = "images/background_2.jpg"
	
	bb_text_color = (0.9, 0.9, 0.9, 1)
	bb_background_color = (0.1, 0.1, 0.1, 0.8)
	bb_font_size = 18

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
		sm.add_widget(SettingsScreen(self.chessbox, name='settings'))
		return sm

if __name__ == '__main__':
	ChessboxApp().run()