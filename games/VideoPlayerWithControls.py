from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QFontMetrics
from PyQt5.QtMultimedia import QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import QWidget, QSlider, QVBoxLayout, QHBoxLayout, QLabel, QPushButton


class VideoControls( QWidget ):
	def __init__( self, v_player ):
		super().__init__()

		self.slider_in_use = False

		self.toggle_label = QPushButton( "⏯" )
		font = QFont( self.toggle_label.font().family(), pointSize=25 )
		self.toggle_label.setFont( font )
		self.toggle_label.clicked.connect( self.toggle_button_pressed )

		self.v_player = v_player
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
		else:
			self.v_player.play()

	def video_position_changed( self ):
		if not self.slider_in_use:
			self.slider.setValue( self.v_player.position() )

	def video_duration_changed( self ):
		self.slider.setRange( 0, self.v_player.duration() )

	def slider_pressed( self ):
		self.slider_in_use = True

	def slider_value_changed( self ):
		self.v_player.setPosition( self.slider.value() )
		self.slider_in_use = False


class VideoPlayerWithControls( QWidget ):
	def __init__( self ):
		super().__init__()

		self.video_w = QVideoWidget()
		self.v_player = QMediaPlayer( None, QMediaPlayer.VideoSurface )
		self.v_player.setVideoOutput( self.video_w )
		self.v_player.setNotifyInterval( 50 )
		self.v_player.stateChanged.connect( self.video_ended )

		self.controls = VideoControls( self.v_player )

		self._layout = QVBoxLayout()

		self._layout.addWidget( self.video_w )
		self._layout.addWidget( self.controls )

		self._layout.setSpacing( 0 )
		self._layout.setContentsMargins( 0, 0, 0, 0 )

		self.setLayout( self._layout )

	def video_ended( self, state ):
		if state == QMediaPlayer.StoppedState:
			self.v_player.setPosition( self.v_player.duration() - 10 )
			self.v_player.play()
			self.v_player.pause()
