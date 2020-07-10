import cv2
import pyaudio
import wave
import threading
import time
import subprocess
import os


########################
# JRF
# VideoRecorder and AudioRecorder are two classes based on openCV and pyaudio, respectively.
# By using multithreading these two classes allow to record simultaneously video and audio.
# ffmpeg is used for muxing the two signals
# A timer loop is used to control the frame rate of the video recording. This timer as well as
# the final encoding rate can be adjusted according to camera capabilities
########################

########################
# Usage:
#
# numpy, PyAudio and Wave need to be installed
# install openCV, make sure the file cv2.pyd is located in the same folder as the other libraries
# install ffmpeg and make sure the ffmpeg .exe is in the working directory
#
#
# start_AVrecording(filename) # function to start the recording
# stop_AVrecording(filename)  # "" ... to stop it
#
#
########################

class VideoRecorder:

	# Video class based on openCV
	def __init__( self, filename ):

		self.open = True
		self.device_index = 0
		self.fps = 6  # fps should be the minimum constant rate at which the camera can
		self.fourcc = "MJPG"  # capture images (with no decrease in speed over time; testing is required)
		self.frameSize = (640, 480)  # video formats and sizes also depend and vary according to the camera used
		self.video_filename = f"{filename}.avi"
		self.video_cap = cv2.VideoCapture( self.device_index )
		self.video_writer = cv2.VideoWriter_fourcc( *self.fourcc )
		self.video_out = cv2.VideoWriter( self.video_filename, self.video_writer, self.fps, self.frameSize )
		self.frame_counts = 1
		self.start_time = time.time()

	# Video starts being recorded
	def record( self ):

		# counter = 1
		# timer_start = time.time()
		# timer_current = 0

		while self.open:
			ret, video_frame = self.video_cap.read()
			if ret:

				self.video_out.write( video_frame )
				# print str(counter) + " " + str(self.frame_counts) + " frames written " + str(timer_current)
				self.frame_counts += 1
				# counter += 1
				# timer_current = time.time() - timer_start
				time.sleep( 0.16 )

			# Uncomment the following three lines to make the video to be
			# displayed to screen while recording

			# gray = cv2.cvtColor(video_frame, cv2.COLOR_BGR2GRAY)
			# cv2.imshow('video_frame', gray)
			# cv2.waitKey(1)
			else:
				break

	# 0.16 delay -> 6 fps
	#

	# Finishes the video recording therefore the thread too
	def stop( self ):

		if self.open:

			self.open = False
			self.video_out.release()
			self.video_cap.release()
			cv2.destroyAllWindows()

		else:
			pass

	# Launches the video recording function using a thread
	def start( self ):
		video_recording_thread = threading.Thread( target=self.record )
		video_recording_thread.start()


class AudioRecorder:

	# Audio class based on pyAudio and Wave
	def __init__( self, filename ):
		self.audio = pyaudio.PyAudio()
		self.device_index = self.find_device_index()

		self.open = True
		self.rate = 44100
		self.frames_per_buffer = 1024
		self.channels = 2
		self.format = pyaudio.paInt16
		self.audio_filename = f"{filename}.wav"
		self.stream = self.audio.open(
			format=self.format,
			channels=self.channels,
			rate=self.rate,
			input=True,
			output=False,
			input_device_index=self.device_index
		)
		self.audio_frames = [ ]

	# Audio starts being recorded
	def record( self ):

		self.stream.start_stream()
		while self.open:
			data = self.stream.read( self.frames_per_buffer )
			self.audio_frames.append( data )
			if not self.open:  # Is this line necessary? Might have to do something with audio timing, but seems rather pointless
				break

	# Finishes the audio recording therefore the thread too
	def stop( self ):
		if not self.open:
			return

		self.open = False
		self.stream.stop_stream()
		self.stream.close()
		self.audio.terminate()

		wave_file = wave.open( self.audio_filename, 'wb' )
		wave_file.setnchannels( self.channels )
		wave_file.setsampwidth( self.audio.get_sample_size( self.format ) )
		wave_file.setframerate( self.rate )
		wave_file.writeframes( b''.join( self.audio_frames ) )
		wave_file.close()

		pass

	# Launches the audio recording function using a thread
	def start( self ):
		audio_recording_thread = threading.Thread( target=self.record )
		audio_recording_thread.start()

	def find_device_index( self ):
		device_index = -1
		for x in range( 0, self.audio.get_device_count() ):
			info = self.audio.get_device_info_by_index( x )
			if info[ "name" ] == "pulse":
				device_index = info[ "index" ]
		return device_index


video_thread: VideoRecorder
audio_thread: AudioRecorder


def start_av_recording( filename ):
	global video_thread
	global audio_thread

	video_thread = VideoRecorder( filename )
	audio_thread = AudioRecorder( filename )

	audio_thread.start()
	video_thread.start()

	return filename


def start_video_recording( filename ):
	global video_thread

	video_thread = VideoRecorder( filename )
	video_thread.start()

	return filename


def start_audio_recording( filename ):
	global audio_thread

	audio_thread = AudioRecorder( filename )
	audio_thread.start()

	return filename


def stop_av_recording( filename ):
	audio_thread.stop()
	frame_counts = video_thread.frame_counts
	elapsed_time = time.time() - video_thread.start_time
	recorded_fps = frame_counts / elapsed_time
	print( "total frames " + str( frame_counts ) )
	print( "elapsed time " + str( elapsed_time ) )
	print( "recorded fps " + str( recorded_fps ) )
	video_thread.stop()

	# Makes sure the threads have finished
	while threading.active_count() > 1:
		time.sleep( 1 )

	# Merging audio and video signal

	if abs( recorded_fps - 30 ) >= 0.01:  # If the fps rate was higher/lower than expected, re-encode it to the expected

		print( "Re-encoding" )
		cmd = "ffmpeg -r " + str( recorded_fps ) + f" -i {filename}.avi -pix_fmt yuv420p -r 6 {filename}2.avi"
		subprocess.call( cmd, shell=True )

		print( "Muxing" )
		cmd = f"ffmpeg -ac 2 -channel_layout stereo -i {filename}.wav -i {filename}2.avi -pix_fmt yuv420p {filename}_final.avi"
		subprocess.call( cmd, shell=True )

	else:

		print( "Normal recording\nMuxing" )
		cmd = f"ffmpeg -ac 2 -channel_layout stereo -i {filename}.wav -i {filename}.avi -pix_fmt yuv420p {filename}_final.avi"
		subprocess.call( cmd, shell=True )

		print( ".." )

	# file_manager( filename )
	pass


# Required and wanted processing of final files
def file_manager( filename ):
	local_path = os.getcwd()

	if os.path.exists( f"{local_path}/{filename}.wav" ):
		os.remove( f"{local_path}/{filename}.wav" )

	if os.path.exists( f"{local_path}/{filename}.avi" ):
		os.remove( f"{local_path}/{filename}.avi" )

	if os.path.exists( f"{local_path}/{filename}2.avi" ):
		os.remove( f"{local_path}/{filename}2.avi" )
