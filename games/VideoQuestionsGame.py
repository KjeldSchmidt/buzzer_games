from PyQt5 import QtSerialPort, QtCore
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtSerialPort import QSerialPort
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFileDialog, QSlider


class VideoPlayerWindow( QWidget ):
	def __init__( self ):
		super().__init__()

		self.slider_in_use = False

		self.video_w = QVideoWidget()
		self.slider = QSlider( Qt.Horizontal )
		self.slider.sliderPressed.connect( self.slider_pressed )
		self.slider.sliderReleased.connect( self.slider_value_changed )

		self.v_player = QMediaPlayer( None, QMediaPlayer.VideoSurface )
		self.v_player.setVideoOutput( self.video_w )
		self.v_player.setNotifyInterval( 50 )
		self.v_player.durationChanged.connect( self.video_duration_changed )
		self.v_player.positionChanged.connect( self.video_position_changed )
		self.v_player.stateChanged.connect( self.video_ended )

		self._layout = QVBoxLayout()

		self._layout.addWidget( self.video_w )
		self._layout.addWidget( self.slider )

		self._layout.setSpacing( 0 )
		self._layout.setContentsMargins( 0, 0, 0, 0 )

		self.setLayout( self._layout )

	def video_duration_changed( self ):
		self.slider.setRange( 0, self.v_player.duration() )

	def slider_pressed( self ):
		self.slider_in_use = True

	def video_position_changed( self ):
		if not self.slider_in_use:
			self.slider.setValue( self.v_player.position() )

	def slider_value_changed( self ):
		self.v_player.setPosition( self.slider.value() )
		self.slider_in_use = False

	def video_ended( self, state ):
		if state == QMediaPlayer.StoppedState:
			self.v_player.setPosition( self.v_player.duration() - 10 )
			self.v_player.play()
			self.v_player.pause()


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

		self.video_window = VideoPlayerWindow()
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
			filename = QFileDialog.getOpenFileName( parent=self, caption="Select Video", filter="Movies (*.mp4)" )
			self.video_window.v_player.setMedia( QMediaContent( QUrl.fromLocalFile( filename[ 0 ] ) ) )

		return handler

	def on_play_video( self ):
		self.video_window.v_player.play()
