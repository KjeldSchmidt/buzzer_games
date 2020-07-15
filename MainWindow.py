from PyQt5 import QtSerialPort, QtCore
from PyQt5.QtCore import QUrl, QFileInfo
from PyQt5.QtMultimedia import QMediaContent
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFileDialog, QSpinBox

import shortuuid

import VideoRecorder as vc
from ReplayWindow import ReplayWindow


class MainWindow( QWidget ):
	def __init__( self ):
		super().__init__()
		self.layout = QVBoxLayout()

		self.serial = self.init_serial()

		self.current_video_file: str = ""

		self.select_audio = QPushButton( "Select Audio" )
		self.select_audio.clicked.connect( self.on_select_audio() )
		self.start_timer = QPushButton( "Start Timer" )
		self.start_timer.clicked.connect( self.on_start_timer )
		self.end_recording = QPushButton( "End Recording" )
		self.end_recording.clicked.connect( self.on_stop_recording )
		self.show_replay = QPushButton( "Show Replay" )
		self.show_replay.clicked.connect( self.on_show_replay )

		self.offset_input = QSpinBox()
		self.offset_input.setRange( 0, 1000 * 60 * 60 )
		self.offset_input.setValue( 5000 )

		self.layout.addWidget( self.offset_input )
		self.layout.addWidget( self.select_audio )
		self.layout.addWidget( self.start_timer )
		self.layout.addWidget( self.end_recording )
		self.layout.addWidget( self.show_replay )

		self.setLayout( self.layout )

		self.replay_window = ReplayWindow()
		self.replay_window.showMaximized()

		self.time_result = None

	def start_recording( self ):
		self.current_video_file = shortuuid.uuid()
		vc.start_av_recording( self.current_video_file )

	def stop_recording( self ):
		vc.stop_av_recording( self.current_video_file )

	def on_select_play( self ):
		def handler():
			filename = QFileDialog.getOpenFileName( self, "Select Video", filter="Movies (*.mp4)" )
			self.replay_window.v_player.setMedia( QMediaContent( QUrl.fromLocalFile( filename[ 0 ] ) ) )
			self.replay_window.v_player.play()
			self.replay_window.music_player.play()

		return handler

	def on_select_audio( self ):
		def handler():
			filename = QFileDialog.getOpenFileName( self, "Select Sound", filter="Sound (*.mp3)", directory="clips/" )
			self.replay_window.music_player.setMedia( QMediaContent( QUrl.fromLocalFile( filename[ 0 ] ) ) )

		return handler

	def on_start_timer( self ):
		self.serial.write( "start_buzzer".encode() )
		self.replay_window.music_player.play()
		self.start_recording()

	def on_stop_recording( self ):
		self.replay_window.music_player.stop()
		self.stop_recording()

	def on_show_replay( self ):
		self.replay_window.time_result = self.time_result
		self.replay_window.offset_defined = self.offset_input.value()
		self.replay_window.replay( self.current_video_file )

	def init_serial( self ):
		port = QtSerialPort.QSerialPort(
			'/dev/ttyUSB0',
			baudRate=QtSerialPort.QSerialPort.Baud9600,
			readyRead=self.receive
		)
		port.open( QtCore.QIODevice.ReadWrite )
		return port

	@QtCore.pyqtSlot()
	def receive( self ):
		message: str
		while self.serial.canReadLine():
			message = self.serial.readLine().data().decode()
			message = message.rstrip( '\r\n' )

		time = self.replay_window.music_player.position()
		self.time_result = time
