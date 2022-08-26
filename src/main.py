import os
import sys
import math
import time
import pygame
current_path = os.getcwd()
import pymunk as pm
from characters import Bird
from level import Level

#importing all pygame modules
pygame.init()

#setting screen size
screen = pygame.display.set_mode((1200, 650))

#creating image objects by importing from images folder .. convert_apha for fast blitting .. refer documentation for more details
redbird = pygame.image.load(
    "../resources/images/red-bird3.png").convert_alpha()
background2 = pygame.image.load(
    "../resources/images/background3.png").convert_alpha()
sling_image = pygame.image.load(
    "../resources/images/sling-3.png").convert_alpha()
full_sprite = pygame.image.load(
    "../resources/images/full-sprite.png").convert_alpha()
#creating a rect to pass into subsurface function for cropping and saving a rectangle at that position of the surface or image
rect = pygame.Rect(181, 1050, 50, 50)
cropped = full_sprite.subsurface(rect).copy()
#scaling the pig_image to required size
pig_image = pygame.transform.scale(cropped, (30, 30))
buttons = pygame.image.load(
    "../resources/images/selected-buttons.png").convert_alpha()
pig_happy = pygame.image.load(
    "../resources/images/pig_failed.png").convert_alpha()
stars = pygame.image.load(
    "../resources/images/stars-edited.png").convert_alpha()
#cropping and storing images used in the game
rect = pygame.Rect(0, 0, 200, 200)
star1 = stars.subsurface(rect).copy()
rect = pygame.Rect(204, 0, 200, 200)
star2 = stars.subsurface(rect).copy()
rect = pygame.Rect(426, 0, 200, 200)
star3 = stars.subsurface(rect).copy()
rect = pygame.Rect(164, 10, 60, 60)
pause_button = buttons.subsurface(rect).copy()
rect = pygame.Rect(24, 4, 100, 100)
replay_button = buttons.subsurface(rect).copy()
rect = pygame.Rect(142, 365, 130, 100)
next_button = buttons.subsurface(rect).copy()
clock = pygame.time.Clock()
rect = pygame.Rect(18, 212, 100, 100)
play_button = buttons.subsurface(rect).copy()
#clock for FPS
clock = pygame.time.Clock()
running = True
# Building our space object. We will put our other objects (like birds and pigs) in this space for simulation
space = pm.Space()
#setting the gravity in our space using gravity method. It takes a tuple with gravity in x and y directions
space.gravity = (0.0, -700.0)
#Initializing object variables as they will be used later in our game. The names are essentially the objects they will be having.
pigs = []
birds = []
balls = []
polys = []
beams = []
columns = []
poly_points = []
ball_number = 0
polys_dict = {}
mouse_distance = 0
rope_lenght = 90
angle = 0
x_mouse = 0
y_mouse = 0
count = 0
mouse_pressed = False
t1 = 0
tick_to_next_circle = 10
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
sling_x, sling_y = 135, 450
sling2_x, sling2_y = 160, 450
score = 0
game_state = 0
bird_path = []
counter = 0
restart_counter = False
bonus_score_once = True
bold_font = pygame.font.SysFont("arial", 30, bold=True)
bold_font2 = pygame.font.SysFont("arial", 40, bold=True)
bold_font3 = pygame.font.SysFont("arial", 50, bold=True)
wall = False

# Unlike bird which is a solid body, floor is just a line. It is also static as it does not move. These 3 lines create the list. The tuple represents initial and final positions.
static_body = pm.Body(body_type=pm.Body.STATIC)
static_lines = [pm.Segment(static_body, (0.0, 060.0), (1200.0, 060.0), 0.0)]
static_lines1 = [pm.Segment(static_body, (1200.0, 060.0), (1200.0, 800.0), 0.0)]
#loop for floor line
for line in static_lines:
    line.elasticity = 0.95
    line.friction = 1
    line.collision_type = 3
#loop for line that will be construted for right vertical edge. Press w in the game to see.
for line in static_lines1:
    line.elasticity = 0.95
    line.friction = 1
    line.collision_type = 3
#Adding floor line to our space. Vertical edge is added when player presses w. This just increases the difficulty of game.
space.add(static_lines)


