import pygame as pyg
import random as rand
import sys
from pygame.locals import *
from asset_manager import AssetManager
from objects import Tank, Enemy

pyg.init()
win_size = [600, 600]
win = pyg.display.set_mode(win_size)
pyg.display.set_caption("Tank Fire")

AssetManager.get_instance().init_assets()

# Pre-load scaled versions of environments for the Menu
env_options = ['grass', 'dirt', 'sand']
menu_icons = []
for opt in env_options:
    img = AssetManager.get_instance().get_environment_image(opt)
    if img:
        img_scaled = pyg.transform.scale(img, (128, 128))
    else:
        img_scaled = pyg.Surface((128, 128))
        img_scaled.fill((34, 139, 34)) 
    menu_icons.append(img_scaled)

game_state = "MENU"
menu_index = 0

font_title = pyg.font.SysFont(None, 64)
font_subtitle = pyg.font.SysFont(None, 32)
font_go = pyg.font.SysFont(None, 48)

# Variables for PLAYING state
bg_surface = None
player = None
enemy_list = []
game_over_played = False
end_sound = None

fire = True
timer = pyg.time.Clock()
fps = 60

while fire:
    timer.tick(fps)
    key_pressed = pyg.key.get_pressed()

    for event in pyg.event.get():
        if event.type == QUIT:
            fire = False
        
        # Menu interaction inputs via one-time KEYDOWN presses
        if game_state == "MENU" and event.type == KEYDOWN:
            if event.key == K_RIGHT:
                menu_index = (menu_index + 1) % len(env_options)
            elif event.key == K_LEFT:
                menu_index = (menu_index - 1) % len(env_options)
            elif event.key == K_RETURN:
                # START GAME
                bg_surface = pyg.Surface(win_size)
                selected_tile_name = env_options[menu_index]
                base_tile = AssetManager.get_instance().get_environment_image(selected_tile_name)
                
                if base_tile:
                    tile_w, tile_h = base_tile.get_size()
                    for gx in range(0, win_size[0], tile_w):
                        for gy in range(0, win_size[1], tile_h):
                            bg_surface.blit(base_tile, (gx, gy))
                else:
                    bg_surface.fill((34, 139, 34))
                    
                # Add some trees to environment
                tree_large = AssetManager.get_instance().get_environment_image('treeLarge')
                if tree_large:
                    for _ in range(8):
                        tx, ty = rand.randint(0, win_size[0] - 60), rand.randint(0, win_size[1] - 60)
                        bg_surface.blit(tree_large, (tx, ty))
                        
                # Initialize Game Entities
                player = Tank(300, 300, 32, 32, 'blue')
                
                for _ in range(3):
                    colors = ['black', 'green', 'red', 'beige']
                    color = rand.choice(colors)
                    enemy_list.append(Enemy(rand.randint(0, 600 - 30), rand.randint(0, 300), 30, 30, color))
                    
                game_over_played = False
                try:
                    end_sound = pyg.mixer.Sound('endSound.wav')
                    end_sound.set_volume(0.5)
                except Exception:
                    end_sound = None
                    
                game_state = "PLAYING"

    if key_pressed[K_ESCAPE]:
        fire = False

    # ---------- RENDER MENU ----------
    if game_state == "MENU":
        win.fill((30, 30, 30))
        
        title_img = font_title.render("SELECT ENVIRONMENT", True, (255, 255, 255))
        win.blit(title_img, (win_size[0]//2 - title_img.get_width()//2, 100))
        
        spacing = 160
        start_x = win_size[0]//2 - (128 + spacing)
        
        for i, icon in enumerate(menu_icons):
            x = start_x + (i * spacing)
            y = 250
            win.blit(icon, (x, y))
            
            label = font_subtitle.render(env_options[i].capitalize(), True, (200, 200, 200))
            win.blit(label, (x + 64 - label.get_width()//2, y + 140))
            
            if i == menu_index:
                pyg.draw.rect(win, (255, 215, 0), [x - 5, y - 5, 138, 138], 5)
                
        pyg.display.update()

    # ---------- RENDER PLAYING ----------
    elif game_state == "PLAYING":
        win.blit(bg_surface, (0, 0))
        
        # 1. Update Game State
        if player.alive:
            player.update(key_pressed)
            
        for enemy in enemy_list:
            enemy.update()

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

        enemy_list = [e for e in enemy_list if e.alive]
        while len(enemy_list) < 3:
            colors = ['black', 'green', 'red', 'beige']
            color = rand.choice(colors)
            enemy_list.append(Enemy(rand.randint(0, 600 - 30), rand.randint(0, 300), 30, 30, color))

        # 2. Render Game State
        if player.alive:
            player.draw(win)
        else:
            if not game_over_played:
                if end_sound:
                    end_sound.play()
                game_over_played = True
                
            game_over_img = font_go.render('GAME OVER', True, (255, 0, 0))
            win.blit(game_over_img, (win_size[0]//2 - game_over_img.get_width()//2, win_size[1]//2))

        for enemy in enemy_list:
            enemy.draw(win)

        pyg.display.update()

pyg.quit()
print("GAME OVER")