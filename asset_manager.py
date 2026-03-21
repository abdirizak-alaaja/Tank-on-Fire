import pygame as pyg
import os

class AssetManager:
    _instance = None

    def __init__(self):
        self.tanks = {}
        self.barrels = {}
        self.bullets = {}
        self.env = {}
        self.obstacles = {}
        self.smoke = {}
        self.initialized = False

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = AssetManager()
        return cls._instance

    def init_assets(self):
        if self.initialized: return
        base_dir = os.path.dirname(__file__)
        assets_dir = os.path.join(base_dir, 'assets')
        
        tank_colors = ['beige', 'black', 'blue', 'green', 'red']
        
        # 1. Load Tanks and Barrels
        for c in tank_colors:
            filename_tank = f"tank{c.capitalize()}.png"
            path_tank = os.path.join(assets_dir, 'Tanks', filename_tank)
            if os.path.exists(path_tank):
                img = pyg.image.load(path_tank).convert_alpha()
                img = pyg.transform.scale(img, (35, 35))
                self.tanks[c] = img
                
            filename_barrel = f"barrel{c.capitalize()}.png"
            path_barrel = os.path.join(assets_dir, 'Tanks', filename_barrel)
            if os.path.exists(path_barrel):
                img_b = pyg.image.load(path_barrel).convert_alpha()
                img_b = pyg.transform.scale(img_b, (10, 24))
                self.barrels[c] = img_b
                
        # 2. Load Bullets
        bullet_colors = ['beige', 'blue', 'green', 'red', 'silver', 'yellow']
        for c in bullet_colors:
            filename = f"bullet{c.capitalize()}.png"
            path = os.path.join(assets_dir, 'Bullets', filename)
            if os.path.exists(path):
                img = pyg.image.load(path).convert_alpha()
                img = pyg.transform.scale(img, (10, 18))
                self.bullets[c] = img

        # 3. Load Environment
        env_files = ['dirt.png', 'grass.png', 'sand.png', 'treeLarge.png', 'treeSmall.png']
        for ef in env_files:
            path = os.path.join(assets_dir, 'Environment', ef)
            if os.path.exists(path):
                img = pyg.image.load(path).convert_alpha()
                key = ef.split('.')[0]
                
                if 'treeLarge' in key:
                    img = pyg.transform.scale(img, (60, 60))
                elif 'treeSmall' in key:
                    img = pyg.transform.scale(img, (40, 40))
                elif 'grass' in key or 'dirt' in key or 'sand' in key:
                    img = pyg.transform.scale(img, (64, 64))
                    
                self.env[key] = img

        # 4. Load Obstacles
        obs_files = ['barrelGreen_side.png', 'barrelGreen_side_damaged.png', 'barrelGreen_up.png', 
                     'barrelGrey_sde_rust.png', 'barrelGrey_side.png', 'barrelGrey_up.png', 
                     'barrelRed_side.png', 'barrelRed_up.png', 'oil.png', 'sandbagBeige.png', 'sandbagBrown.png']
        for of in obs_files:
            path = os.path.join(assets_dir, 'Obstacles', of)
            if os.path.exists(path):
                img = pyg.image.load(path).convert_alpha()
                key = of.split('.')[0]
                img = pyg.transform.scale(img, (35, 35))
                self.obstacles[key] = img

        # 5. Load Smoke (Dynamically Tinted)
        base_smoke = []
        for i in range(6):
            path = os.path.join(assets_dir, 'Smoke', f'smokeWhite{i}.png')
            if os.path.exists(path):
                img = pyg.image.load(path).convert_alpha()
                base_smoke.append(img)

        color_maps = {
            'beige': (210, 180, 140, 255),
            'black': (50, 50, 50, 255),
            'blue': (65, 105, 225, 255),
            'green': (34, 139, 34, 255),
            'red': (220, 20, 60, 255)
        }
        
        for c, rgb in color_maps.items():
            self.smoke[c] = []
            for img in base_smoke:
                tint_surface = pyg.Surface(img.get_size(), pyg.SRCALPHA)
                tint_surface.fill(rgb)
                tinted = img.copy()
                tinted.blit(tint_surface, (0, 0), special_flags=pyg.BLEND_RGBA_MULT)
                tinted = pyg.transform.scale(tinted, (40, 40))
                self.smoke[c].append(tinted)
                
        self.initialized = True

    def get_tank_image(self, color, direction):
        c = color.lower()
        if c not in self.tanks:
            c = list(self.tanks.keys())[0] if self.tanks else None
        if not c: return None
            
        base = self.tanks[c]
        angle = 0
        if direction == 'up': angle = 0
        elif direction == 'left': angle = 90
        elif direction == 'down': angle = 180
        elif direction == 'right': angle = 270
        
        return pyg.transform.rotate(base, angle)

    def get_barrel_image(self, color, direction):
        c = color.lower()
        if c not in self.barrels:
            c = list(self.barrels.keys())[0] if self.barrels else None
        if not c: return None
            
        base = self.barrels[c]
        angle = 0
        if direction == 'up': angle = 0
        elif direction == 'left': angle = 90
        elif direction == 'down': angle = 180
        elif direction == 'right': angle = 270
        
        return pyg.transform.rotate(base, angle)

    def get_bullet_image(self, color, direction):
        c = color.lower()
        if c not in self.bullets:
            c = list(self.bullets.keys())[0] if self.bullets else None
        if not c: return None
            
        base = self.bullets[c]
        angle = 0
        if direction == 'up': angle = 0
        elif direction == 'left': angle = 90
        elif direction == 'down': angle = 180
        elif direction == 'right': angle = 270
        
        return pyg.transform.rotate(base, angle)

    def get_environment_image(self, name):
        return self.env.get(name, None)

    def get_obstacle_image(self, name):
        return self.obstacles.get(name, None)

    def get_smoke_images(self, color):
        c = color.lower()
        return self.smoke.get(c, self.smoke.get('black'))
