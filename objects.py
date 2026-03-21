import pygame as pyg
import random
from pygame.locals import *

win_size = [600, 600]

class Entity:
    def __init__(self, x, y, width, height, color, max_health, speed):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.speed = speed
        self.max_health = max_health
        self.health = max_health
        self.alive = True
        
    def get_rect(self):
        return pyg.Rect(self.x, self.y, self.width, self.height)
        
    def take_damage(self, amount):
        if not self.alive:
            return
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            self.alive = False
            
    def draw_health_bar(self, win):
        if not self.alive or self.health <= 0:
            return
        bar_width = self.width
        bar_height = 5
        fill = (self.health / self.max_health) * bar_width
        outline_rect = pyg.Rect(self.x, self.y - 10, bar_width, bar_height)
        fill_rect = pyg.Rect(self.x, self.y - 10, fill, bar_height)
        
        pyg.draw.rect(win, (255, 0, 0), outline_rect) # Red background
        pyg.draw.rect(win, (0, 255, 0), fill_rect)   # Green fill

    def draw(self, win):
        if self.alive:
            pyg.draw.rect(win, self.color, self.get_rect())
            self.draw_health_bar(win)

class Bullet:
    def __init__(self, x, y, width, height, color, RIGHT, LEFT, UP, DOWN, owner, damage=10):
        # Center bullet logic
        self.width = width
        self.height = height
        
        if DOWN:
            y += 20 + 5
        elif RIGHT or LEFT:
            y += 15
            if RIGHT:
                x += 10
            else:
                x -= 5
                
        self.x = x
        self.y = y
        self.color = color
        self.speed = 5
        self.RIGHT = RIGHT
        self.LEFT = LEFT
        self.UP = UP
        self.DOWN = DOWN
        self.owner = owner # 'player' or 'enemy'
        self.damage = damage
        self.active = True

    def get_rect(self):
        return pyg.Rect(self.x, self.y, self.width, self.height)

    def update(self):
        if not self.active: return
        
        if self.UP:
            self.y -= self.speed
        elif self.DOWN:
            self.y += self.speed
        elif self.RIGHT:
            self.x += self.speed
        elif self.LEFT:
            self.x -= self.speed

        # checking off-screen to deactivate
        if self.y < 0 or self.y > win_size[1] or self.x < 0 or self.x > win_size[0]:
            self.active = False

    def draw(self, win):
        if self.active:
            pyg.draw.rect(win, self.color, self.get_rect())

class Tank(Entity):
    def __init__(self, x, y, width, height, color):
        # Tank has 100 max health and base speed 2
        super().__init__(x, y, width, height, color, max_health=100, speed=2)
        self.bullets = []
        self.shoot_time = 0
        self.UP = True
        self.DOWN = False
        self.LEFT = False
        self.RIGHT = False

    def update(self, key_pressed):
        if not self.alive:
            return
            
        if key_pressed[K_RIGHT] and self.x <= win_size[0] - self.width - 3:
            self.RIGHT = True
            self.LEFT = False
            self.UP = False
            self.DOWN = False
            self.x += self.speed
        elif key_pressed[K_LEFT] and self.x >= 13:
            self.LEFT = True
            self.RIGHT = False
            self.UP = False
            self.DOWN = False
            self.x -= self.speed
        elif key_pressed[K_DOWN] and self.y <= win_size[1] - self.height - 3:
            self.DOWN = True
            self.UP = False
            self.RIGHT = False
            self.LEFT = False
            self.y += self.speed
        elif key_pressed[K_UP] and self.y >= 13:
            self.UP = True
            self.DOWN = False
            self.RIGHT = False
            self.LEFT = False
            self.y -= self.speed

        self.shoot_time += 1
        if key_pressed[K_SPACE] and self.shoot_time >= 25:
            # Create a bullet
            b_width, b_height = self.width / 2, self.height / 2
            bullet = Bullet(self.x + 5, self.y - 10, b_width, b_height, 'red', 
                            self.RIGHT, self.LEFT, self.UP, self.DOWN, owner='player', damage=25)
            self.bullets.append(bullet)
            self.shoot_time = 0

        # Update bullets
        for b in self.bullets:
            b.update()
            
        # Remove inactive bullets
        self.bullets = [b for b in self.bullets if b.active]

    def draw(self, win):
        if not self.alive:
            return
            
        super().draw(win)
        
        # Draw little directional indicator
        UP_rect = [self.x+5, self.y-10, self.width/2, self.height/2]
        DOWN_rect = [self.x+5, self.y-10+20+10, self.width/2, self.height/2]
        RIGHT_rect = [self.x+5+10+5, self.y-10+10+5, self.width/2, self.height/2]
        LEFT_rect = [self.x+5+10+5-30, self.y-10+10+5, self.width/2, self.height/2]
        
        if self.UP: pyg.draw.rect(win, 'red', UP_rect)
        elif self.DOWN: pyg.draw.rect(win, 'red', DOWN_rect)
        elif self.RIGHT: pyg.draw.rect(win, 'red', RIGHT_rect)
        elif self.LEFT: pyg.draw.rect(win, 'red', LEFT_rect)

        for b in self.bullets:
            b.draw(win)

