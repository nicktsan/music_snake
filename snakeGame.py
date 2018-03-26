from battlesnake_functions import *
from speech_coms import *
from osc_stuff import *
from pygame.locals import *
from random import randint
import random
import pygame
import time
import math
import operator
import speech_recognition as sr

pygame.init()
white = [255, 255, 255]
black = [0, 0, 0]
green = [0, 155, 0]
red = [255, 0, 0]

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
 
	updateCountMax = 2
	updateCount = 0
 
	def __init__(self, id_num, length, x0, y0):
		self.player_id = id_num
		self.length = length
		self.x = []
		self.y = []
 
		 # initial positions, no collision.
		self.x.append(x0)
		self.x.append(x0)
		self.x.append(x0)

		self.y.append(y0)
		self.y.append(y0+1)
		self.y.append(y0+2)
 
	def update(self, height, width):
		if self.hp > 0:
			send_dir(self.direction, self.player_id)
			self.updateCount = self.updateCount+1
			if self.updateCount > self.updateCountMax:
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
		self.x = 0
		self.y = 0
		self.length = 0
		self.alive = False
		#for python 2.7
		#print ("Player %i died!") % self.player_id
		#for python 3.6.4
		print("player", self.player_id, "died!")

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
	board_width = 35
	board_height = 35

	def __init__(self):
		self._running = True
		self._display_surf = None
		self._head_surf = None
		self._image_surf = None
		self._apple_surf = None
		self.game = Game()

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
		final_players = 0
		final_food = 0
		final_ai = 0
		while settings: 
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					quit()
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_ESCAPE:
						pygame.quit()
						quit()
					if setting_ai == True and setting_food == True:
						if event.key == pygame.K_RETURN:
							try:
								final_ai = int(num_ai)
								settings = False
							except ValueError:
								print ("Only accepts integers.")
						elif event.key == pygame.K_BACKSPACE:
							num_ai = num_ai[:-1]
							self._display_surf.fill((255,255,255))
						else:
							num_ai += chr(event.key)
							self._display_surf.fill((255,255,255))
					if setting_food == True and setting_ai == False:
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
					if setting_food == False and setting_ai == False:
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
				if setting_food == True:
					self.message_to_screen("Enter number of food.", black, "normal", self.windowWidth/2, self.windowHeight/2+65, self._display_surf)
					self.message_to_screen(num_food, black, "normal", self.windowWidth/2, self.windowHeight/2+115, self._display_surf)
				if setting_ai == True and setting_food == True:
					self.message_to_screen("Enter number of AI.", black, "normal", self.windowWidth/2, self.windowHeight/2+165, self._display_surf)
					self.message_to_screen(num_ai, black, "normal", self.windowWidth/2, self.windowHeight/2+215, self._display_surf)

			pygame.display.update()
		return final_players, final_food, final_ai
 
		#do a maximum of 4 players
	def create_players(self, players, board_width, num_players, num_ai):
		total_snakes = num_players + num_ai
		spawn_location = int(board_width/3)
		for p in range(1, total_snakes+1):
			new_snake = 0
			x = 0
			y = 0
			if p > 4:
				break
			if p <= 2:
				x = spawn_location*p
				y = spawn_location
			else:
				x = spawn_location*(p-2)
				y = spawn_location*2
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
		self._running = True
		self._image_surf = []
		self._head_surf = []
		self._apple_surf = pygame.image.load("sprites/apple_sprite_01.png").convert()

		self._head_surf.append(pygame.image.load("sprites/snakehead_red.png").convert())
		self._head_surf.append(pygame.image.load("sprites/snakehead_green.png").convert())
		self._head_surf.append(pygame.image.load("sprites/snakehead_blue.png").convert())
		self._head_surf.append(pygame.image.load("sprites/snakehead_black.png").convert())

		self._image_surf.append(pygame.image.load("sprites/snake_tail_red.png").convert())
		self._image_surf.append(pygame.image.load("sprites/snake_tail_green.png").convert())
		self._image_surf.append(pygame.image.load("sprites/snake_tail_blue.png").convert())
		self._image_surf.append(pygame.image.load("sprites/snake_tail_black.png").convert())
		
 
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
		for player in kill_list:
			player.kill()
		self.board = update_board(self.players, self.apples, self.board_width, self.board_height)
		for player in self.players:
			if player.ai and player.hp > 0:
				self.calc_move(player)
 
	def on_render(self):
		self._display_surf.fill((255,255,255))
		for i in range(1, self.board_height+1):
			pygame.draw.line(self._display_surf, black, [i*step, 0], [i*step, self.windowHeight])
			pygame.draw.line(self._display_surf, black, [0, i*step], [(self.board_width)*step, i*step])
		stats_midpoint = (self.windowWidth - (self.board_width)*step)/2 + (self.board_width)*step

		for player in self.players:
			if player.hp > 0:
				player.draw(self._display_surf, self._image_surf[player.player_id-1], self._head_surf[player.player_id-1])
			message = 'Player ' + str(player.player_id) + ' HP: ' + str(player.hp)
			#message_to_screen(self, message, color, font_size, x_dispose, y_dispose, surface):
			self.message_to_screen(message, black, "small", stats_midpoint, 25*player.player_id, self._display_surf)
	
		for apple in self.apples:
			apple.draw(self._display_surf, self._apple_surf)
		pygame.display.flip()
 
	def on_cleanup(self):
		pygame.quit()
 
	def on_execute(self):
		if self.on_init() == False:
			self._running = False
		init_osc()
		while(self._running):
			self.game_intro()
			num_players, num_apples, num_ai = self.game_settings()
			self.players = self.create_players(self.players, self.board_width, num_players, num_ai)
			self.board = init_board(self.apples, num_apples, self.players, self.board_width, self.board_height)
			all_alive = True
			while(all_alive):
				pygame.event.pump()
				keys = pygame.key.get_pressed()
				alive_status = 0
				alive_status = []
				if keys[K_ESCAPE]:
					all_alive = False
				for player in self.players:
					if not player.ai:
						if (keys[K_RIGHT]):
							player.moveRight()
						if (keys[K_LEFT]):
							player.moveLeft()
						if (keys[K_UP]):
							player.moveUp()
						if (keys[K_DOWN]):
							player.moveDown()
				self.on_loop()
				self.on_render()
				for player in self.players:
					alive_status.append(player.alive)
				if not any(alive_status):
					all_alive = False
				time.sleep (50.0 / 1000.0);
		self.on_cleanup()
 
if __name__ == "__main__" :
	theApp = App()
	theApp.on_execute()