from pythonosc import dispatcher
from pythonosc import osc_server
from pythonosc import osc_message_builder
from pythonosc import udp_client

import argparse

if __name__ == "__main__":
	ip = "192.168.1.123"
	sendPort = 7000
	inPort = 8000
	client = udp_client.SimpleUDPClient(ip, sendPort)

	server = osc_server.ThreadingOSCUDPServer((ip, inPort), dispatcher)
	print ("servering on {}".format(server.server_address))
	server.serve_forever()