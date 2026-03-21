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

env_options = ['grass', 'dirt', 'sand']
menu_icons = []

def create_env_preview(env_name, w=150, h=150):
    surf = pyg.Surface((w, h))
    base_tile = AssetManager.get_instance().get_environment_image(env_name)
    if base_tile:
        tile_w, tile_h = base_tile.get_size()
        for gx in range(0, w, tile_w):
            for gy in range(0, h, tile_h):
                surf.blit(base_tile, (gx, gy))
    else:
        surf.fill((34, 139, 34))
        
    tree = AssetManager.get_instance().get_environment_image('treeLarge')
    if tree:
        tree_small = pyg.transform.scale(tree, (30, 30))
        surf.blit(tree_small, (20, 20))
        surf.blit(tree_small, (90, 80))
    return surf

for opt in env_options:
    img = create_env_preview(opt)
    menu_icons.append(img)

game_state = "MENU"
menu_index = 0

font_title = pyg.font.SysFont(None, 64)
font_subtitle = pyg.font.SysFont(None, 32)
font_go = pyg.font.SysFont(None, 48)

bg_surface = None
player = None
enemy_list = []
game_over_played = False
end_sound = None

fire = True
timer = pyg.time.Clock()
fps = 60

# Clear relative mouse movement queue once before starting loop
pyg.mouse.get_rel()

while fire:
    timer.tick(fps)
    key_pressed = pyg.key.get_pressed()
    
    mouse_pos = pyg.mouse.get_pos()
    mouse_rel = pyg.mouse.get_rel()
    mouse_click = False
    start_game = False

    for event in pyg.event.get():
        if event.type == QUIT:
            fire = False
        
        if game_state == "MENU":
            if event.type == KEYDOWN:
                if event.key == K_RIGHT:
                    menu_index = (menu_index + 1) % len(env_options)
                elif event.key == K_LEFT:
                    menu_index = (menu_index - 1) % len(env_options)
                elif event.key == K_RETURN or event.key == K_SPACE:
                    start_game = True
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                mouse_click = True

    if key_pressed[K_ESCAPE]:
        fire = False

    # ---------- RENDER MENU ----------
    if game_state == "MENU":
        win.fill((30, 30, 30))
        title_img = font_title.render("SELECT ENVIRONMENT", True, (255, 255, 255))
        win.blit(title_img, (win_size[0]//2 - title_img.get_width()//2, 100))
        
        spacing = 30
        w = 150
        start_x = (win_size[0] - (w * 3 + spacing * 2)) // 2
        
        # Hover logic dynamically updates menu_index only if mouse moves
        for i in range(len(env_options)):
            x = start_x + (i * (w + spacing))
            y = 250
            rect = pyg.Rect(x, y, w, w)
            if rect.collidepoint(mouse_pos):
                if mouse_rel != (0, 0):
                    menu_index = i
                if mouse_click:
                    menu_index = i
                    start_game = True
                    
        # Apply visual rendering strictly based on menu_index
        for i, icon in enumerate(menu_icons):
            x = start_x + (i * (w + spacing))
            y = 250
            
            if i == menu_index:
                scaled_w = int(w * 1.1)
                scaled_icon = pyg.transform.scale(icon, (scaled_w, scaled_w))
                draw_x = x - (scaled_w - w)//2
                draw_y = y - (scaled_w - w)//2
                win.blit(scaled_icon, (draw_x, draw_y))
                pyg.draw.rect(win, (255, 215, 0), [draw_x - 5, draw_y - 5, scaled_w + 10, scaled_w + 10], 5)
                
                label = font_subtitle.render(env_options[i].capitalize(), True, (255, 215, 0))
                label_x = x + w//2 - label.get_width()//2
                label_y = y + int(w * 1.1) + 10
                win.blit(label, (label_x, label_y))
            else:
                win.blit(icon, (x, y))
                pyg.draw.rect(win, (100, 100, 100), [x - 2, y - 2, w + 4, w + 4], 2)
                
                label = font_subtitle.render(env_options[i].capitalize(), True, (200, 200, 200))
                label_x = x + w//2 - label.get_width()//2
                label_y = y + w + 20
                win.blit(label, (label_x, label_y))
                
        if start_game:
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
                
            tree_large = AssetManager.get_instance().get_environment_image('treeLarge')
            if tree_large:
                for _ in range(8):
                    tx, ty = rand.randint(0, win_size[0] - 60), rand.randint(0, win_size[1] - 60)
                    bg_surface.blit(tree_large, (tx, ty))
                    
            player = Tank(300, 300, 32, 32, 'blue')
            
            enemy_list.clear() 
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