class Enemy(Entity):
    def __init__(self, x, y, width, height, color):
        # Enemy has 50 max health and base speed 1
        super().__init__(x, y, width, height, color, max_health=50, speed=1)
        self.shooting = False
        self.steps = 0
        self.count = 0
        self.bullets = []
        self.shoot_time = 0
        self.directions = {
            "right": False,
            "left": False,
            "up": False,
            "down": False
        }

        dirs = ['right', 'up', 'down', 'left']
        self.current_direction = random.choice(dirs)
        self.directions[self.current_direction] = True

    def update(self):
        if not self.alive:
            return
            
        # Movement logic
        for d in self.directions:
            if self.directions[d]:
                if d == 'right' and self.x <= win_size[0] - self.width:
                    self.x += self.speed
                elif d == 'left' and self.x >= 0:
                    self.x -= self.speed
                elif d == 'up' and self.y >= 0:
                    self.y -= self.speed
                elif d == 'down' and self.y <= win_size[1] - self.height:
                    self.y += self.speed
                    
        self.count += 1
        if self.count >= 100:
            self.steps += 1
            self.count = 0

        # Change direction occasionally
        if self.steps >= random.randint(3, 13):
            dirs = ['right', 'up', 'down', 'left']
            self.current_direction = random.choice(dirs)
            self.steps = 0
            for d in self.directions:
                self.directions[d] = (d == self.current_direction)
            self.shooting = True
            
        # Shooting logic
        self.shoot_time += 1
        if self.shoot_time >= 25 and self.shooting:
            b_width, b_height = self.width / 3, self.height / 2
            bullet = Bullet(self.x + 5, self.y - 10, b_width, b_height, 'red',
                            self.directions['right'], self.directions['left'],
                            self.directions['up'], self.directions['down'], 
                            owner='enemy', damage=10)
            self.bullets.append(bullet)
            self.shoot_time = 0

        # Update bullets
        for b in self.bullets:
            b.update()
            
        # Remove inactive bullets
        self.bullets = [b for b in self.bullets if b.active]

    def draw(self, win):
        if not self.alive:
            return
            
        super().draw(win)
        
        UP_rect = [self.x+5, self.y-10, self.width/2, self.height/2]
        DOWN_rect = [self.x+5, self.y-10+20+10, self.width/2, self.height/2]
        RIGHT_rect = [self.x+5+10+5, self.y-10+10+5, self.width/2, self.height/2]
        LEFT_rect = [self.x+5+10+5-30, self.y-10+10+5, self.width/2, self.height/2]
        
        if self.current_direction == 'up': pyg.draw.rect(win, 'purple', UP_rect)
        elif self.current_direction == 'down': pyg.draw.rect(win, 'purple', DOWN_rect)
        elif self.current_direction == 'right': pyg.draw.rect(win, 'purple', RIGHT_rect)
        elif self.current_direction == 'left': pyg.draw.rect(win, 'purple', LEFT_rect)

        for b in self.bullets:
            b.draw(win)