def to_pygame(p):
    """Convert pymunk to pygame coordinates. For objects in space, we extract their location using pymunk. Those coordinates are converted because pymunk has a different convention."""
    return int(p.x), int(-p.y+600)


def vector(p0, p1):
    """Return the vector joining p0 and p1. It points from p0 to p1. This function is used for angle calulation while sling is acting.
    p0 = (xo,yo), p1 = (x1,y1)"""
    a = p1[0] - p0[0]
    b = p1[1] - p0[1]
    return (a, b)

#This function is used for angle calulation while sling is acting
def unit_vector(v):
    """Return the unit vector of the points
    v = (a,b)"""
    h = ((v[0]**2)+(v[1]**2))**0.5
    if h == 0:
        h = 0.000000000000001
    ua = v[0] / h
    ub = v[1] / h
    return (ua, ub)

#This function is used for angle calulation while sling is acting
def distance(xo, yo, x, y):
    """distance between points"""
    dx = x - xo
    dy = y - yo
    d = ((dx ** 2) + (dy ** 2)) ** 0.5
    return d

#loading the muscic in our game
def load_music():
    """Load the music"""
    song1 = '../resources/sounds/angry-birds.ogg'
    pygame.mixer.music.load(song1)
    pygame.mixer.music.play(-1)

#this function will draw the 2 black lines of sling, the bird as it is moved with the mouse as well as calculate the angle of bird when it was released. It uses vector mathematics for doing these things.
def sling_action():
    """Set up sling behavior"""
    global mouse_distance
    global rope_lenght
    global angle
    global x_mouse
    global y_mouse
    # Fixing bird to the sling rope
    #we created sling_x and sling_y constants above in our code. Hence one point in v vector is fixed.
    v = vector((sling_x, sling_y), (x_mouse, y_mouse))
    #now is the maths. Use copy-pen for visualization
    uv = unit_vector(v)
    uv1 = uv[0]
    uv2 = uv[1]
    mouse_distance = distance(sling_x, sling_y, x_mouse, y_mouse)
    pu = (uv1*rope_lenght+sling_x, uv2*rope_lenght+sling_y)
    bigger_rope = 102
    #20 is half the width and height of bird image. This subtraction is done because image is not a point object.
    x_redbird = x_mouse - 20
    y_redbird = y_mouse - 20
    #if mouse is far from bird we use the unit vector and take magnitude of rope_lenght!
    if mouse_distance > rope_lenght:
        pux, puy = pu
        pux -= 20
        puy -= 20
        pul = pux, puy
        screen.blit(redbird, pul)
        pu2 = (uv1*bigger_rope+sling_x, uv2*bigger_rope+sling_y)
        #drawing the lines and bird at the position
        pygame.draw.line(screen, (0, 0, 0), (sling2_x, sling2_y), pu2, 5)
        screen.blit(redbird, pul)
        pygame.draw.line(screen, (0, 0, 0), (sling_x, sling_y), pu2, 5)
    else:
        mouse_distance += 10
        pu3 = (uv1*mouse_distance+sling_x, uv2*mouse_distance+sling_y)
        pygame.draw.line(screen, (0, 0, 0), (sling2_x, sling2_y), pu3, 5)
        screen.blit(redbird, (x_redbird, y_redbird))
        pygame.draw.line(screen, (0, 0, 0), (sling_x, sling_y), pu3, 5)
    # Angle of bird before launch .. this direction is the direction of impulse
    dy = y_mouse - sling_y
    dx = x_mouse - sling_x
    if dx == 0:
        dx = 0.00000000000001
    angle = math.atan((float(dy))/dx)

