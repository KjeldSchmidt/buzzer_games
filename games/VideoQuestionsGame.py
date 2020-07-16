from PyQt5 import QtCore
from PyQt5.QtCore import QUrl
from PyQt5.QtMultimedia import QMediaContent
from PyQt5.QtSerialPort import QSerialPort
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFileDialog

from VideoPlayerWithControls import VideoPlayerWithControls


class VideoQuestionsGame( QWidget ):
	def __init__( self, serial: QSerialPort, stylesheet ):
		super().__init__()
		self.serial = serial
		self.serial.readyRead.connect( self.handle_serial )
		self.setStyleSheet( stylesheet )
		self.layout = QVBoxLayout()

		self.select_video = QPushButton( "Select Video" )
		self.select_video.clicked.connect( self.on_select_video() )
		self.play_video = QPushButton( "Play Video" )
		self.play_video.clicked.connect( self.on_play_video )

		self.layout.addWidget( self.select_video )
		self.layout.addWidget( self.play_video )

		self.setLayout( self.layout )

		self.video_window = VideoPlayerWithControls()
		self.video_window.setStyleSheet( self.styleSheet() )
		self.video_window.showMaximized()

	@QtCore.pyqtSlot()
	def handle_serial( self ):
		message = self.serial.readLine().data().decode()
		message = message.rstrip( '\r\n' )
		message = message[ -1 ]
		if message == "s":
			self.video_window.v_player.pause()
		elif message == "c":
			self.video_window.v_player.play()

	def hideEvent( self, hide_event ):
		super().hideEvent( hide_event )
		self.video_window.v_player.stop()
		self.video_window.close()

	def on_select_video( self ):
		def handler():
			filename = QFileDialog.getOpenFileName(
				parent=self,
				caption="Select Video",
				filter="Movies (*.mp4)",
				directory="/home/kjeld/Desktop/schlag_den_boehm/data/video_question_videos"
			)
			self.video_window.v_player.setMedia( QMediaContent( QUrl.fromLocalFile( filename[ 0 ] ) ) )

		return handler

	def on_play_video( self ):
		self.video_window.v_player.play()
