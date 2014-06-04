# Source can be found at
# http://stackoverflow.com/questions/14354171/add-scrolling-to-a-platformer-in-pygame

import pygame
from pygame import *

import levels

# FUNCTIONS

def simple_camera(camera, target_rect):
    l, t, _, _ = target_rect # l = left,  t = top
    _, _, w, h = camera      # w = width, h = height
    return Rect(-l+HALF_WIDTH, -t+HALF_HEIGHT, w, h)

def complex_camera(camera, target_rect):
    l, t, _, _ = target_rect
    _, _, w, h = camera
    l, t, _, _ = -l+HALF_WIDTH, -t+HALF_HEIGHT, w, h # center player

    l = min(0, l)                           # stop scrolling at the left edge
    l = max(-(camera.width-WIN_WIDTH), l)   # stop scrolling at the right edge
    t = max(-(camera.height-WIN_HEIGHT), t) # stop scrolling at the bottom
    t = min(0, t)                           # stop scrolling at the top

    return Rect(l, t, w, h)

# CONSTANTS

WIN_WIDTH = 800
WIN_HEIGHT = 640
HALF_WIDTH = int(WIN_WIDTH / 2)
HALF_HEIGHT = int(WIN_HEIGHT / 2)

DISPLAY = (WIN_WIDTH, WIN_HEIGHT)
DEPTH = 32
FLAGS = 0
CAMERA_SLACK = 30

# MAIN FUNCTION

def main(level):
    global cameraX, cameraY
    pygame.init()
    screen = pygame.display.set_mode(DISPLAY, FLAGS, DEPTH)
    pygame.display.set_caption("Use arrows to move!")
    timer = pygame.time.Clock()

    up = down = left = right = running = False
    bg = Surface((32,32))
    bg.convert()
    bg.fill(Color("#000000"))
    entities = pygame.sprite.Group()
    player = Player(32, 32)
    platforms = []

    # LEVELS ARE NOW CREATED IN levels.py  JBF 5/29/14

    x = y = 0

    # build the level
    for row in level:
        for col in row:
            if col == "F":              # JBF - Added another letter for Floor  5/29/14  (Step 1 of 2)
                f = Floor(x, y)
                platforms.append(f)
                entities.add(f)
            if col == "B":              # JBF - Added another letter for Floor  5/29/14  (Step 1 of 2)
                f = Floor2(x, y)
                platforms.append(B)
                entities.add(B)
            if col == "L":              # JBF - Lava  5/29/14 
                l = Lava(x, y)
                platforms.append(l)
                entities.add(l)
            if col == "K":              # JBF - Added another letter for Key  5/29/14 
                k = Key(x, y)           # Note I don't append it to the list of platforms, just add it as an entity
                entities.add(k)
            if col == "P":
                p = Platform(x, y)
                platforms.append(p)
                entities.add(p)
            if col == "E":
                e = ExitBlock(x, y)
                platforms.append(e)
                entities.add(e)
            x += 32
        y += 32
        x = 0

    total_level_width  = len(level[0])*32 # calculate size of level in pixels
    total_level_height = len(level)*32    # maybe make 32 an constant
    camera = Camera(complex_camera, total_level_width, total_level_height)

    entities.add(player)

    done = False

    while not done:
        timer.tick(60)

        for e in pygame.event.get():
            if e.type == QUIT: raise SystemExit, "QUIT"
            if e.type == KEYDOWN and e.key == K_ESCAPE:
                raise SystemExit, "ESCAPE"
            if e.type == KEYDOWN and e.key == K_UP:
                up = True
            if e.type == KEYDOWN and e.key == K_DOWN:
                down = True
            if e.type == KEYDOWN and e.key == K_LEFT:
                left = True
            if e.type == KEYDOWN and e.key == K_RIGHT:
                right = True
            if e.type == KEYDOWN and e.key == K_SPACE:
                running = True

            if e.type == KEYUP and e.key == K_UP:
                up = False
            if e.type == KEYUP and e.key == K_DOWN:
                down = False
            if e.type == KEYUP and e.key == K_RIGHT:
                right = False
            if e.type == KEYUP and e.key == K_LEFT:
                left = False
            if e.type == KEYUP and e.key == K_SPACE:
                running = False

        # draw background
        for y in range(32):
            for x in range(32):
                screen.blit(bg, (x * 32, y * 32))

        camera.update(player) # camera follows player. Note that we could also follow any other sprite

        # update player, draw everything else
        player.update(up, down, left, right, running, platforms, entities)
        #entities.draw(screen)
        for e in entities:
            # apply the offset to each entity.
            # call this for everything that should scroll,
            # which is basically everything other than GUI/HUD/UI
            screen.blit(e.image, camera.apply(e)) 

        pygame.display.update()

        if player.exit:
            done = True