#basic fonts and image rendering for drawing score and images
def draw_level_cleared():
    """Draw level cleared"""
    global game_state
    global bonus_score_once
    global score
    # we get the score from another function which deals with collision! dont worry about it here.
    level_cleared = bold_font3.render("Level Cleared!", 1, WHITE)
    score_level_cleared = bold_font2.render(str(score), 1, WHITE)
    #checking if level is completed. The list pigs has pig objects that are in space. We append this list in main loop.
    if level.number_of_birds >= 0 and len(pigs) == 0:
        #bonus score logic
        #bonus_score_once was made true while declaring variables for the game
        if bonus_score_once:
            score += (level.number_of_birds-1) * 10000
        # changing it to false. It will be made true again when a level is initialized.
        bonus_score_once = False
        #game_state variables are used to check the state of game. For eg- after level is completed and before another level is started the state is 4.
        game_state = 4
        rect = pygame.Rect(300, 0, 600, 800)
        pygame.draw.rect(screen, (128,0,128), rect)
        screen.blit(level_cleared, (450, 90))
        #game logic
        if score >= level.one_star and score <= level.two_star:
            screen.blit(star1, (310, 190))
        if score >= level.two_star and score <= level.three_star:
            screen.blit(star1, (310, 190))
            screen.blit(star2, (500, 170))
        if score >= level.three_star:
            screen.blit(star1, (310, 190))
            screen.blit(star2, (500, 170))
            screen.blit(star3, (700, 200))
        screen.blit(score_level_cleared, (550, 400))
        screen.blit(replay_button, (510, 480))
        screen.blit(next_button, (620, 480))

#same explanation as above function
def draw_level_failed():
    """Draw level failed"""
    global game_state
    failed = bold_font3.render("Level Failed", 1, WHITE)
    # t2 is the time at the release of bird. We subtract it from current time. 5 seconds after last bird is shot, level is failed
    if level.number_of_birds <= 0 and time.time() - t2 > 5 and len(pigs) > 0:
        #state 3 is after level fails and before level is restarted
        game_state = 3
        rect = pygame.Rect(300, 0, 600, 800)
        pygame.draw.rect(screen, BLACK, rect)
        screen.blit(failed, (450, 90))
        screen.blit(pig_happy, (380, 120))
        screen.blit(replay_button, (520, 460))

#at restart we have to reset all our variables that we created.
def restart():
    """Delete all objects of the level"""
    pigs_to_remove = []
    birds_to_remove = []
    columns_to_remove = []
    beams_to_remove = []
    #why first append in another list and then delete? why not direct?
    for pig in pigs:
        pigs_to_remove.append(pig)
    for pig in pigs_to_remove:
        space.remove(pig.shape, pig.shape.body)
        pigs.remove(pig)
    for bird in birds:
        birds_to_remove.append(bird)
    for bird in birds_to_remove:
        space.remove(bird.shape, bird.shape.body)
        birds.remove(bird)
    for column in columns:
        columns_to_remove.append(column)
    for column in columns_to_remove:
        space.remove(column.shape, column.shape.body)
        columns.remove(column)
    for beam in beams:
        beams_to_remove.append(beam)
    for beam in beams_to_remove:
        space.remove(beam.shape, beam.shape.body)
        beams.remove(beam)

# this function needs argument which do not change. We do not call this function in our main loop. We write a single line of code before our main loop and pymunk runs this function each time collision happens between bird and pig. More details are written before the main loop where this function is called.
def post_solve_bird_pig(arbiter, space, _):
    """Collision between bird and pig"""
    surface=screen
    a, b = arbiter.shapes
    bird_body = a.body
    pig_body = b.body
    #changing from pymunk to pygame coordinates
    p = to_pygame(bird_body.position)
    p2 = to_pygame(pig_body.position)
    r = 30
    #drawing these circles to create an explosion effecct
    pygame.draw.circle(surface, BLACK, p, r, 4)
    pygame.draw.circle(surface, RED, p2, r, 4)
    pigs_to_remove = []
    #removing the pig with which the bird collided from space and pig list
    for pig in pigs:
        if pig_body == pig.body:
            pigs_to_remove.append(pig)
            global score
            #incrementing the score
            score += 10000
    for pig in pigs_to_remove:
        space.remove(pig.shape, pig.shape.body)
        pigs.remove(pig)


def post_solve_bird_wood(arbiter, space, _):
    """Collision between bird and wood"""
    poly_to_remove = []
    #defining the threshold of internsity of collision above which wood dissapears
    if arbiter.total_impulse.length > 1100:
        a, b = arbiter.shapes
        #checking for both columns and beams. Both of them are in a single function because whatever happens after collision is same for them.
        for column in columns:
            if b == column.shape:
                poly_to_remove.append(column)
        for beam in beams:
            if b == beam.shape:
                poly_to_remove.append(beam)
        for poly in poly_to_remove:
            if poly in columns:
                columns.remove(poly)
            if poly in beams:
                beams.remove(poly)
        #removing from space
        space.remove(b, b.body)
        global score
        score += 5000

