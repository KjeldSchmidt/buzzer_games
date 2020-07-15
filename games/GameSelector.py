from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton

from VideoQuestionsGame import VideoQuestionsGame
from WebcamBuzzerGame import WebcamBuzzerGame


class GameSelector( QWidget ):
	def __init__( self ):
		super().__init__()
		self.layout = QVBoxLayout()

		self.buzzer_game_button = QPushButton( "Webcam Buzzer Game" )
		self.buzzer_game_button.clicked.connect( self.on_start_buzzer )
		self.video_question_game = QPushButton( "Video Questions" )
		self.video_question_game.clicked.connect( self.on_start_video )
		self.read_questions_game = QPushButton( "Freestyle Questions" )
		self.read_questions_game.clicked.connect( self.on_start_freestyle )

		self.layout.addWidget( self.buzzer_game_button )
		self.layout.addWidget( self.video_question_game )
		self.layout.addWidget( self.read_questions_game )

		self.setLayout( self.layout )

	def on_start_buzzer( self ):
		buzzer_game_window = WebcamBuzzerGame( self.serial )
		buzzer_game_window.setStyleSheet( self.styleSheet() )
		buzzer_game_window.show()

	def on_start_video( self ):
		video_questions_game = VideoQuestionsGame()
		video_questions_game.setStyleSheet( self.styleSheet() )
		video_questions_game.show()

	def on_start_freestyle( self ):
		pass
