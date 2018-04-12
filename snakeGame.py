from battlesnake_functions import *
#from speech_coms import *
from osc_stuff import *
from pygame.locals import *
from pygame import mixer
from random import randint
from os import listdir
from os.path import isfile, join
import random
import pygame
import time
import math
import operator
import os
import speech_recognition as sr

pygame.init()
mixer.init()
white = [255, 255, 255]
black = [0, 0, 0]
green = [0, 155, 0]
red = [255, 0, 0]
cyan = [204, 255, 255]

small_font = pygame.font.SysFont("timesnewroman", 25)
normal_font = pygame.font.SysFont("timesnewroman", 50)
large_font = pygame.font.SysFont("timesnewroman", 100)

step = 22
class Apple:
	x = 0
	y = 0
 
	def __init__(self,x,y):
		self.x = x
		self.y = y
 
	def draw(self, surface, image):
		surface.blit(image,(self.x * step, self.y * step)) 

class Player:
	player_id = 0
	hp = 100
	x = 0
	y = 0
	direction = "up"
	length = 3
	ai = False
	angle = 90
	alive = True
	respawn_timer = 0.0
 
	updateCountMax = 2
	updateCount = 0
 
	def __init__(self, id_num, length, x0, y0):
		self.player_id = id_num
		self.length = length
		self.x = []
		self.y = []
 
		 # initial positions, no collision.
		for i in range(0, length):
			self.x.append(x0)
			self.y.append(y0+i)
 
	def update(self, height, width):
		if self.hp > 0:
			
			if not self.ai:
				self.direction = get_dir(self.player_id)
				if self.direction == "right":
					self.angle = 0
				if self.direction == "left":
					self.angle = 180
				if self.direction == "up":
					self.angle = 90
				if self.direction == "down":
					self.angle = 270
			self.updateCount = self.updateCount+1
			if self.updateCount > self.updateCountMax:
				send_dir(self.direction, self.player_id)
				send_quadrant(self.x[0], self.y[0], height, width)
				# update previous positions
				for i in range(self.length-1,0,-1):
					self.x[i] = self.x[i-1]
					self.y[i] = self.y[i-1]
					
				# update position of head of snake
				if self.direction == "right":
					self.x[0] = self.x[0] + 1
				if self.direction == "left":
					self.x[0] = self.x[0] - 1
				if self.direction == "up":
					self.y[0] = self.y[0] - 1
				if self.direction == "down":
					self.y[0] = self.y[0] + 1
 
				self.updateCount = 0
				self.hp -= 1
				if (self.x[0] >= width or self.y[0] >= height or self.x[0] < 0 or self.y[0] < 0 or self.hp <= 0):
					self.kill()
					
	def kill(self):
		self.hp = 0
		self.x.clear()
		self.y.clear()
		self.length = 0
		self.alive = False
		self.direction = "up"
		self.respawn_timer = 5000.0
		#for python 2.7
		#print ("Player %i died!") % self.player_id
		#for python 3.6.4
		print("player", self.player_id, "died!")
		death_trigger(self.length, self.player_id)

	def respawn(self, board, board_width, board_height, length):
		x_respawn = random.randint(5, board_width - 6)
		y_respawn = random.randint(5, board_height - 6)
		valid_spawn = False

		#check within a 2 tile radius of respawn for obstacles
		while not valid_spawn:
			valid_spawn = True
			while is_obstacle(x_respawn, y_respawn, board):
				x_respawn = random.randint(5, board_width - 6)
				y_respawn = random.randint(5, board_height - 6)

			for i in range(0, length):
				print("tile check: " + str(x_respawn) + ", " + str(y_respawn+i))
				#for radius = 0
				if is_obstacle(x_respawn, y_respawn+i, board) and not is_apple(x_respawn, y_respawn+i, board):
					valid_spawn = False
					break

				#for radius = 1
				for dX in range(-1, 2):
					#calculate absolute value of y
					dY = 1 - abs(dX)
					neg_dY = dY*-1
					if is_obstacle(x_respawn+dX, y_respawn+i+dY, board) or is_obstacle(x_respawn+dX, y_respawn+i+neg_dY, board):
						valid_spawn = False
						break

				#for radius = 2
				for dX in range(-2, 3):
					#calculate absolute value of y
					dY = 2 - abs(dX)
					neg_dY = dY*-1
					if is_obstacle(x_respawn+dX, y_respawn+i+dY, board) or is_obstacle(x_respawn+dX, y_respawn+i+neg_dY, board):
						valid_spawn = False
						break
				if not valid_spawn:
					x_respawn = random.randint(5, board_width - 6)
					y_respawn = random.randint(5, board_height - 6)
					break

			self.hp = 100
			self.x = []
			self.y = []
			self.direction = "up"
			self.length = 3
			self.angle = 90
			self.alive = True
			self.respawn_timer = 0.0
			self.updateCountMax = 2
			self.updateCount = 0
			for i in range(0, length):
				self.x.append(x_respawn)
				self.y.append(y_respawn+i)

	def moveRight(self):
		self.direction = "right"
		self.angle = 0
 
	def moveLeft(self):
		self.direction = "left"
		self.angle = 180
 
	def moveUp(self):
		self.direction = "up"
		self.angle = 90
 
	def moveDown(self):
		self.direction = "down"
		self.angle = 270
 
	def draw(self, surface, image, head):
		head = pygame.transform.rotate(head, self.angle)
		surface.blit(head, (self.x[0]*step, self.y[0]*step))
		for i in range(1, self.length):
			surface.blit(image,(self.x[i]*step, self.y[i]*step)) 