#same explanation as above 2 functions
def post_solve_pig_wood(arbiter, space, _):
    """Collision between pig and wood"""
    pigs_to_remove = []
    if arbiter.total_impulse.length > 700:
        pig_shape, wood_shape = arbiter.shapes
        for pig in pigs:
            if pig_shape == pig.shape:
                global score
                score += 10000
                pigs_to_remove.append(pig)
    for pig in pigs_to_remove:
        space.remove(pig.shape, pig.shape.body)
        pigs.remove(pig)


# bird and pigs, these 0,1 are collision type of bird and wood respectively(defined in their class in characters and polygon file)
space.add_collision_handler(0, 1).post_solve=post_solve_bird_pig
# bird and wood
#this runs the function post_solve_bird_wood (defined above) every time collision happens between shapes with collision type 0 and 2!
space.add_collision_handler(0, 2).post_solve=post_solve_bird_wood
# pig and wood
space.add_collision_handler(1, 2).post_solve=post_solve_pig_wood
load_music()
#creating a level class instance .. all the passed lists are empty initially
level = Level(pigs, columns, beams, space)
#changing the level number to 0 .. this does not draw anything on screen..
level.number = 0
#this function calls build_0 function inside the class. That function appends pigs, columns, beams list according to that level.
level.load_level()

