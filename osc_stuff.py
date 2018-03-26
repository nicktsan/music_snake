from pythonosc import dispatcher
from pythonosc import osc_server
from pythonosc import osc_message_builder
from pythonosc import udp_client
import argparse
import speech_recognition as sr
r = sr.Recognizer()
m = sr.Microphone()
stop_listening = None

def callback(recognizer, audio):
	print("data received from thread")
	try:
		data = r.recognize_sphinx(audio)
		print("Sphinx thinks you said: " + data)
		client.send_message("/data", data)
	except sr.UnknownValueError:
		print("Sphinx could not understand audio")
	except sr.RequestError as e:
		print("Sphinx error; {0}".format(e))	

def calibrate_threshold(unused_addr, args):
	print ("Calibrate received")
	client.send_message("/calibration", "calibration commenced")
	try:
		with m as source:
			r.adjust_for_ambient_noise(source, duration = 1.0)
			client.send_message("/calibration", "Minimum threshold set to {}", formate(r.energy_threshold))
	except (KeyboardInterrupt):
		print("Keyboard interrupt received")
		pass

def start_listening(unused_addr, args):
	global stop_listening 
	print("started listening")
	client.send_message("/startedListening", "Listening thread started")
	stop_listening = r.listen_in_background(m, callback, phrase_time_limit = 1.0)
	return

def stop_listening(unused_addr, args):
	global stop_listening
	print("stopping")
	client.send_message("/stoppedlistening", "stopped microphone thread")
	stop_listening(wait_for_stop = False)

if __name__ == "__main__":
	ip = "192.168.1.123"
	sendPort = 7000
	inPort = 8000

	#sending osc messages on
	client = udp_client.SimpleUDPClient(ip, sendPort)

	#catches OSC messages
	dispatcher = dispatcher.Dispatcher()
	dispatcher.map("/calibrate", calibrate_threshold)
	dispatcher.map("/startListening", start_listening)
	dispatcher.map("/stopListening", stop_listening)

	#set up server to listen for osc messages
	server = osc_server.ThreadingOSCUDPServer((ip, inPort), dispatcher)
	print ("servering on {}".format(server.server_address))
	server.serve_forever()