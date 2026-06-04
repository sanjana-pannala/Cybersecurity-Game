import pygame
from pygame.locals import *
from pygame import mixer
import pickle
import yaml
from random import randrange
from os import path
import webbrowser
import auth  # Import the authentication module

pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 1000
screen_height = 1000

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Platformer')


#define font
font = pygame.font.SysFont('Bauhaus 93', 60)
font_score = pygame.font.SysFont('Bauhaus 93', 30)
video_font = pygame.font.SysFont('Bauhaus 93', 20)
option_font = pygame.font.SysFont('Bauhaus 93', 30)
input_font = pygame.font.SysFont('Arial', 24)  # Font for input fields

#define game variables
tile_size = 50
game_over = 0
main_menu = True
level = 0
max_levels = 7
score = 0

# Authentication variables
auth_state = "login"  # States: "login", "register", "game"
current_user = None
username_input = ""
password_input = ""
active_input = "username"  # Which input field is active
auth_message = ""
show_password = False  # For password visibility toggle

show_continue_prompt = False
question_mode = False
current_question = None
user_answer = ''
show_feedback = False
show_game_over_window = False
show_hint_options = False

# Array of video links (will be changed later)
video_links = [
    'https://youtu.be/00hpRjfbM0A?si=_DVKpVK4NQKWMxLg',
    'https://youtu.be/dQw4w9WgXcQ',
    'https://youtu.be/jNQXAC9IVRw',
    'https://youtu.be/kJQP7kiw5Fk',
    'https://youtu.be/9bZkp7q19f0',
    'https://youtu.be/RgKAFK5djSk',
    'https://youtu.be/OPf0YbXqDm0',
    'https://youtu.be/JGwWNGJdvx8',
    'https://youtu.be/fJ9rUzIMcZQ',
    'https://youtu.be/1G4isv_Fylg'
]

#define colours
white = (255, 255, 255)
blue = (0, 0, 255)
dark_blue = (0, 0, 139)
BUTTON_COLOR = dark_blue
black = (0, 0, 0)
red = (255, 0, 0)
green = (0, 255, 0)
gray = (128, 128, 128)
light_gray = (200, 200, 200)

#load images
sun_img = pygame.image.load('img/sun.png')
bg_img = pygame.image.load('img/sky.png')
restart_img = pygame.image.load('img/restart_btn.png')
start_img = pygame.image.load('img/start_btn.png')
exit_img = pygame.image.load('img/exit_btn.png')
watch_img = pygame.image.load('img/watch_video2.png').convert_alpha()
answer_img = pygame.image.load('img/solve_question2.png').convert_alpha()

#load yaml for questions
with open("questions.yaml", "r") as file:
    question_data = yaml.safe_load(file)

#load sounds
pygame.mixer.music.load('img/music.wav')
pygame.mixer.music.play(-1, 0.0, 5000)
coin_fx = pygame.mixer.Sound('img/coin.wav')
coin_fx.set_volume(0.5)
jump_fx = pygame.mixer.Sound('img/jump.wav')
jump_fx.set_volume(0.5)
game_over_fx = pygame.mixer.Sound('img/game_over.wav')
game_over_fx.set_volume(0.5)

