import pygame as pyg
import random as rand
import sys
from pygame.locals import *

pyg.init()
win_size = [600, 600]
win = pyg.display.set_mode(win_size)
pyg.display.set_caption("Tank Fire")

from asset_manager import AssetManager
from objects import Tank, Enemy

AssetManager.get_instance().init_assets()

# Build Static Background Surface
bg_surface = pyg.Surface(win_size)
grass_tile = AssetManager.get_instance().get_environment_image('grass')
dirt_tile = AssetManager.get_instance().get_environment_image('dirt')
base_tile = grass_tile if grass_tile else (dirt_tile if dirt_tile else None)

if base_tile:
    tile_w, tile_h = base_tile.get_size()
    for gx in range(0, win_size[0], tile_w):
        for gy in range(0, win_size[1], tile_h):
            bg_surface.blit(base_tile, (gx, gy))
else:
    bg_surface.fill((34, 139, 34)) # Fallback to solid green

# Add some trees
tree_large = AssetManager.get_instance().get_environment_image('treeLarge')
if tree_large:
    for _ in range(8):
        tx, ty = rand.randint(0, win_size[0] - 60), rand.randint(0, win_size[1] - 60)
        bg_surface.blit(tree_large, (tx, ty))

game_over_played = False
try:
    end_sound = pyg.mixer.Sound('endSound.wav')
    end_sound.set_volume(0.5)
except Exception:
    end_sound = None

player = Tank(300, 300, 32, 32, 'blue')

enemy_list = []
def newEnemy():
    colors = ['black', 'green', 'red', 'beige']
    color = rand.choice(colors)
    enemy_list.append(Enemy(rand.randint(0, 600 - 30), rand.randint(0, 300), 30, 30, color))

for _ in range(3):
    newEnemy()

fire = True
timer = pyg.time.Clock()
fps = 60
font = pyg.font.SysFont(None, 48)

while fire:
    win.blit(bg_surface, (0, 0))
    timer.tick(fps)

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
    for b in player.bullets:
        if not b.active: continue
        b_rect = b.get_rect()
        for enemy in enemy_list:
            if enemy.alive and b_rect.colliderect(enemy.get_rect()):
                enemy.take_damage(b.damage)
                b.active = False
                break 

    if player.alive:
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
            
        game_over_img = font.render('GAME OVER', True, (255, 0, 0))
        win.blit(game_over_img, (win_size[0]//2 - game_over_img.get_width()//2, win_size[1]//2))

    for enemy in enemy_list:
        enemy.draw(win)

    pyg.display.update()

pyg.quit()
print("GAME OVER")