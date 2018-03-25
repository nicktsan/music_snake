from battlesnake_functions import *
from pygame.locals import *
from random import randint
import pygame
import time
import math

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
	hp = 250
	x = 0
	y = 0
	direction = 2
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
 
	def update(self):
 		if self.hp > 0:
			self.updateCount += 1
			if self.updateCount > self.updateCountMax:
				# update previous positions
				for i in range(self.length-1,0,-1):
					self.x[i] = self.x[i-1]
					self.y[i] = self.y[i-1]
					
 
				# update position of head of snake
				if self.direction == 0:
					self.x[0] = self.x[0] + 1
				if self.direction == 1:
					self.x[0] = self.x[0] - 1
				if self.direction == 2:
					self.y[0] = self.y[0] - 1
				if self.direction == 3:
					self.y[0] = self.y[0] + 1
 
				self.updateCount = 0
				self.hp -= 1
		elif self.hp <= 0 and self.alive:
			print "in player.update"
			self.kill()
 
 	def kill(self):
 		self.hp = 0
 		self.x = 0
 		self.y = 0
 		self.length = 0
 		self.alive = False
 		print "Player %i died!" % self.player_id

	def moveRight(self):
		self.direction = 0
		self.angle = 0
 
	def moveLeft(self):
		self.direction = 1
		self.angle = 180
 
	def moveUp(self):
		self.direction = 2
		self.angle = 90
 
	def moveDown(self):
		self.direction = 3 
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
					quit()

				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_c:
						intro = False
					if event.key == pygame.K_q:
						pygame.quit()
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
							final_ai = int(num_ai)
							settings = False
						elif event.key == pygame.K_BACKSPACE:
							num_ai = num_ai[:-1]
							self._display_surf.fill((255,255,255))
						else:
							num_ai += chr(event.key)
							self._display_surf.fill((255,255,255))
					if setting_food == True and setting_ai == False:
						if event.key == pygame.K_RETURN:
							final_food = int(num_food)
							setting_ai = True
						elif event.key == pygame.K_BACKSPACE:
							num_food = num_food[:-1]
							self._display_surf.fill((255,255,255))
						else:
							num_food += chr(event.key)
							self._display_surf.fill((255,255,255))
					if setting_food == False and setting_ai == False:
						if event.key == pygame.K_RETURN:
							final_players = int(num_players)
							setting_food = True
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
		directions = ['up', 'down', 'left', 'right']

		return 0

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
				player.update()
				if (player.x[0] >= self.board_width or player.y[0] >= self.board_height or player.x[0] < 0 or player.y[0] < 0):
					print "in on_loop check for outofbounds"
					player.kill()
			elif player.alive and player.hp <= 0:
				print "check for hp <= 0"
				player.kill()
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
							player.hp = 250
			elif player.alive and player.hp <= 0:
				print "checking collision"
				player.kill()
		for player in kill_list:
			print "killing wave"
			player.kill()
		self.board = update_board(self.players, self.apples, self.board_width, self.board_height)
 
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

		self.game_intro()

		num_players, num_apples, num_ai = self.game_settings()

		self.players = self.create_players(self.players, self.board_width, num_players, num_ai)

		self.board = init_board(self.apples, num_apples, self.players, self.board_width, self.board_height)
 
		while( self._running ):
			pygame.event.pump()
			keys = pygame.key.get_pressed()
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
 
					if (keys[K_ESCAPE]):
						self._running = False
 				else:
 					self.calc_move(player)
			self.on_loop()
			self.on_render()
 
			time.sleep (50.0 / 1000.0);
		self.on_cleanup()
 
if __name__ == "__main__" :
	theApp = App()
	theApp.on_execute()