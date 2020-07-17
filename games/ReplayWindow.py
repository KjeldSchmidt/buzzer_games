import time

from PyQt5 import QtCore
from PyQt5.QtCore import QFileInfo, QUrl, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QSlider, QHBoxLayout

recording_latency = 255


class ReplayWindowControls( QWidget ):
	def __init__( self, v_player, music_player, recording_player ):
		super().__init__()

		self.slider_in_use = False

		self.toggle_label = QPushButton( "⏯" )
		font = QFont( self.toggle_label.font().family(), pointSize=25 )
		self.toggle_label.setFont( font )
		self.toggle_label.clicked.connect( self.toggle_button_pressed )

		self.v_player = v_player
		self.music_player = music_player
		self.recording_player = recording_player
		self.v_player.durationChanged.connect( self.video_duration_changed )
		self.v_player.positionChanged.connect( self.video_position_changed )

		self.slider = QSlider( Qt.Horizontal )
		self.slider.sliderPressed.connect( self.slider_pressed )
		self.slider.sliderReleased.connect( self.slider_value_changed )

		self._layout = QHBoxLayout()
		self._layout.addWidget( self.toggle_label )
		self._layout.addWidget( self.slider )
		self.setLayout( self._layout )

	def toggle_button_pressed( self ):
		if self.v_player.state() == QMediaPlayer.PlayingState:
			self.v_player.pause()
			self.music_player.pause()
			self.recording_player.pause()
		elif self.v_player.state() == QMediaPlayer.PausedState:
			self.v_player.play()
			self.music_player.play()
			self.recording_player.play()

	def video_position_changed( self ):
		if not self.slider_in_use:
			self.slider.setValue( self.v_player.position() )

	def video_duration_changed( self ):
		self.slider.setRange( 0, self.v_player.duration() )

	def slider_pressed( self ):
		self.slider_in_use = True

	def slider_value_changed( self ):
		self.v_player.setPosition( max( self.slider.value(), recording_latency ) )
		self.music_player.setPosition( max( self.slider.value() - recording_latency, 0 ) )
		self.recording_player.setPosition( max( self.slider.value(), recording_latency ) )
		self.slider_in_use = False


class ReplayWindow( QWidget ):
	def __init__( self, stylesheet, **kwargs ):
		super().__init__( **kwargs )

		self.setStyleSheet( stylesheet )

		self.offset_defined = None
		self.time_result = None

		self.layout = QVBoxLayout()
		self.timer_label = self.make_label()
		self.video_w = QVideoWidget()

		self.v_player = QMediaPlayer( None, QMediaPlayer.VideoSurface )
		self.v_player.setVideoOutput( self.video_w )
		self.v_player.setNotifyInterval( 7 )
		self.v_player.positionChanged.connect( self.update_time_label )
		self.v_player.stateChanged.connect( self.video_ended )

		self.music_player = QMediaPlayer( None, QMediaPlayer.LowLatency )
		self.recording_player = QMediaPlayer( None, QMediaPlayer.LowLatency )

		self.controls = ReplayWindowControls( self.v_player, self.recording_player, self.music_player )

		self.layout.addWidget( self.timer_label )
		self.layout.addWidget( self.video_w )
		self.layout.addWidget( self.controls )
		self.layout.setSpacing( 0 )
		self.layout.setContentsMargins( 0, 0, 0, 0 )

		self.setLayout( self.layout )

	@staticmethod
	def format_millis( millis: int ) -> str:
		if millis >= 0:
			minutes = int( millis / (60 * 1000) )
			seconds = int( (millis % (60 * 1000)) / 1000 )
			ms = millis % 1000
			return f"{minutes:02}:{seconds:02}:{ms:03}"
		else:
			millis = -millis
			minutes = int( millis / (60 * 1000) )
			seconds = int( (millis % (60 * 1000)) / 1000 )
			ms = millis % 1000
			return f"-{minutes:02}:{seconds:02}:{ms:03}"

	def update_time_label( self ):
		if self.time_result is None:
			return

		position = self.v_player.position()
		if position > self.time_result:
			text = self.format_millis( self.time_result - self.offset_defined )
		else:
			text = self.format_millis( position - self.offset_defined )

		self.timer_label.setText( text )

	def make_label( self ):
		timer_label = QLabel()
		timer_label.setText( self.format_millis( 0 ) )
		timer_label.setAlignment( QtCore.Qt.AlignRight )
		timer_label.setStyleSheet(
			"""
			color: #CCCCCC;
			font-size:32px;
			padding: 16px;
			position: absolute;			
			"""
		)
		return timer_label

	def replay( self, file: str ):
		self.music_player.stop()
		self.v_player.stop()
		self.recording_player.stop()
		
		v_path = QFileInfo( f"recordings/{file}2.avi" ).absoluteFilePath()
		a_path = QFileInfo( f"recordings/{file}.wav" ).absoluteFilePath()
		self.v_player.setMedia( QMediaContent( QUrl.fromLocalFile( v_path ) ) )
		self.recording_player.setMedia( QMediaContent( QUrl.fromLocalFile( a_path ) ) )

		self.music_player.play()
		time.sleep( recording_latency / 1000 )  # Latency guessed empirically
		self.v_player.play()
		self.recording_player.play()

	def end_replay( self ):
		self.music_player.stop()
		self.v_player.stop()
		self.recording_player.stop()

	def video_ended( self ):
		if self.v_player.state() == QMediaPlayer.StoppedState:
			self.music_player.stop()
			self.v_player.setPosition( self.v_player.duration() - 10 )
			self.v_player.play()
			self.v_player.pause()