# Function to draw input field
def draw_input_field(x, y, width, height, text, active, is_password=False):
    color = light_gray if active else gray
    pygame.draw.rect(screen, color, (x, y, width, height), border_radius=5)
    pygame.draw.rect(screen, black, (x, y, width, height), 2, border_radius=5)
    
    # Display text or asterisks for password
    display_text = "*" * len(text) if is_password else text
    text_surface = input_font.render(display_text, True, black)
    text_rect = text_surface.get_rect(midleft=(x + 10, y + height // 2))
    screen.blit(text_surface, text_rect)
    
    return pygame.Rect(x, y, width, height)

# Function to draw button
def draw_button_with_text(x, y, w, h, text, font, color, bg_color, surface):
    rect = pygame.Rect(x, y, w, h)
    pygame.draw.rect(surface, bg_color, rect, border_radius=12)
    pygame.draw.rect(surface, (0, 0, 0), rect, 2, border_radius=12)
    text_surf = font.render(text, True, color)
    text_rect = text_surf.get_rect(center=rect.center)
    surface.blit(text_surf, text_rect)
    return rect

# Function to draw text
def draw_text(text, font, text_col, center_x, y):
    lines = text.split('\n')
    for i, line in enumerate(lines):
        text_surf = font.render(line, True, text_col)
        text_rect = text_surf.get_rect(center=(center_x, y + i * (text_surf.get_height() + 10)))
        screen.blit(text_surf, text_rect)

# Function to draw wrapped text
def draw_wrapped_text(text, font, color, x, y, max_width, surface, line_spacing=5):
    words = text.split(' ')
    lines = []
    current_line = ''

    for word in words:
        test_line = current_line + word + ' '
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + ' '
    lines.append(current_line)  # last line

    for i, line in enumerate(lines):
        text_surface = font.render(line.strip(), True, color)
        surface.blit(text_surface, (x, y + i * (font.get_height() + line_spacing)))

# Function to reset level
def reset_level(level):
    player.reset(100, screen_height - 130)
    blob_group.empty()
    platform_group.empty()
    coin_group.empty()
    lava_group.empty()
    exit_group.empty()

    #load in level data and create world
    if path.exists(f'level{level}_data'):
        pickle_in = open(f'level{level}_data', 'rb')
        world_data = pickle.load(pickle_in)
    world = World(world_data)
    #create dummy coin for showing the score
    score_coin = Coin(tile_size // 2, tile_size // 2)
    coin_group.add(score_coin)
    return world

# Function to handle authentication screen
def handle_auth_screen():
    global auth_state, current_user, username_input, password_input, active_input, auth_message
    
    # Draw background
    screen.blit(bg_img, (0, 0))
    screen.blit(sun_img, (100, 100))
    
    # Draw title
    title = "Sign In" if auth_state == "login" else "Create Account"
    draw_text(title, font, blue, screen_width // 2, 100)
    
    # Draw input fields
    username_rect = draw_input_field(
        screen_width // 2 - 150, 
        250, 
        300, 
        40, 
        username_input, 
        active_input == "username"
    )
    
    password_rect = draw_input_field(
        screen_width // 2 - 150, 
        320, 
        300, 
        40, 
        password_input, 
        active_input == "password",
        is_password=True
    )
    
    # Draw labels
    draw_text("Username:", input_font, black, screen_width // 2 - 200, 260)
    draw_text("Password:", input_font, black, screen_width // 2 - 200, 330)
    
    # Draw buttons
    if auth_state == "login":
        # Login button
        login_rect = draw_button_with_text(
            screen_width // 2 - 150,
            400,
            300,
            50,
            "Sign In",
            font_score,
            white,
            dark_blue,
            screen
        )
        
        # Register button
        register_rect = draw_button_with_text(
            screen_width // 2 - 150,
            480,
            300,
            50,
            "Create Account",
            font_score,
            white,
            dark_blue,
            screen
        )
    else:
        # Create account button
        create_rect = draw_button_with_text(
            screen_width // 2 - 150,
            400,
            300,
            50,
            "Create Account",
            font_score,
            white,
            dark_blue,
            screen
        )
        
        # Back to login button
        back_rect = draw_button_with_text(
            screen_width // 2 - 150,
            480,
            300,
            50,
            "Back to Login",
            font_score,
            white,
            dark_blue,
            screen
        )
    
    # Draw message if any
    if auth_message:
        color = green if "success" in auth_message.lower() else red
        draw_text(auth_message, font_score, color, screen_width // 2, 550)
    
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check if username field is clicked
            if username_rect.collidepoint(event.pos):
                active_input = "username"
            
            # Check if password field is clicked
            elif password_rect.collidepoint(event.pos):
                active_input = "password"
            
            # Handle button clicks
            elif auth_state == "login":
                if login_rect.collidepoint(event.pos):
                    # Attempt to sign in
                    success, result = auth.sign_in(username_input, password_input)
                    if success:
                        current_user = result
                        auth_state = "game"
                        main_menu = False
                    else:
                        auth_message = result
                
                elif register_rect.collidepoint(event.pos):
                    # Switch to register screen
                    auth_state = "register"
                    auth_message = ""
            
            else:  # Register screen
                if create_rect.collidepoint(event.pos):
                    # Attempt to create account
                    success, message = auth.create_account(username_input, password_input)
                    auth_message = message
                    if success:
                        # Switch back to login screen
                        auth_state = "login"
                        username_input = ""
                        password_input = ""
                
                elif back_rect.collidepoint(event.pos):
                    # Switch back to login screen
                    auth_state = "login"
                    auth_message = ""
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB:
                # Switch between input fields
                active_input = "password" if active_input == "username" else "username"
            
            elif event.key == pygame.K_RETURN:
                # Submit form
                if auth_state == "login":
                    success, result = auth.sign_in(username_input, password_input)
                    if success:
                        current_user = result
                        auth_state = "game"
                        main_menu = False
                    else:
                        auth_message = result
                else:
                    success, message = auth.create_account(username_input, password_input)
                    auth_message = message
                    if success:
                        auth_state = "login"
                        username_input = ""
                        password_input = ""
            
            elif event.key == pygame.K_BACKSPACE:
                # Handle backspace
                if active_input == "username":
                    username_input = username_input[:-1]
                else:
                    password_input = password_input[:-1]
            
            else:
                # Add character to active input
                if active_input == "username":
                    username_input += event.unicode
                else:
                    password_input += event.unicode
    
    return True

class Button():
	def __init__(self, x, y, image):
		self.image = image
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.clicked = False

	def draw(self):
		action = False

		#get mouse position
		pos = pygame.mouse.get_pos()

		#check mouseover and clicked conditions
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				action = True
				self.clicked = True

		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False


		#draw button
		screen.blit(self.image, self.rect)

		return action


class Player():
	def __init__(self, x, y):
		self.reset(x, y)

	def update(self, game_over):
		dx = 0
		dy = 0
		walk_cooldown = 5
		col_thresh = 20

		if game_over == 0:
			#get keypresses
			key = pygame.key.get_pressed()
			if key[pygame.K_SPACE] and self.jumped == False and self.in_air == False:
				jump_fx.play()
				self.vel_y = -15
				self.jumped = True
			if key[pygame.K_SPACE] == False:
				self.jumped = False
			if key[pygame.K_LEFT]:
				dx -= 5
				self.counter += 1
				self.direction = -1
			if key[pygame.K_RIGHT]:
				dx += 5
				self.counter += 1
				self.direction = 1
			if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False:
				self.counter = 0
				self.index = 0
				if self.direction == 1:
					self.image = self.images_right[self.index]
				if self.direction == -1:
					self.image = self.images_left[self.index]


			#handle animation
			if self.counter > walk_cooldown:
				self.counter = 0	
				self.index += 1
				if self.index >= len(self.images_right):
					self.index = 0
				if self.direction == 1:
					self.image = self.images_right[self.index]
				if self.direction == -1:
					self.image = self.images_left[self.index]


			#add gravity
			self.vel_y += 1
			if self.vel_y > 10:
				self.vel_y = 10
			dy += self.vel_y

			#check for collision
			self.in_air = True
			for tile in world.tile_list:
				#check for collision in x direction
				if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
					dx = 0
				#check for collision in y direction
				if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
					#check if below the ground i.e. jumping
					if self.vel_y < 0:
						dy = tile[1].bottom - self.rect.top
						self.vel_y = 0
					#check if above the ground i.e. falling
					elif self.vel_y >= 0:
						dy = tile[1].top - self.rect.bottom
						self.vel_y = 0
						self.in_air = False


			#check for collision with enemies
			if pygame.sprite.spritecollide(self, blob_group, False):
				game_over = -1
				game_over_fx.play()

			#check for collision with lava
			if pygame.sprite.spritecollide(self, lava_group, False):
				game_over = -1
				game_over_fx.play()

			#check for collision with exit
			if pygame.sprite.spritecollide(self, exit_group, False):
				game_over = 1


			#check for collision with platforms
			for platform in platform_group:
				#collision in the x direction
				if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
					dx = 0
				#collision in the y direction
				if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
					#check if below platform
					if abs((self.rect.top + dy) - platform.rect.bottom) < col_thresh:
						self.vel_y = 0
						dy = platform.rect.bottom - self.rect.top
					#check if above platform
					elif abs((self.rect.bottom + dy) - platform.rect.top) < col_thresh:
						self.rect.bottom = platform.rect.top - 1
						self.in_air = False
						dy = 0
					#move sideways with the platform
					if platform.move_x != 0:
						self.rect.x += platform.move_direction


			#update player coordinates
			self.rect.x += dx
			self.rect.y += dy


		elif game_over == -1:
			self.image = self.dead_image
			global show_continue_prompt
			show_continue_prompt = True
			if self.rect.y > 200:
				self.rect.y -= 5

		#draw player onto screen
		screen.blit(self.image, self.rect)

		return game_over


	def reset(self, x, y):
		self.images_right = []
		self.images_left = []
		self.index = 0
		self.counter = 0
		for num in range(1, 5):
			img_right = pygame.image.load(f'img/guy{num}.png')
			img_right = pygame.transform.scale(img_right, (40, 80))
			img_left = pygame.transform.flip(img_right, True, False)
			self.images_right.append(img_right)
			self.images_left.append(img_left)
		self.dead_image = pygame.image.load('img/ghost.png')
		self.image = self.images_right[self.index]
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.width = self.image.get_width()
		self.height = self.image.get_height()
		self.vel_y = 0
		self.jumped = False
		self.direction = 0
		self.in_air = True



class World():
	def __init__(self, data):
		self.tile_list = []

		#load images
		dirt_img = pygame.image.load('img/dirt.png')
		grass_img = pygame.image.load('img/grass.png')

		row_count = 0
		for row in data:
			col_count = 0
			for tile in row:
				if tile == 1:
					img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
					img_rect = img.get_rect()
					img_rect.x = col_count * tile_size
					img_rect.y = row_count * tile_size
					tile = (img, img_rect)
					self.tile_list.append(tile)
				if tile == 2:
					img = pygame.transform.scale(grass_img, (tile_size, tile_size))
					img_rect = img.get_rect()
					img_rect.x = col_count * tile_size
					img_rect.y = row_count * tile_size
					tile = (img, img_rect)
					self.tile_list.append(tile)
				if tile == 3:
					blob = Enemy(col_count * tile_size, row_count * tile_size + 15)
					blob_group.add(blob)
				if tile == 4:
					platform = Platform(col_count * tile_size, row_count * tile_size, 1, 0)
					platform_group.add(platform)
				if tile == 5:
					platform = Platform(col_count * tile_size, row_count * tile_size, 0, 1)
					platform_group.add(platform)
				if tile == 6:
					lava = Lava(col_count * tile_size, row_count * tile_size + (tile_size // 2))
					lava_group.add(lava)
				if tile == 7:
					coin = Coin(col_count * tile_size + (tile_size // 2), row_count * tile_size + (tile_size // 2))
					coin_group.add(coin)
				if tile == 8:
					exit = Exit(col_count * tile_size, row_count * tile_size - (tile_size // 2))
					exit_group.add(exit)
				col_count += 1
			row_count += 1


	def draw(self):
		for tile in self.tile_list:
			screen.blit(tile[0], tile[1])



class Enemy(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load('img/blob.png')
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.move_direction = 1
		self.move_counter = 0

	def update(self):
		self.rect.x += self.move_direction
		self.move_counter += 1
		if abs(self.move_counter) > 50:
			self.move_direction *= -1
			self.move_counter *= -1


class Platform(pygame.sprite.Sprite):
	def __init__(self, x, y, move_x, move_y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('img/platform.png')
		self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.move_counter = 0
		self.move_direction = 1
		self.move_x = move_x
		self.move_y = move_y


	def update(self):
		self.rect.x += self.move_direction * self.move_x
		self.rect.y += self.move_direction * self.move_y
		self.move_counter += 1
		if abs(self.move_counter) > 50:
			self.move_direction *= -1
			self.move_counter *= -1





class Lava(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('img/lava.png')
		self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y


class Coin(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('img/coin.png')
		self.image = pygame.transform.scale(img, (tile_size // 2, tile_size // 2))
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)


class Exit(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('img/exit.png')
		self.image = pygame.transform.scale(img, (tile_size, int(tile_size * 1.5)))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y



player = Player(100, screen_height - 130)

blob_group = pygame.sprite.Group()
platform_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

#create dummy coin for showing the score
score_coin = Coin(tile_size // 2, tile_size // 2)
coin_group.add(score_coin)

#load in level data and create world
if path.exists(f'level{level}_data'):
	pickle_in = open(f'level{level}_data', 'rb')
	world_data = pickle.load(pickle_in)
world = World(world_data)


#create buttons
restart_button = Button(screen_width // 2 - 50, screen_height // 2 + 100, restart_img)
start_button = Button(screen_width // 2 - 350, screen_height // 2, start_img)
exit_button = Button(screen_width // 2 + 150, screen_height // 2, exit_img)
watch_button = Button(screen_width // 2 + - 350, screen_height // 2 + 100, watch_img)
answer_button = Button(screen_width // 2 + 150, screen_height // 2 + 100, answer_img)


run = True
while run:

	clock.tick(fps)

	screen.blit(bg_img, (0, 0))
	screen.blit(sun_img, (100, 100))

	if auth_state == "login" or auth_state == "register":
		run = handle_auth_screen()
	elif main_menu == True:
		if exit_button.draw():
			run = False
		if start_button.draw():
			main_menu = False
	else:
		world.draw()

		if game_over == 0:
			blob_group.update()
			platform_group.update()
			#update score
			#check if a coin has been collected
			if pygame.sprite.spritecollide(player, coin_group, True):
				score += 1
				coin_fx.play()
			draw_text('X ' + str(score), font_score, white, tile_size - 10, 10)
			
			# Display username and high score
			if current_user:
				draw_text(f"Player: {current_user['username']}", font_score, white, screen_width - 150, 10)
				draw_text(f"High Score: {current_user['high_score']}", font_score, white, screen_width - 150, 40)
		
		blob_group.draw(screen)
		platform_group.draw(screen)
		lava_group.draw(screen)
		coin_group.draw(screen)
		exit_group.draw(screen)

		if show_feedback == False:
			game_over = player.update(game_over)

		#if player has died
		if game_over == -1:
			show_game_over_window = True
			game_over_fx.play()
			
		if show_game_over_window:
			# Draw semi-transparent overlay
			overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
			overlay.fill((0, 0, 0, 128))
			screen.blit(overlay, (0, 0))
			
			# Draw game over window
			draw_text('GAME OVER!', font, blue, screen_width // 2, screen_height // 2 - 100)
			
			if not show_hint_options:
				# Draw hint and restart buttons
				# Create text-based hint button
				hint_button_rect = draw_button_with_text(
					screen_width // 2 - 350, 
					screen_height // 2 + 100, 
					300, 
					50, 
					"HINT", 
					font_score, 
					white, 
					dark_blue, 
					screen
				)
				
				# Check if hint button is clicked
				pos = pygame.mouse.get_pos()
				if hint_button_rect.collidepoint(pos) and pygame.mouse.get_pressed()[0] == 1:
					show_hint_options = True
					pygame.time.delay(300)  # Add a small delay to prevent multiple clicks
				
				# Create text-based restart button
				restart_button_rect = draw_button_with_text(
					screen_width // 2 + 50, 
					screen_height // 2 + 100, 
					300, 
					50, 
					"RESTART", 
					font_score, 
					white, 
					dark_blue, 
					screen
				)
				
				# Check if restart button is clicked
				if restart_button_rect.collidepoint(pos) and pygame.mouse.get_pressed()[0] == 1:
					show_game_over_window = False
					level = 0
					# reset level
					world_data = []
					world = reset_level(level)
					game_over = 0
					score = 0
					pygame.time.delay(300)  # Add a small delay to prevent multiple clicks
			else:
				# Draw hint options (video and answer game)
				draw_text('Choose a hint option:', font_score, blue, screen_width // 2, screen_height // 2 - 50)
				
				# Create text-based video button
				video_button_rect = draw_button_with_text(
					screen_width // 2 - 350, 
					screen_height // 2 + 100, 
					300, 
					50, 
					"WATCH VIDEO", 
					font_score, 
					white, 
					dark_blue, 
					screen
				)
				
				# Create text-based answer button
				answer_button_rect = draw_button_with_text(
					screen_width // 2 + 50, 
					screen_height // 2 + 100, 
					300, 
					50, 
					"ANSWER QUESTION", 
					font_score, 
					white, 
					dark_blue, 
					screen
				)
				
				# Check if video button is clicked
				pos = pygame.mouse.get_pos()
				if video_button_rect.collidepoint(pos) and pygame.mouse.get_pressed()[0] == 1:
					show_game_over_window = False
					show_hint_options = False
					# Select a random video from the array
					random_video_index = randrange(0, len(video_links))
					selected_video = video_links[random_video_index]
					# Open video in browser
					webbrowser.open(selected_video)
					# Continue at the same level after watching video
					world_data = []
					world = reset_level(level)
					game_over = 0
					pygame.time.delay(300)  # Add a small delay to prevent multiple clicks
					
				# Check if answer button is clicked
				if answer_button_rect.collidepoint(pos) and pygame.mouse.get_pressed()[0] == 1:
					show_game_over_window = False
					show_hint_options = False
					question_mode = True
					current_question_index = randrange(0, len(question_data['questions']))
					current_question = question_data['questions'][current_question_index]
					pygame.time.delay(300)  # Add a small delay to prevent multiple clicks

		if question_mode and current_question:
			question = current_question['question']
			answer = int(current_question['answer'])

			screen.blit(bg_img, (0, 0))
			screen.blit(sun_img, (100, 100))
			# Display question
			draw_wrapped_text(question, font, blue, 100, 230, 800, screen)

			# Display options
			option_buttons = []
			for i, option in enumerate(current_question["options"]):
				option_text = option_font.render(option, True, blue)
				option_button = Button(screen_width // 2 + - 350, screen_height // 2 + 100 + (i*100), option_text)
				option_buttons.append(option_button)
				if option_button.draw():
					if answer == i:
						# Continue at the same level when answered correctly
						world_data = []
						world = reset_level(level)
						game_over = 0
						show_hint_options = False  # Ensure hint options are not shown
						show_game_over_window = False  # Ensure game over window is closed
					else:
						show_feedback = True
						level = 0
						# reset level
						world_data = []
						world = reset_level(level)
						game_over = 0
						score = 0
						show_game_over_window = False  # Ensure game over window is closed
				
					current_question = None
					question_mode = False
					pygame.time.delay(300)  # Add a small delay to prevent multiple clicks
			# Select a random question from the list

		if show_feedback:
			draw_text('Wrong Answer!\nTry again from starting', font, blue, screen_width // 2, screen_height // 2 - 100)
			if restart_button.draw():
				show_feedback = False
				level = 0
				# reset level
				world_data = []
				world = reset_level(level)
				game_over = 0
				score = 0
		#if player has completed the level
		if game_over == 1:
			#reset game and go to next level
			level += 1
			if level <= max_levels:
				#reset level
				world_data = []
				world = reset_level(level)
				game_over = 0
			else:
				draw_text('YOU WIN!', font, blue, (screen_width // 2) - 140, screen_height // 2)
				if restart_button.draw():
					level = 0
					#reset level
					world_data = []
					world = reset_level(level)
					game_over = 0
					score = 0

			# Update high score when game is over
			if game_over == 1 and current_user:
				auth.update_high_score(current_user['username'], score)

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False

	pygame.display.update()

pygame.quit()