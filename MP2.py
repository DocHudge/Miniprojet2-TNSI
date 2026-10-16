import pyxel

TILE_FLOOR1 = (4,1)
TILE_FLOOR2 = (4,2)
TILE_FLOOR3 = (5,0)
TILE_FLOOR4 = (5,1)

TILE_SOLID = [TILE_FLOOR1, TILE_FLOOR2, TILE_FLOOR3, TILE_FLOOR4, (7,0), (8,0)]

scroll_x = 0
SCROLL_BORDER = 64

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 2
        self.vy = 2
        self.is_facing_right = True
        self.physics = Physics()
        self.is_on_the_ground = False
        self.jump_force = 6

    def update(self):
        # CORRECTION : on teste le mur avant de se déplacer
        if pyxel.btn(pyxel.KEY_LEFT):
            self.is_facing_right = False
            if not self.physics.is_wall(self.x - self.vx, self.y):
                self.x -= self.vx

        if pyxel.btn(pyxel.KEY_RIGHT):
            self.is_facing_right = True
            if not self.physics.is_wall(self.x + self.vx, self.y):
                self.x += self.vx

        # CORRECTION : saut uniquement au sol, et vy fixé (pas cumulé)
        if pyxel.btnp(pyxel.KEY_UP) and self.is_on_the_ground:
            self.is_on_the_ground = False
            self.vy = -self.jump_force

        """if pyxel.btn(pyxel.KEY_DOWN):
            self.y += self.vy"""

        self.vy = min(self.vy + self.physics.gravity, 6)
        self.y += self.vy
        self.is_on_floor = False

        # CORRECTION : plafond (on se cogne la tête en montant)
        if self.vy < 0 and self.physics.is_wall(self.x, self.y):
            self.y = (int(self.y) // 8 + 1) * 8
            self.vy = 0

        # CORRECTION : on ne teste le sol que quand on descend
        if self.vy >= 0 and self.physics.is_on_floor(self.x, self.y):
            self.is_on_the_ground = True
            self.vy = 0
            self.y = self.physics.get_floor_y(self.x, self.y)

        else:
            self.is_on_the_ground = False

    def draw(self):
        # CORRECTION : x - scroll_x (et non x - y)
        screen_x = self.x - scroll_x
        w = 8 if self.is_facing_right else -8
        pyxel.blt(screen_x, self.y, 0, 0, 16, w, 8, 2)

class Physics:
    def __init__(self):
        self.gravity = 0.5

    def get_tile(self,x,y):
        tile_x = int(x)//8
        tile_y = int(y)//8
        if tile_x < 0 or tile_y < 0:
            return (0,0)

        return pyxel.tilemaps[0].pget(tile_x, tile_y)

    def is_on_floor(self,x,y):
        tile_left = self.get_tile(x, y + 8)
        tile_right = self.get_tile(x + 7, y + 8)
        if tile_left in TILE_SOLID or tile_right in TILE_SOLID:
            return True
        else:
            return False

    # NOUVEAU : teste les 4 coins du sprite (8x8) pour les murs
    def is_wall(self, x, y):
        corners = [
            self.get_tile(x,     y),
            self.get_tile(x + 7, y),
            self.get_tile(x,     y + 7),
            self.get_tile(x + 7, y + 7),
        ]
        for tile in corners:
            if tile in TILE_SOLID:
                return True
        return False

    def get_floor_y(self,x,y):
        tile_y = (y+8) // 8
        floor_y = tile_y * 8
        return floor_y - 8



class App:
    def __init__(self):
        pyxel.init(128, 128)
        pyxel.load("1.pyxres")
        self.map_width = 1000
        self.physics = Physics()
        self.player = Player(50, 50)
        pyxel.run(self.update, self.draw)

    def update(self):
        global scroll_x
        scroll_x = self.player.x - SCROLL_BORDER
        scroll_x = max(0, min(scroll_x, self.map_width-128))
        self.player.update()


    def draw(self):
        pyxel.cls(0)
        pyxel.bltm(0, 0, 0, scroll_x, 0, 128, 128)
        self.player.draw()
        pyxel.text(10,10,f"Player : {self.player.x}, {self.player.y}", 9)
        tile_x, tile_y = self.physics.get_tile(self.player.x, self.player.y)
        pyxel.text(10,20,f"Tile : {tile_x}, {tile_y}", 9)
        pyxel.text(10,30,f"On floor : {self.physics.is_on_floor (self.player.x, self.player.y)}", 9)

App()