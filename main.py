import pygame as pyg
import random as rand
import sys
from pygame.locals import *
from objects import Tank, Enemy

pyg.init()
win_size = [600, 600]
win = pyg.display.set_mode(win_size)
pyg.display.set_caption("Tank Fire")

game_over_played = False
try:
    end_sound = pyg.mixer.Sound('endSound.wav')
    end_sound.set_volume(0.5)
except Exception:
    end_sound = None

player = Tank(300, 300, 20, 20, 'purple')

enemy_list = []
def newEnemy():
    colors = ['red','green','yellow','blue','skyblue','pink','navy','orange','Crimson','Coral','SlateGray','Silver']
    color = rand.choice(colors)
    enemy_list.append(Enemy(rand.randint(0, 600 - 20), rand.randint(0, 300), 20, 20, color))

for _ in range(3):
    newEnemy()

fire = True
timer = pyg.time.Clock()
fps = 60

font = pyg.font.SysFont(None, 48)

while fire:
    win.fill((0, 0, 0))
    timer.tick(fps)

    # Event handling
    for event in pyg.event.get():
        if event.type == QUIT:
            fire = False
            
    key_pressed = pyg.key.get_pressed()
    if key_pressed[K_ESCAPE]:
        fire = False

    # 1. Update Game State
    if player.alive:
        player.update(key_pressed)
        
    for enemy in enemy_list:
        enemy.update()

    # Collect all active bullets to process collisions
    # Player bullets vs Enemies
    for b in player.bullets:
        if not b.active: continue
        b_rect = b.get_rect()
        for enemy in enemy_list:
            if enemy.alive and b_rect.colliderect(enemy.get_rect()):
                enemy.take_damage(b.damage)
                b.active = False
                break # Bullet disappears after one hit

    # Enemy bullets vs Player
    if player.alive:
        # Optimization: cache player rect
        p_rect = player.get_rect()
        for enemy in enemy_list:
            for b in enemy.bullets:
                if not b.active: continue
                if b.get_rect().colliderect(p_rect):
                    player.take_damage(b.damage)
                    b.active = False

    # Remove dead enemies and respawn new ones
    enemy_list = [e for e in enemy_list if e.alive]
    while len(enemy_list) < 3:
        newEnemy()

    # 2. Render Game State
    if player.alive:
        player.draw(win)
    else:
        if not game_over_played:
            if end_sound:
                end_sound.play()
            game_over_played = True
        # Game Over text
        game_over_img = font.render('GAME OVER', True, (255, 0, 0))
        win.blit(game_over_img, (win_size[0]//2 - game_over_img.get_width()//2, win_size[1]//2))

    for enemy in enemy_list:
        enemy.draw(win)

    pyg.display.update()

pyg.quit()
print("GAME OVER")