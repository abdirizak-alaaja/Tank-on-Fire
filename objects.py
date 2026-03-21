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

class Obstacle:
    def __init__(self, x, y, width, height, name, destructible=False, health=100):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.name = name
        self.destructible = destructible
        self.health = health
        self.max_health = health
        self.alive = True
        self.image = AssetManager.get_instance().get_obstacle_image(name)

    def get_rect(self):
        return pyg.Rect(self.x, self.y, self.width, self.height)

    def take_damage(self, amount):
        if not self.destructible or not self.alive:
            return
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            self.alive = False
            if explosion_sound:
                explosion_sound.play()

    def draw(self, win):
        if self.alive:
            if self.image:
                rect = self.get_rect()
                img_rect = self.image.get_rect(center=rect.center)
                win.blit(self.image, img_rect)
            else:
                pyg.draw.rect(win, 'brown', self.get_rect())


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
        self.barrel_image = None
        
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
            rect = self.get_rect()
            if self.image:
                img_rect = self.image.get_rect(center=rect.center)
                win.blit(self.image, img_rect)
            else:
                pyg.draw.rect(win, self.color, rect)
                
            if self.barrel_image:
                offset_x, offset_y = 0, 0
                if self.direction == 'up': offset_y = -10
                elif self.direction == 'down': offset_y = 10
                elif self.direction == 'left': offset_x = -10
                elif self.direction == 'right': offset_x = 10
                
                b_rect = self.barrel_image.get_rect(center=(rect.centerx + offset_x, rect.centery + offset_y))
                win.blit(self.barrel_image, b_rect)
                
            self.draw_health_bar(win)

class Bullet:
    def __init__(self, x, y, width, height, color, RIGHT, LEFT, UP, DOWN, owner, damage=10):
        self.width = width
        self.height = height
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
        orig_width = 30
        orig_height = 30
        super().__init__(x, y, orig_width, orig_height, color, max_health=100, speed=2)
        self.bullets = []
        self.shoot_time = 0
        self.UP = True
        self.DOWN = False
        self.LEFT = False
        self.RIGHT = False
        self.direction = 'up'

    def update(self, key_pressed, obstacle_list):
        if not self.alive:
            return
            
        dx, dy = 0, 0
        if key_pressed[K_RIGHT]:
            self.RIGHT = True; self.LEFT = False; self.UP = False; self.DOWN = False
            self.direction = 'right'
            dx = self.speed
        elif key_pressed[K_LEFT]:
            self.LEFT = True; self.RIGHT = False; self.UP = False; self.DOWN = False
            self.direction = 'left'
            dx = -self.speed
        elif key_pressed[K_DOWN]:
            self.DOWN = True; self.UP = False; self.RIGHT = False; self.LEFT = False
            self.direction = 'down'
            dy = self.speed
        elif key_pressed[K_UP]:
            self.UP = True; self.DOWN = False; self.RIGHT = False; self.LEFT = False
            self.direction = 'up'
            dy = -self.speed

        predicted_rect = self.get_rect().move(dx, dy)
        collision = False
        
        # Room bounds
        if predicted_rect.left < 13 or predicted_rect.right > win_size[0] - 3 or predicted_rect.top < 13 or predicted_rect.bottom > win_size[1] - 3:
            collision = True
            
        for obs in obstacle_list:
            if obs.alive and predicted_rect.colliderect(obs.get_rect()):
                collision = True
                break
                
        if not collision:
            self.x += dx
            self.y += dy

        self.shoot_time += 1
        if key_pressed[K_SPACE] and self.shoot_time >= 25:
            b_width, b_height = 10, 18
            rect = self.get_rect()
            tip_x, tip_y = rect.centerx, rect.centery
            if self.direction == 'up':
                tip_y -= 22
                tip_x -= b_width//2
            elif self.direction == 'down':
                tip_y += 22
                tip_x -= b_width//2
            elif self.direction == 'left':
                tip_x -= 22
                tip_y -= b_width//2
            elif self.direction == 'right':
                tip_x += 22
                tip_y -= b_width//2

            bullet = Bullet(tip_x, tip_y, 
                            b_width, b_height, self.color, 
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
        self.barrel_image = AssetManager.get_instance().get_barrel_image(self.color, self.direction)
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

    def update(self, obstacle_list):
        if not self.alive:
            return
            
        dx, dy = 0, 0
        if self.directions['right']: dx = self.speed
        elif self.directions['left']: dx = -self.speed
        elif self.directions['up']: dy = -self.speed
        elif self.directions['down']: dy = self.speed

        predicted_rect = self.get_rect().move(dx, dy)
        collision = False
        
        # Room bounds
        if predicted_rect.left < 13 or predicted_rect.right > win_size[0] - 3 or predicted_rect.top < 13 or predicted_rect.bottom > win_size[1] - 3:
            collision = True
            
        for obs in obstacle_list:
            if obs.alive and predicted_rect.colliderect(obs.get_rect()):
                collision = True
                break

        if not collision:
            self.x += dx
            self.y += dy
        else:
            # Force rotation earlier if blocked
            self.count = 100
                    
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
            rect = self.get_rect()
            tip_x, tip_y = rect.centerx, rect.centery
            if self.direction == 'up':
                tip_y -= 22
                tip_x -= b_width//2
            elif self.direction == 'down':
                tip_y += 22
                tip_x -= b_width//2
            elif self.direction == 'left':
                tip_x -= 22
                tip_y -= b_width//2
            elif self.direction == 'right':
                tip_x += 22
                tip_y -= b_width//2

            bullet = Bullet(tip_x, tip_y, 
                            b_width, b_height, self.color,
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
        self.barrel_image = AssetManager.get_instance().get_barrel_image(self.color, self.direction)
        super().draw(win)
        for b in self.bullets:
            b.draw(win)
