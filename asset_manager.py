import pygame as pyg
import os

class AssetManager:
    _instance = None

    def __init__(self):
        self.tanks = {}
        self.bullets = {}
        self.env = {}
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
        
        # 1. Load Tanks
        tank_colors = ['beige', 'black', 'blue', 'green', 'red']
        for c in tank_colors:
            # Match capitalization from file listing, e.g. tankBlue.png
            filename = f"tank{c.capitalize()}.png"
            path = os.path.join(assets_dir, 'Tanks', filename)
            if os.path.exists(path):
                img = pyg.image.load(path).convert_alpha()
                # Scale tanks to slightly larger than the old 20x20 rect
                img = pyg.transform.scale(img, (35, 35))
                self.tanks[c] = img
                
        # 2. Load Bullets
        bullet_colors = ['beige', 'blue', 'green', 'red', 'silver', 'yellow']
        for c in bullet_colors:
            # Bullet file looks like bulletRed.png
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
                
                # Optionally scale environment objects
                if 'treeLarge' in key:
                    img = pyg.transform.scale(img, (60, 60))
                elif 'treeSmall' in key:
                    img = pyg.transform.scale(img, (40, 40))
                elif 'grass' in key or 'dirt' in key or 'sand' in key:
                    img = pyg.transform.scale(img, (64, 64))
                    
                self.env[key] = img
                
        self.initialized = True

    def get_tank_image(self, color, direction):
        c = color.lower()
        if c not in self.tanks:
            c = list(self.tanks.keys())[0] if self.tanks else None
            
        if not c:
            return None
            
        base = self.tanks[c]
        
        # Rotate image based on direction
        # Assuming original asset faces UP
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
            
        if not c:
            return None
            
        base = self.bullets[c]
        
        angle = 0
        if direction == 'up': angle = 0
        elif direction == 'left': angle = 90
        elif direction == 'down': angle = 180
        elif direction == 'right': angle = 270
        
        return pyg.transform.rotate(base, angle)

    def get_environment_image(self, name):
        return self.env.get(name, None)