while running:
    # Input handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_w:
            # Toggle wall .. this variable is initialized as false
            if wall:
                space.remove(static_lines1)
                wall = False
            else:
                space.add(static_lines1)
                wall = True
        #if mouse is pressed near the the bird
        if (pygame.mouse.get_pressed()[0] and x_mouse > 100 and x_mouse < 250 and y_mouse > 370 and y_mouse < 550):
            mouse_pressed = True
        if (event.type == pygame.MOUSEBUTTONUP and event.button == 1 and mouse_pressed):
            # Release new bird
            mouse_pressed = False
            #modyfing numer of birds. Initially in every level it is 4.
            if level.number_of_birds > 0:
                level.number_of_birds -= 1
                #t1 is the time when bird is released!
                t1 = time.time()*1000
                #coordinates from which bird is released. When we move our mouse it may seem like we are changing the start point of the bird but there we are only setting the angle!
                xo = 154
                yo = 156
                # mouse_distance initialized as 0
                if mouse_distance > rope_lenght:
                    mouse_distance = rope_lenght
                if x_mouse < sling_x+5:
                    #adds a bird to space
                    bird = Bird(mouse_distance, angle, xo, yo, space)
                    birds.append(bird)
                else:
                    # giving negative distance will cause the initial launch of bird in opposite direction
                    bird = Bird(-mouse_distance, angle, xo, yo, space)
                    birds.append(bird)
                if level.number_of_birds == 0:
                    t2 = time.time()
        #this condition is true if game left button is clicked
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            #checking if clicked on pause button
            if (x_mouse < 60 and y_mouse < 155 and y_mouse > 90):
                #state 1 is paused state
                game_state = 1
            #if game is paused we check whether click on resume or restart
            if game_state == 1:
                if x_mouse > 500 and y_mouse > 200 and y_mouse < 300:
                    # Resume in the paused screen
                    game_state = 0

                if x_mouse > 500 and y_mouse > 300:
                    # Restart in the paused screen
                    restart()
                    level.load_level()
                    game_state = 0
                    bird_path = []
            #we check if restart is clicked in state 3 (after level fails)
            if game_state == 3:
                # Restart in the failed level screen
                if x_mouse > 500 and x_mouse < 620 and y_mouse > 450:
                    #in restart we only empty all the lists
                    restart()
                    #calling the level again .. this fills up our lists
                    level.load_level()
                    #state 0 is when player is playing
                    game_state = 0
                    bird_path = []
                    score = 0
            if game_state == 4:
                # Build next level
                if x_mouse > 610 and y_mouse > 450:
                    #making the lists empty
                    restart()
                    level.number += 1
                    game_state = 0
                    level.load_level()
                    score = 0
                    bird_path = []
                    bonus_score_once = True
                if x_mouse < 610 and x_mouse > 500 and y_mouse > 450:
                    # Restart in the level cleared screen
                    restart()
                    level.load_level()
                    game_state = 0
                    bird_path = []
                    score = 0
    x_mouse, y_mouse = pygame.mouse.get_pos()
    # Draw background
    screen.fill((130, 200, 100))
    screen.blit(background2, (0, -50))
    # Draw first part of the sling
    rect = pygame.Rect(50, 0, 70, 220)
    screen.blit(sling_image, (138, 420), rect)
    # Draw the trail left behind
    for point in bird_path:
        pygame.draw.circle(screen, WHITE, point, 5, 0)
    # Draw the birds in the wait line
    if level.number_of_birds > 0:
        for i in range(level.number_of_birds-1):
            x = 100 - (i*35)
            screen.blit(redbird, (x, 508))
    # Draw sling behavior
    if mouse_pressed and level.number_of_birds > 0:
        sling_action()
    else:
        #drawing new bird on sling few seconds after previous bird is released
        if time.time()*1000 - t1 > 300 and level.number_of_birds > 0:
            screen.blit(redbird, (130, 426))
        else:
            # draw the rubber band line
            pygame.draw.line(screen, (0, 0, 0), (sling_x, sling_y-8),
                             (sling2_x, sling2_y-7), 5)
    birds_to_remove = []
    pigs_to_remove = []
    counter += 1
    # Drawing the bird image on pymunk's circle by taking it's coordinates!
    for bird in birds:
        if bird.shape.body.position.y < 0:
            birds_to_remove.append(bird)
        p = to_pygame(bird.shape.body.position)
        x, y = p
        x -= 22
        y -= 20
        screen.blit(redbird, (x, y))
        #logic is added so that circles in path are seperated
        if counter >= 3 and time.time() - t1 < 5:
            bird_path.append(p)
            restart_counter = True
    if restart_counter:
        counter = 0
        restart_counter = False
    # Remove birds and pigs
    for bird in birds_to_remove:
        space.remove(bird.shape, bird.shape.body)
        birds.remove(bird)
    for pig in pigs_to_remove:
        space.remove(pig.shape, pig.shape.body)
        pigs.remove(pig)
    # Draw static lines. Without this loop, floor will exist but will be invisible
    for line in static_lines:
        body = line.body
        pv1 = body.position + line.a.rotated(body.angle)
        pv2 = body.position + line.b.rotated(body.angle)
        p1 = to_pygame(pv1)
        p2 = to_pygame(pv2)
        pygame.draw.lines(screen, (150, 150, 150), False, [p1, p2])
    i = 0
    # Draw pigs
    for pig in pigs:
        i += 1

        pig = pig.shape
        if pig.body.position.y < 0:
            pigs_to_remove.append(pig)

        p = to_pygame(pig.body.position)
        x, y = p
        #calculaing the degrees of pig circle rotated
        angle_degrees = math.degrees(pig.body.angle)
        #rotating pig image by same angle
        img = pygame.transform.rotate(pig_image, angle_degrees)
        w,h = img.get_size()
        x -= w*0.5
        y -= h*0.5
        #drawing pig over the circle
        screen.blit(img, (x, y))

    # Draw columns and Beams
    for column in columns:
        column.draw_poly('columns', screen)
    for beam in beams:
        beam.draw_poly('beams', screen)
    # Update the space!
    dt = 1.0/50.0/2. #time after which space updates
    for x in range(2):
        space.step(dt) # make two updates per frame for better stability
    # Drawing second part of the sling
    rect = pygame.Rect(0, 0, 60, 200)
    screen.blit(sling_image, (120, 420), rect)
    # Draw score
    score_font = bold_font.render("SCORE", 1, WHITE)
    number_font = bold_font.render(str(score), 1, WHITE)
    screen.blit(score_font, (1060, 90))
    if score == 0:
        screen.blit(number_font, (1100, 130))
    else:
        screen.blit(number_font, (1060, 130))
    screen.blit(pause_button, (10, 90))
    # Pause option
    if game_state == 1:
        screen.blit(play_button, (500, 200))
        screen.blit(replay_button, (500, 300))
    #we are calling these functions in every iteration. This is why we check the condition for cleared or failed inside the function
    draw_level_cleared()
    draw_level_failed()
    pygame.display.flip()
    clock.tick(50)
    pygame.display.set_caption("Angry Bird")
