from pythonosc import dispatcher
from pythonosc import osc_server
from pythonosc import osc_message_builder
from pythonosc import udp_client
import threading
from speech_coms import *
import argparse
import random
import time
import speech_recognition as sr
r = sr.Recognizer()
m = sr.Microphone()
stop_listening = None
client = 0
server = 0
server_thread = 0
directions = []
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

def calibrate_threshold(unused_addr):
	print ("Calibrate received")
	directions.append("up")
	print (directions)
	client.send_message("/calibration", "calibration commenced")
	try:
		with m as source:
			r.adjust_for_ambient_noise(source, duration = 1.0)
			client.send_message("/calibration", "Minimum threshold set to {}".format(r.energy_threshold))
	except (KeyboardInterrupt):
		print("Keyboard interrupt received")
		pass

def start_listening(unused_addr):
	global stop_listening
	directions.append("down")
	print(directions)
	print("started listening")
	client.send_message("/startedListening", "Listening thread started")
	stop_listening = r.listen_in_background(m, callback, phrase_time_limit = 1.0)
	return

def stop_listening(unused_addr):
	global stop_listening
	directions.append("left")
	print(directions)
	print("stopping")
	client.send_message("/stoppedlistening", "stopped microphone thread")
	stop_listening(wait_for_stop = False)

def player1up(unused_addr):
	try:
		#print("up1")
		directions[0] = "up"
	except (IndexError):
		pass

def player1down(unused_addr):
	try:
		#print("down1")
		directions[0] = "down"
	except (IndexError):
		pass

def player1left(unused_addr):
	try:
		#print("left1")
		directions[0] = "left"
	except (IndexError):
		pass

def player1right(unused_addr):
	try:
		#print("right1")
		directions[0] = "right"
	except (IndexError):
		pass

def player2up(unused_addr):
	try:
		#print("up2")
		directions[1] = "up"
	except (IndexError):
		pass

def player2down(unused_addr):
	try:
		#print("down2")
		directions[1] = "down"
	except (IndexError):
		pass

def player2left(unused_addr):
	try:
		#print("left2")
		directions[1] = "left"
	except (IndexError):
		pass

def player2right(unused_addr):
	try:
		#print("right2")
		directions[1] = "right"
	except (IndexError):
		pass
def death_trigger(length):
	global client
	client.send_message("/death", length)

def eat_trigger(length):
	global client
	client.send_message("/eat", length)

def send_dir(move, player_id):
	global client
	#move = str(player_id) + " " + str(move)
	client.send_message("/move", move)

def get_dir(player_id):
	return directions[player_id-1]

def create_dirs(num_players):
	for i in range(0, num_players):
		directions.append("up")
				
def reset_players():
	directions.clear()

def send_quadrant(x, y, board_height, board_width):
	#0-7 8-15 16-23 24-31 32-34
	global client
	height_division = int(board_height/4)
	width_division = int(board_width/4)
	x_section = int(x/width_division)
	y_section = int(y/height_division)
	if x_section > 3:
			x_section = 3
	if y_section > 3:
			y_section = 3
	section_num = int(x_section + 4*y_section)
	client.send_message("/quadrant", section_num)

def kill_server():
	global server
	global server_thread
	server.shutdown()
	print("active threads: ")
	print(threading.active_count())

def init_osc():
	#for my laptop to uvic wifi
	#ip = "134.87.146.10"
	#for mac in pty
	#ip = "192.168.10.255"
	#for uvic mac studio 2 computer
	#ip = "192.168.1.102"
	#for home laptop at home ethernet
	ip = "192.168.1.123"
	#for uvic wifi
	#ip = "134.87.155.109"
	sendPort = 5005
	inPort = 8000

	#sending osc messages on
	global client
	client = udp_client.SimpleUDPClient(ip, sendPort)

	#catches OSC messages
	global dispatcher
	dispatcher = dispatcher.Dispatcher()
	dispatcher.map("/calibrate", calibrate_threshold)
	dispatcher.map("/startListening", start_listening)
	dispatcher.map("/stopListening", stop_listening)
	dispatcher.map("/up1", player1up)
	dispatcher.map("/down1", player1down)
	dispatcher.map("/left1", player1left)
	dispatcher.map("/right1", player1right)
	dispatcher.map("/up2", player2up)
	dispatcher.map("/down2", player2down)
	dispatcher.map("/left2", player2left)
	dispatcher.map("/right2", player2right)
	
	#set up server to listen for osc messages
	global server
	global server_thread
	server = osc_server.ThreadingOSCUDPServer((ip, inPort), dispatcher)
	server_thread = threading.Thread(target=server.serve_forever)
	server_thread.start()
	print ("servering on {}".format(server.server_address))
	print("active threads: ")
	print(threading.active_count())

if __name__ == "__main__":
	init_osc()
	"""
	ip = "192.168.1.123"
	sendPort = 5005
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
	"""