# CLASSES 

class Camera(object):
    def __init__(self, camera_func, width, height):
        self.camera_func = camera_func
        self.state = Rect(0, 0, width, height)

    def apply(self, target):
        return target.rect.move(self.state.topleft)

    def update(self, target):
        self.state = self.camera_func(self.state, target.rect)

class Entity(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

class Player(Entity):
    def __init__(self, x, y):
        Entity.__init__(self)
        self.xvel = 0
        self.yvel = 0
        self.onGround = False
        self.image = Surface((32,32))
        self.image = pygame.image.load("Mario.png")
        self.image.convert()
        self.rect = Rect(x, y, 32, 32)

        self.key = False        # ADDED JBF 5/28/14
        self.exit = False   

    def update(self, up, down, left, right, running, platforms, entities):
        if up:
            # only jump if on the ground
            if self.onGround: self.yvel -= 10
        if down:
            pass
        if running:
            self.xvel = 12
        if left:
            self.xvel = -8
        if right:
            self.xvel = 8
        if not self.onGround:
            # only accelerate with gravity if in the air
            self.yvel += 0.3
            # max falling speed
            if self.yvel > 100: self.yvel = 100
        if not(left or right):
            self.xvel = 0
        # increment in x direction
        self.rect.left += self.xvel
        # do x-axis collisions
        self.collide(self.xvel, 0, platforms)
        # increment in y direction
        self.rect.top += self.yvel
        # assuming we're in the air
        self.onGround = False;
        # do y-axis collisions
        self.collide(0, self.yvel, platforms)
        self.pickup(entities)                  # ADDED JBF 5/28/14

    def collide(self, xvel, yvel, platforms):
        for p in platforms:
            if pygame.sprite.collide_rect(self, p):
                if isinstance(p, ExitBlock):    # If I collided with an ExitBlock..... JBF  5/28/14
                    if self.key:                # ... check if I have the key ....
                        self.exit = True        # Then I'm ready to exit.
                if isinstance(p, Lava):
                    print "Get off the lava, you idiot!"
                if xvel > 0:
                    self.rect.right = p.rect.left
                    #print "collide right"
                if xvel < 0:
                    self.rect.left = p.rect.right
                    #print "collide left"
                if yvel > 0:
                    self.rect.bottom = p.rect.top
                    self.onGround = True
                    self.yvel = 0
                    #print "collide bottom"
                if yvel < 0:
                    self.rect.top = p.rect.bottom
                    #print "collide top"
                    
    def pickup(self, entities):             # ADDED JBF 5/28/14
        for e in entities:
            if pygame.sprite.collide_rect(self, e):
                if isinstance(e, Key):          # If I collided with a key...
                    entities.remove(e)          # Remove the key from the list of entities.
                    print "got the key!"
                    self.key = True             # Set the flag that you now have a key.
                # THIS IS WHERE YOU WOULD CHECK TO SEE IF YOU HIT SOMETHING ELSE, LIKE AN ENEMY, OR A TREASURE

class Platform(Entity):
    def __init__(self, x, y):
        Entity.__init__(self)
        self.image = Surface((32, 32))
        self.image.convert()
        self.image.fill(Color("#DDDDDD"))
        self.rect = Rect(x, y, 32, 32)

    def update(self):
        pass

class Floor(Platform):                    # JBF - Added the Floor class with the floor image 5/29/14  (Step 2 of 2)
    def __init__(self, x, y):
        Platform.__init__(self, x, y)
        self.image = pygame.image.load("floor.png")
        self.image.convert()

    def update(self):
        pass

class Floor2(Platform):                    # JBF - Added the Floor class with the floor image 5/29/14  (Step 2 of 2)
    def __init__(self, x, y):
        Platform.__init__(self, x, y)
        self.image = pygame.image.load("floor2.png")
        self.image.convert()

    def update(self):
        pass

class Lava(Platform):                    # JBF -  5/29/14 
    def __init__(self, x, y):
        Platform.__init__(self, x, y)
        self.image = pygame.image.load("lava.jpeg")
        self.image.convert()

    def update(self):
        pass

class Key(Entity):                    # JBF - Added the Floor class with the floor image 5/29/14  (Step 2 of 2)
    def __init__(self, x, y):
        Entity.__init__(self)
        self.image = pygame.image.load("key.jpeg")
        self.image.convert()
        self.rect = Rect(x, y, 32, 32)

    def update(self):
        pass

class ExitBlock(Platform):
    def __init__(self, x, y):
        Platform.__init__(self, x, y)
        self.image.fill(Color("#0033FF"))

# RUNS THE main() FUNCTION

if __name__ == "__main__":
    main(levels.level1)
    main(levels.level2)
    main(levels.level3)
