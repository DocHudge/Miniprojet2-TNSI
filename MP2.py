import pyxel

TILE_FLOOR1 = (4,1)
TILE_FLOOR2 = (4,2)

TILE_SOLID = [TILE_FLOOR1, TILE_FLOOR2]

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 2
        self.vy = 2
        self.is_facing_right = True
        self.physics = Physics()
        self.is_on_the_ground = False

    def update(self):
        if pyxel.btn(pyxel.KEY_LEFT):
            self.x -= self.vx
            self.is_facing_right = False

        if pyxel.btn(pyxel.KEY_RIGHT):
            self.x += self.vx
            self.is_facing_right = True

        """if pyxel.btn(pyxel.KEY_UP):
            self.y -= self.vy

        if pyxel.btn(pyxel.KEY_DOWN):
            self.y += self.vy"""

        self.vy += self.physics.gravity
        self.y += self.vy
        self.is_on_floor = False

        if self.physics.is_on_floor(self.x, self.y):
            self.is_on_the_ground = True
            self.vy = 0

        else:
            self.is_on_the_ground = False

    def draw(self):
        #pyxel.rect(self.x, self.y, 8, 8, 9)
        w = 8 if self.is_facing_right else -8
        pyxel.blt(self.x, self.y, 0, 0, 16, w, 8, 2)

class Physics:
    def __init__(self):
        self.gravity = 0.5

    def get_tile(self,x,y):
        tile_x = x//8
        tile_y = y//8
        if tile_x < 0 or tile_y < 0:
            return (0,0)

        return pyxel.tilemaps[0].pget(tile_x, tile_y)

    def is_on_floor(self,x,y):
        tile_left = self.get_tile(x, y + 8)
        tile_right = self.get_tile(x + 8, y + 8)
        if tile_left in TILE_SOLID or tile_right in TILE_SOLID:
            return True
        else:
            return False




class App:
    def __init__(self):
        pyxel.init(160, 120)
        pyxel.load("1.pyxres")
        self.physics = Physics()
        self.player = Player(50, 50)
        pyxel.run(self.update, self.draw)

    def update(self):
        self.player.update()


    def draw(self):
        pyxel.cls(0)
        pyxel.bltm(0, 0, 0, 0, 0, 160, 160)
        self.player.draw()
        pyxel.text(10,10,f"Player : {self.player.x}, {self.player.y}", 9)
        tile_x, tile_y = self.physics.get_tile(self.player.x, self.player.y)
        pyxel.text(10,20,f"Tile : {tile_x}, {tile_y}", 9)
        pyxel.text(10,30,f"On floor : {self.physics.is_on_floor (self.player.x, self.player.y)}", 9)

App()