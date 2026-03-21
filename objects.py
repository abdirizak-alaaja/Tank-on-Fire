import pygame as pyg
import random
from pygame.locals import *
from asset_manager import AssetManager

pyg.init()
try:
    shoot_sound = pyg.mixer.Sound('laser.wav')
    shoot_sound.set_volume(0.2)
except Exception:
    shoot_sound = None

try:
    explosion_sound = pyg.mixer.Sound('explosion.wav')
    explosion_sound.set_volume(0.3)
except Exception:
    explosion_sound = None

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
        self.direction = 'up'
        self.image = None
        
    def get_rect(self):
        return pyg.Rect(self.x, self.y, self.width, self.height)
        
    def take_damage(self, amount):
        if not self.alive:
            return
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            self.alive = False
            if explosion_sound:
                explosion_sound.play()
            
    def draw_health_bar(self, win):
        if not self.alive or self.health <= 0:
            return
        bar_width = self.width
        bar_height = 5
        fill = (self.health / self.max_health) * bar_width
        outline_rect = pyg.Rect(self.x, self.y - 10, bar_width, bar_height)
        fill_rect = pyg.Rect(self.x, self.y - 10, fill, bar_height)
        
        pyg.draw.rect(win, (255, 0, 0), outline_rect) 
        pyg.draw.rect(win, (0, 255, 0), fill_rect)   

    def draw(self, win):
        if self.alive:
            if self.image:
                rect = self.get_rect()
                img_rect = self.image.get_rect(center=rect.center)
                win.blit(self.image, img_rect)
            else:
                pyg.draw.rect(win, self.color, self.get_rect())
            self.draw_health_bar(win)

class Bullet:
    def __init__(self, x, y, width, height, color, RIGHT, LEFT, UP, DOWN, owner, damage=10):
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
        self.owner = owner
        self.damage = damage
        self.active = True
        
        self.direction = 'up'
        if self.UP: self.direction = 'up'
        elif self.DOWN: self.direction = 'down'
        elif self.LEFT: self.direction = 'left'
        elif self.RIGHT: self.direction = 'right'

        self.image = AssetManager.get_instance().get_bullet_image(self.color, self.direction)

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

        if self.y < 0 or self.y > win_size[1] or self.x < 0 or self.x > win_size[0]:
            self.active = False

    def draw(self, win):
        if self.active:
            if self.image:
                rect = self.get_rect()
                img_rect = self.image.get_rect(center=rect.center)
                win.blit(self.image, img_rect)
            else:
                pyg.draw.rect(win, self.color, self.get_rect())

class Tank(Entity):
    def __init__(self, x, y, width, height, color):
        orig_width = 32
        orig_height = 32
        super().__init__(x, y, orig_width, orig_height, color, max_health=100, speed=2)
        self.bullets = []
        self.shoot_time = 0
        self.UP = True
        self.DOWN = False
        self.LEFT = False
        self.RIGHT = False
        self.direction = 'up'

    def update(self, key_pressed):
        if not self.alive:
            return
            
        if key_pressed[K_RIGHT] and self.x <= win_size[0] - self.width - 3:
            self.RIGHT = True; self.LEFT = False; self.UP = False; self.DOWN = False
            self.direction = 'right'
            self.x += self.speed
        elif key_pressed[K_LEFT] and self.x >= 13:
            self.LEFT = True; self.RIGHT = False; self.UP = False; self.DOWN = False
            self.direction = 'left'
            self.x -= self.speed
        elif key_pressed[K_DOWN] and self.y <= win_size[1] - self.height - 3:
            self.DOWN = True; self.UP = False; self.RIGHT = False; self.LEFT = False
            self.direction = 'down'
            self.y += self.speed
        elif key_pressed[K_UP] and self.y >= 13:
            self.UP = True; self.DOWN = False; self.RIGHT = False; self.LEFT = False
            self.direction = 'up'
            self.y -= self.speed

        self.shoot_time += 1
        if key_pressed[K_SPACE] and self.shoot_time >= 25:
            b_width, b_height = 10, 18
            bullet = Bullet(self.x + self.width//2 - 5, self.y + self.height//2 - 9, 
                            b_width, b_height, 'red', 
                            self.RIGHT, self.LEFT, self.UP, self.DOWN, owner='player', damage=25)
            self.bullets.append(bullet)
            self.shoot_time = 0
            if shoot_sound:
                shoot_sound.play()

        for b in self.bullets:
            b.update()
        self.bullets = [b for b in self.bullets if b.active]

    def draw(self, win):
        if not self.alive: return
        self.image = AssetManager.get_instance().get_tank_image(self.color, self.direction)
        super().draw(win)
        for b in self.bullets:
            b.draw(win)

class Enemy(Entity):
    def __init__(self, x, y, width, height, color):
        orig_width = 30
        orig_height = 30
        super().__init__(x, y, orig_width, orig_height, color, max_health=50, speed=1)
        self.shooting = False
        self.steps = 0
        self.count = 0
        self.bullets = []
        self.shoot_time = 0
        self.directions = {
            "right": False, "left": False, "up": False, "down": False
        }

        dirs = ['right', 'up', 'down', 'left']
        self.current_direction = random.choice(dirs)
        self.directions[self.current_direction] = True
        self.direction = self.current_direction

    def update(self):
        if not self.alive:
            return
            
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

        if self.steps >= random.randint(3, 13):
            dirs = ['right', 'up', 'down', 'left']
            self.current_direction = random.choice(dirs)
            self.direction = self.current_direction
            self.steps = 0
            for d in self.directions:
                self.directions[d] = (d == self.current_direction)
            self.shooting = True
            
        self.shoot_time += 1
        if self.shoot_time >= 25 and self.shooting:
            b_width, b_height = 10, 18
            bullet = Bullet(self.x + self.width//2 - 5, self.y + self.height//2 - 9, 
                            b_width, b_height, 'red',
                            self.directions['right'], self.directions['left'],
                            self.directions['up'], self.directions['down'], 
                            owner='enemy', damage=10)
            self.bullets.append(bullet)
            self.shoot_time = 0
            if shoot_sound:
                shoot_sound.play()

        for b in self.bullets:
            b.update()
        self.bullets = [b for b in self.bullets if b.active]

    def draw(self, win):
        if not self.alive: return
        self.image = AssetManager.get_instance().get_tank_image(self.color, self.direction)
        super().draw(win)
        for b in self.bullets:
            b.draw(win)
