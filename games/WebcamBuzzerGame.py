import time

from PyQt5 import QtSerialPort, QtCore
from PyQt5.QtCore import QUrl, QFileInfo
from PyQt5.QtMultimedia import QMediaContent
from PyQt5.QtSerialPort import QSerialPort
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFileDialog, QSpinBox, QDialog, QMessageBox

import VideoRecorder as vc
from ReplayWindow import ReplayWindow


class WebcamBuzzerGame( QWidget ):
	def __init__( self, serial: QSerialPort, stylesheet ):
		super().__init__()
		self.setStyleSheet( stylesheet )
		self.layout = QVBoxLayout()

		self.serial = serial
		self.serial.readyRead.connect( self.receive )

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
		self.offset_input.setValue( 0 )

		self.latency_input = QSpinBox()
		self.latency_input.setRange( -5000, 5000 )
		self.latency_input.setValue( 0 )

		self.layout.addWidget( self.offset_input )
		self.layout.addWidget( self.select_audio )
		self.layout.addWidget( self.start_timer )
		self.layout.addWidget( self.end_recording )
		self.layout.addWidget( self.show_replay )
		self.layout.addWidget( self.latency_input )

		self.setLayout( self.layout )

		self.replay_window = ReplayWindow( self.styleSheet(), self.latency_input )
		self.replay_window.showMaximized()

		self.time_result = None

	def hideEvent( self, QHideEvent ):
		super().hideEvent( QHideEvent )
		self.replay_window.close()

	def start_recording( self ):
		self.current_video_file = time.strftime( '%H-%M-%S', time.localtime() )
		vc.start_av_recording( self.current_video_file )

	def stop_recording( self ):
		vc.stop_av_recording( self.current_video_file )

	def on_select_audio( self ):
		def handler():
			filename = QFileDialog.getOpenFileName(
				self,
				"Select Sound",
				filter="Sound (*.mp3)",
				directory="../data/webcam_soundfiles"
			)
			self.replay_window.music_player.setMedia( QMediaContent( QUrl.fromLocalFile( filename[ 0 ] ) ) )

		return handler

	def on_start_timer( self ):
		if self.offset_input.value() != 0:
			self.serial.write( "v".encode() )
			self.replay_window.music_player.play()
			self.start_recording()
		else:
			mbox = QMessageBox()
			mbox.setText( "Set desired timing!" )
			mbox.exec_()

	def on_stop_recording( self ):
		self.serial.write( "i".encode() )
		self.replay_window.music_player.stop()
		self.stop_recording()
		self.replay_window.time_result = self.time_result
		self.replay_window.offset_defined = self.offset_input.value()
		self.offset_input.setValue( 0 )

	def on_show_replay( self ):
		self.replay_window.replay( self.current_video_file )

	@QtCore.pyqtSlot()
	def receive( self ):
		self.time_result = self.replay_window.music_player.position()
