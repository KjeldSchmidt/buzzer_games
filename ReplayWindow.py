from PyQt5 import QtCore
from PyQt5.QtMultimedia import QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel


class ReplayWindow( QWidget ):
	def __init__( self ):
		super().__init__()

		self.setStyleSheet( "background-color:black;" )

		self.offset_defined = None
		self.time_result = None

		self.layout = QVBoxLayout()
		self.video_w = QVideoWidget()
		self.timer_label = self.make_label()

		self.v_player = QMediaPlayer( None, QMediaPlayer.VideoSurface )
		self.v_player.setVideoOutput( self.video_w )
		self.v_player.setNotifyInterval( 7 )
		self.v_player.positionChanged.connect( self.update_time_label )
		self.a_player = QMediaPlayer( None, QMediaPlayer.LowLatency )

		self.layout.addWidget( self.timer_label )
		self.layout.addWidget( self.video_w )
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
			color:white;
			font-size:32px;
			padding: 16px;
			position: absolute;			
			"""
		)
		return timer_label