class Game:
	def isCollision(self,x1,y1,x2,y2, width, height):
		if x1 == x2:
			if y1 == y2:
				return True
		if (x1 < 0 or x1 >= width or y1 < 0 or y1 >= height):
			return True
		return False

class App:
	players = []
	#apples are marked on the board as non-zero integers. When referencing the apple list using board location,
	#do i-1
	apples = []
	windowWidth = 1012
	windowHeight = 770
	board = 0
	board_width = 28
	board_height = 28
	time = 0

	def __init__(self):
		self._running = True
		self._display_surf = None
		self._head_surf = None
		self._image_surf = None
		self._apple_surf = None
		self.game = Game()

	def reset_game(self):
		self.time = 0
		self.players.clear()
		self.apples.clear()
		self.board = 0

	def text_objects(self, text, color, font_size):
		text_surface = None
		if font_size == "small":
			text_surface = small_font.render(text, True, color)
		elif font_size == "normal":
			text_surface = normal_font.render(text, True, color)
		elif font_size == "large":
			text_surface = large_font.render(text, True, color)
		return text_surface, text_surface.get_rect()

	def message_to_screen(self, message, color, font_size, x_dispose, y_dispose, surface):
		text_surface, text_rect = self.text_objects(message, color, font_size)
		text_rect.center = x_dispose, y_dispose
		surface.blit(text_surface, text_rect)

	def game_intro(self):
		self._display_surf.fill((255,255,255))
		intro = True
		while intro:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					kill_server()
					quit()

				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_c:
						intro = False
					if event.key == pygame.K_q:
						pygame.quit()
						kill_server()
						quit()

			self.message_to_screen("Musical Snakes!", black, "normal", self.windowWidth/2, self.windowHeight/2-115, self._display_surf)
			#message_to_screen("PYTHON", red, font_size="large", y_dispose=-40)
			#message_to_screen("game!", black, font_size="normal", y_dispose=20)
			self.message_to_screen("Press C to play or Q to quit!", green, "small", self.windowWidth/2, self.windowHeight/2+180, self._display_surf)
			pygame.display.update()

	def game_settings(self):
		self._display_surf.fill((255,255,255))
		settings = True
		num_players = ""
		setting_food = False
		num_food = ""
		setting_ai = False
		num_ai = ""
		setting_time = False
		time_num = ""
		final_players = 0
		final_food = 0
		final_ai = 0
		final_time = 0
		while settings: 
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					kill_server()
					quit()
				if event.type == pygame.KEYDOWN:

					if event.key == pygame.K_ESCAPE:
						if setting_ai and setting_food and setting_time:
							setting_time = False
						elif setting_ai and setting_food and not setting_time:
							setting_ai = False
						elif not setting_ai and setting_food and not setting_time:
							setting_food = False
						else:
							pygame.quit()
							kill_server()
							quit()

					if setting_ai and setting_food and setting_time:
						if event.key == pygame.K_RETURN:
							try:
								final_time = int(time_num)
								settings = False
							except ValueError:
								print ("Only accepts integers.")
						elif event.key == pygame.K_BACKSPACE:
							time_num = time_num[:-1]
							self._display_surf.fill((255,255,255))
						else:
							time_num += chr(event.key)
							self._display_surf.fill((255,255,255))

					if setting_ai and setting_food and not setting_time:
						if event.key == pygame.K_RETURN:
							try:
								final_ai = int(num_ai)
								setting_time = True
							except ValueError:
								print ("Only accepts integers.")
						elif event.key == pygame.K_BACKSPACE:
							num_ai = num_ai[:-1]
							self._display_surf.fill((255,255,255))
						else:
							num_ai += chr(event.key)
							self._display_surf.fill((255,255,255))
					if setting_food and not setting_ai and not setting_time:
						if event.key == pygame.K_RETURN:
							try:
								final_food = int(num_food)
								setting_ai = True
							except ValueError:
								print ("Only accepts integers.")
						elif event.key == pygame.K_BACKSPACE:
							num_food = num_food[:-1]
							self._display_surf.fill((255,255,255))
						else:
							num_food += chr(event.key)
							self._display_surf.fill((255,255,255))
					if not setting_food and not setting_ai and not setting_time:
						if event.key == pygame.K_RETURN:
							try:
								final_players = int(num_players)
								setting_food = True
							except ValueError:
								print ("Only accepts integers.")
						elif event.key == pygame.K_BACKSPACE:
							num_players = num_players[:-1]
							self._display_surf.fill((255,255,255))
						else:
							num_players += chr(event.key)
							self._display_surf.fill((255,255,255))
					
			
				self.message_to_screen("Enter number of players.", black, "normal", self.windowWidth/2, self.windowHeight/2-115, self._display_surf)
				self.message_to_screen(num_players, black, "normal", self.windowWidth/2, self.windowHeight/2-65, self._display_surf)
				if setting_food:
					self.message_to_screen("Enter number of food.", black, "normal", self.windowWidth/2, self.windowHeight/2-15, self._display_surf)
					self.message_to_screen(num_food, black, "normal", self.windowWidth/2, self.windowHeight/2+45, self._display_surf)
				if setting_ai and setting_food:
					self.message_to_screen("Enter number of AI.", black, "normal", self.windowWidth/2, self.windowHeight/2+95, self._display_surf)
					self.message_to_screen(num_ai, black, "normal", self.windowWidth/2, self.windowHeight/2+145, self._display_surf)
				if setting_ai and setting_food and setting_time:
					self.message_to_screen("Enter time (seconds).", black, "normal", self.windowWidth/2, self.windowHeight/2+195, self._display_surf)
					self.message_to_screen(time_num, black, "normal", self.windowWidth/2, self.windowHeight/2+245, self._display_surf)

			pygame.display.update()
		return final_players, final_food, final_ai, final_time
 
		#do a maximum of 4 players
	def create_players(self, players, num_players, num_ai):
		total_snakes = num_players + num_ai
		players_per_row = math.ceil(math.sqrt(total_snakes))
		x_distance = int(self.board_width/(players_per_row+1))
		y_distance = int(self.board_height/(players_per_row+1))
		for p in range(1, total_snakes+1):
			x_spawn = p % players_per_row
			if x_spawn == 0:
				x_spawn = players_per_row
			y_spawn = math.ceil(float(p/players_per_row))
			new_snake = 0
			x = x_spawn*x_distance
			y = y_spawn*y_distance
			new_snake = Player(p, 3, x, y)
			if p > num_players:
				new_snake.ai = True
			players.append(new_snake)	
		return players

	def calc_move(self, player):
		if player.updateCount == player.updateCountMax:
			directions = ['up', 'down', 'left', 'right']
			is_left = check_left(player.x[0], player.y[0], self.board)
			is_right = check_right(player.x[0], player.y[0], self.board)
			is_up = check_up(player.x[0], player.y[0], self.board)
			is_down = check_down(player.x[0], player.y[0], self.board)
			if is_up:
				directions.remove('up')
			if is_down:
				directions.remove('down')
			if is_left:
				directions.remove('left')
			if is_right:
				directions.remove('right')
			try:
				direction = random.choice(directions)
			except IndexError:
				print ("Goodbye cruel world!")
				direction = 'up'
			if (len(directions) > 1):
				#make a dictionary for remaining viable directions.
				#For example: if directions = ['up', 'down', 'right'] then moves will be
				#							  {'up': 0, 'down': 0, 'right': 0}
				moves = {}
				for direction in directions:
					moves[direction] = 0
				"""
				TODO assign points to corresponding choices
				Let's say we want to give 'right' 3 points. Type:
				moves['right'] += 3 
				moves will then become 
				{'up': 0, 'down': 0, 'right': 3}
				"""
				goal_points = seek_apple(self.apples, self.players, player)
				for goal_point in goal_points:
					path = jps((player.x[0], player.y[0]), (goal_point[1], goal_point[2]), self.board)
					if path != None:
						head, nextNode = path[0][0], path[0][1]
						vect = calc_vec(head[0], head[1], nextNode[0], nextNode[1])
						vX, vY = vect[0], vect[1]
						priority = 200
						score = (priority - player.hp)*0.01
						if (vX < 0):
							if ('left' in moves):
								moves['left'] += score
						if (vX > 0):
							if ('right' in moves):
								moves['right'] += score
						if (vY < 0):
							if ('up' in moves):
								moves['up'] += score
						if (vY > 0):
							if ('down' in moves):
								moves['down'] += score
						break
					else:
						path = jps((player.x[0], player.y[0]), (player.x[player.length-1], player.y[player.length-1]), self.board)
				#for python 2.7
				#direction = max(moves.iteritems(), key = operator.itemgetter(1))[0]

				#for python 3.6.4
				direction = max(moves.items(), key = operator.itemgetter(1))[0]

			if direction == 'up':
				player.moveUp()
			if direction == 'down':
				player.moveDown()
			if direction == 'left':
				player.moveLeft()
			if direction == 'right':
				player.moveRight()

	def on_init(self):
		self._display_surf = pygame.display.set_mode((self.windowWidth,self.windowHeight), pygame.HWSURFACE)
		pygame.display.set_caption('Nicholas Tsang Python')
		headpath = "sprites/heads/"
		tailpath = "sprites/tails/"
		headpics = [f for f in listdir(headpath) if isfile(join(headpath, f))]
		tailpics = [f for f in listdir(tailpath) if isfile(join(tailpath, f))]
		self._running = True
		self._image_surf = []
		self._head_surf = []
		self._apple_surf = pygame.image.load("sprites/apple_sprite_01.png").convert()

		for headpic in headpics:
			headpath = "sprites/heads/"
			headpath = headpath + headpic
			self._head_surf.append(pygame.image.load(headpath).convert())

		for tailpic in tailpics:
			tailpath = "sprites/tails/"
			tailpath = tailpath + tailpic
			self._image_surf.append(pygame.image.load(tailpath).convert())

	def on_event(self, event):
		if event.type == QUIT:
			self._running = False
		

	def on_loop(self):
		for player in self.players:
			if player.hp > 0:
				player.update(self.board_height, self.board_width)

		kill_list = []
		for player in self.players:
			if player.hp > 0:
				# does snake collide with itself?
				for enemy in self.players:
					if enemy.hp > 0:
						for i in range(0, enemy.length):
							if enemy.player_id == player.player_id and i == 0:
								continue
							if self.game.isCollision(player.x[0], player.y[0], enemy.x[i], enemy.y[i],self.board_width, self.board_height):
								kill_list.append(player)

				# does snake eat apple?
				for i in range(0, player.length):
					for apple in self.apples:
						if self.game.isCollision(apple.x, apple.y, player.x[i], player.y[i], self.board_width, self.board_height):
							apple.respawn(self.board, self.board_width, self.board_height)
							player.x.append(player.x[player.length-1])
							player.y.append(player.y[player.length-1])
							player.length += 1
							player.hp = 100
							eat_trigger(player.length)
		for player in kill_list:
			player.kill()
		self.board = update_board(self.players, self.apples, self.board_width, self.board_height)
		for player in self.players:
			if player.hp <= 0:
				if player.respawn_timer == 0:
					player.respawn(self.board, self.board_width, self.board_height, 3)
					self.board = update_board(self.players, self.apples, self.board_width, self.board_height)
				else:
					player.respawn_timer -= 50
			if player.ai and player.hp > 0:
				self.calc_move(player)
 
	def on_render(self, countdown, elapsed_time):
		height_division = int(self.board_height/4)
		width_division = int(self.board_width/4)
		self._display_surf.fill((255,255,255))
		for y in range(0, 4):
			for x in range(0, 4):
				total = x + y
				colour = white
				if total % 2 == 0:
					colour = cyan
				pygame.draw.rect(self._display_surf, colour, [x*step*width_division, y*step*height_division, step*width_division, step*height_division])


		for i in range(1, self.board_height+1):
			pygame.draw.line(self._display_surf, black, [i*step, 0], [i*step, self.board_height*step])
			pygame.draw.line(self._display_surf, black, [0, i*step], [self.board_width*step, i*step])
		stats_midpoint = (self.windowWidth - (self.board_width)*step)/2 + (self.board_width)*step

		for player in self.players:
			if player.hp > 0:
				player.draw(self._display_surf, self._image_surf[player.player_id-1], self._head_surf[player.player_id-1])
			self._display_surf.blit(self._head_surf[player.player_id-1], (stats_midpoint-107, 25*player.player_id-9))
			message = 'Player ' + str(player.player_id) + ' HP: ' + str(player.hp)
			self.message_to_screen(message, black, "small", stats_midpoint, 25*player.player_id, self._display_surf)
	
		for apple in self.apples:
			apple.draw(self._display_surf, self._apple_surf)
		
		if countdown > 0:
			self.message_to_screen(str(countdown), black, "normal", stats_midpoint, self.windowHeight - 30, self._display_surf)
			pygame.display.flip()
			time.sleep(1)
			self.on_render(countdown - 1, elapsed_time)
		self.message_to_screen(str('%.3f' % (self.time - elapsed_time)), black, "normal", stats_midpoint, self.windowHeight - 60, self._display_surf)
		pygame.display.flip()

	def game_results(self):
		self._display_surf.fill((255,255,255))
		done = False
		player_lengths = []
		for player in self.players:
			self._display_surf.blit(self._head_surf[player.player_id-1], (self.windowWidth/2-107, 25*player.player_id-9))
			message = 'Player ' + str(player.player_id) + ' length: ' + str(player.length)
			self.message_to_screen(message, black, "small", self.windowWidth/2, 25*player.player_id, self._display_surf)
			player_lengths.append((player.player_id, player.length))
		#winner = max(player_lengths, key=operator.itemgetter(1))[0]
		sorted_player_lengths = sorted(player_lengths, key=operator.itemgetter(1), reverse = True)
		winners = []
		for i in range(0, len(sorted_player_lengths)):
			if i == 0:
				winners.append(sorted_player_lengths[i])
			else:
				if sorted_player_lengths[i][1] == winners[0][1]:
					winners.append(sorted_player_lengths[i])

		message = "Congratulations player " + str(winners[0][0])
		winners.pop(0)
		for winner in winners:
			message = message + ", " + str(winner[0])

		self.message_to_screen(message, black, "normal", self.windowWidth/2, 25*len(self.players) + 50, self._display_surf)
		pygame.display.flip()
		while not done:
			for event in pygame.event.get():
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
						done = True

 
	def on_cleanup(self):
		pygame.quit()
 
	def on_execute(self):
		if self.on_init() == False:
			self._running = False
		init_osc()
		while(self._running):
			self.game_intro()
			num_players, num_apples, num_ai, self.time = self.game_settings()
			self.players = self.create_players(self.players, num_players, num_ai)
			create_dirs(num_players)
			self.board = init_board(self.apples, num_apples, self.players, self.board_width, self.board_height)
			announce_start()
			self.on_render(3, 0)
			start_time = time.time()
			elapsed_time = 0.0
			while(elapsed_time < self.time):
				pygame.event.pump()
				keys = pygame.key.get_pressed()
				if keys[K_ESCAPE]:
					break
				self.on_loop()
				self.on_render(0, elapsed_time)
				if check_game_status() == False:
					break
				time.sleep (50.0 / 1000.0);
				elapsed_time = time.time() - start_time
			self.game_results()
			self.reset_game()
			reset_players()
				
		self.on_cleanup()
 
if __name__ == "__main__" :
	theApp = App()
	theApp.on_execute()
