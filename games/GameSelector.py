from typing import Union

from PyQt5 import QtSerialPort, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QLabel

from VideoQuestionsGame import VideoQuestionsGame
from WebcamBuzzerGame import WebcamBuzzerGame


class ControllerWindow( QWidget ):
	def __init__( self, flags, stylesheet, *args, **kwargs ):
		super().__init__( flags, *args, **kwargs )
		self.setStyleSheet( stylesheet )
		self.current_game_widget: Union[ None, QWidget ] = None

		self.serial = self.init_serial()

		self.game_layout = QVBoxLayout()
		self.game_layout.setAlignment( Qt.AlignTop )

		self.game_selector = GameSelector( stylesheet )

		self._layout = QHBoxLayout()
		self._layout.addWidget( self.game_selector )
		self._layout.addLayout( self.game_layout )
		self.setLayout( self._layout )

		self.game_selector.buzzer_game_button.clicked.connect( self.on_start_buzzer )
		self.game_selector.video_question_game.clicked.connect( self.on_start_video )
		self.game_selector.read_questions_game.clicked.connect( self.on_start_freestyle )

	def swap_current_game_widget( self, new_game_widget ):
		if self.current_game_widget:
			self.current_game_widget.hide()
			self.game_layout.removeWidget( self.current_game_widget )

		self.current_game_widget = new_game_widget

		if new_game_widget:
			self.game_layout.addWidget( new_game_widget )

		self.raise_()

	def on_start_buzzer( self ):
		buzzer_game_window = WebcamBuzzerGame( self.serial, self.styleSheet() )
		buzzer_game_window.setStyleSheet( self.styleSheet() )
		self.swap_current_game_widget( buzzer_game_window )

	def on_start_video( self ):
		video_questions_game = VideoQuestionsGame( self.serial, self.styleSheet() )
		self.serial.write( "f".encode() )
		self.swap_current_game_widget( video_questions_game )

	def on_start_freestyle( self ):
		self.serial.write( "f".encode() )

		self.swap_current_game_widget( None )

	@staticmethod
	def init_serial():
		port = QtSerialPort.QSerialPort(
			'/dev/ttyUSB0',
			baudRate=QtSerialPort.QSerialPort.Baud9600
		)
		port.open( QtCore.QIODevice.ReadWrite )
		return port


class GameSelector( QWidget ):
	def __init__( self, stylesheet ):
		super().__init__()
		self.setStyleSheet( stylesheet )

		self.buzzer_game_button = QPushButton( "Webcam Buzzer Game" )
		self.video_question_game = QPushButton( "Video Questions" )
		self.read_questions_game = QPushButton( "Freestyle Questions" )

		self._layout = QVBoxLayout()
		self._layout.setAlignment( Qt.AlignTop )
		self._layout.addWidget( self.buzzer_game_button )
		self._layout.addWidget( self.video_question_game )
		self._layout.addWidget( self.read_questions_game )

		self.setLayout( self._layout )
