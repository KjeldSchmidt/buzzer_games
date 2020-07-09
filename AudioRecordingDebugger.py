import wave

import pyaudio

pa = pyaudio.PyAudio()
chosen_device_index = -1
for x in range( 0, pa.get_device_count() ):
	info = pa.get_device_info_by_index( x )
	if info[ "name" ] == "pulse":
		chosen_device_index = info[ "index" ]
		print( info )
		print( "Chosen index: ", chosen_device_index )

channel_count = 2
rate = 44100
stream = pa.open(
	format=pyaudio.paInt16,
	channels=channel_count,
	rate=rate,
	input_device_index=chosen_device_index,
	input=True,
	output=False
)
stream.start_stream()
audio_frames = [ ]

print( "start recording" )
for i in range( 500 ):
	data = stream.read( 1024 )
	audio_frames.append( data )
print( "end recording" )

stream.stop_stream()
stream.close()
pa.terminate()

with wave.open( 'test_audio.wav', 'wb' ) as wave_file:
	wave_file.setnchannels( channel_count )
	wave_file.setsampwidth( pa.get_sample_size( pyaudio.paInt16 ) )
	wave_file.setframerate( rate )
	wave_file.writeframes( b''.join( audio_frames ) )
