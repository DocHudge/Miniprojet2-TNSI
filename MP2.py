
import pyxel

TILE_FLOOR1 = (4, 1)
TILE_FLOOR2 = (4, 2)
TILE_FLOOR3 = (5, 0)
TILE_FLOOR4 = (5, 1)
TILE_FLOOR5 = (5, 2)
TILE_FLOOR6 = (6, 2)
TILE_FLOOR7 = (7, 2)

TILE_SOLID = [
    TILE_FLOOR1, TILE_FLOOR2, TILE_FLOOR3, TILE_FLOOR4, TILE_FLOOR5, TILE_FLOOR6, TILE_FLOOR7, 
    (7, 0), (8, 0), (5, 4), (5, 5), (6, 5), (6, 7), (7, 4), (7, 5), (6, 1), (7, 1)
]

TILE_PLATFORM = (1, 0)

scroll_x = 0
SCROLL_BORDER = 64
GAME_OVER_Y = 136


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 2
        self.vy = 0
        self.is_facing_right = True
        self.physics = Physics()
        self.is_on_the_ground = False
        self.jump_force = 6

    def update(self):
        moving = False

        if pyxel.btn(pyxel.KEY_LEFT):
            self.is_facing_right = False
            moving = True
            if not self.physics.is_wall(self.x - self.vx, self.y):
                self.x -= self.vx

        if pyxel.btn(pyxel.KEY_RIGHT):
            self.is_facing_right = True
            moving = True
            if not self.physics.is_wall(self.x + self.vx, self.y):
                self.x += self.vx

        if pyxel.btnp(pyxel.KEY_UP) and self.is_on_the_ground:
            self.is_on_the_ground = False
            self.vy = -self.jump_force

        self.vy = min(self.vy + self.physics.gravity, 6)
        old_y = self.y
        self.y += self.vy

        if self.vy < 0 and self.physics.is_wall(self.x, self.y):
            self.y = (int(self.y) // 8 + 1) * 8
            self.vy = 0

        if self.vy >= 0 and self.physics.is_on_floor(self.x, self.y, old_y):
            self.is_on_the_ground = True
            self.vy = 0
            self.y = self.physics.get_floor_y(self.x, self.y)
        else:
            self.is_on_the_ground = False

        self.moving = moving

    def draw(self):
        screen_x = self.x - scroll_x

        if self.is_on_the_ground:
            if self.moving:
                sprite_x = [0, 8][(pyxel.frame_count // 8) % 2]
            else:
                sprite_x = 8
        else:
            sprite_x = [16, 0, 8][(pyxel.frame_count // 5) % 3]

        w = 8 if self.is_facing_right else -8
        pyxel.blt(screen_x, self.y, 0, sprite_x, 16, w, 8, 2)


class Physics:
    def __init__(self):
        self.gravity = 0.5

    def get_tile(self, x, y):
        tile_x = int(x) // 8
        tile_y = int(y) // 8

        if tile_x < 0 or tile_y < 0:
            return (0, 0)

        return pyxel.tilemaps[0].pget(tile_x, tile_y)

    def is_on_floor(self, x, y, old_y):
        tile_left = self.get_tile(x, y + 8)
        tile_right = self.get_tile(x + 7, y + 8)

        if tile_left in TILE_SOLID or tile_right in TILE_SOLID:
            return True

        if self.get_tile(x, y + 8) == TILE_PLATFORM:
            platform_y = ((y + 8) // 8) * 8
            if old_y + 8 <= platform_y <= y + 8:
                return True

        if self.get_tile(x + 7, y + 8) == TILE_PLATFORM:
            platform_y = ((y + 8) // 8) * 8
            if old_y + 8 <= platform_y <= y + 8:
                return True

        return False

    def is_wall(self, x, y):
        corners = [
            self.get_tile(x, y),
            self.get_tile(x + 7, y),
            self.get_tile(x, y + 7),
            self.get_tile(x + 7, y + 7),
        ]

        return any(tile in TILE_SOLID for tile in corners)

    def get_floor_y(self, x, y):
        tile_y = (y + 8) // 8
        return tile_y * 8 - 8


class App:
    def __init__(self):
        pyxel.init(128, 128, title="Je vais tuer ce petit oiseau si git fait encore de la merde")
        pyxel.load("1.pyxres")
        pyxel.mouse(True)

        self.map_width = 1000
        self.physics = Physics()
        self.game_over = False
        self.player = Player(50, 50)

        pyxel.run(self.update, self.draw)

    def restart(self):
        global scroll_x

        self.player = Player(50, 50)
        self.game_over = False
        scroll_x = 0

    def update(self):
        global scroll_x

        if self.game_over:
            button_clicked = (
                pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT)
                and 24 <= pyxel.mouse_x <= 104
                and 70 <= pyxel.mouse_y <= 92
            )

            if button_clicked or pyxel.btnp(pyxel.KEY_R):
                self.restart()

            return

        self.player.update()

        if self.player.y > GAME_OVER_Y:
            self.game_over = True
            return

        scroll_x = self.player.x - SCROLL_BORDER
        scroll_x = max(0, min(scroll_x, self.map_width - 128))

    def draw(self):
        pyxel.cls(0)

        if not self.game_over:
            pyxel.bltm(0, 0, 0, scroll_x, 0, 128, 128)
            self.player.draw()
            return

        pyxel.rect(0, 0, 128, 128, 1)
        pyxel.rectb(8, 8, 112, 112, 13)

        pyxel.text(39, 35, "GAME OVER", 8)
        pyxel.text(23, 49, "L'oiseau est tombe", 7)

        mouse_over = (
            24 <= pyxel.mouse_x <= 104
            and 70 <= pyxel.mouse_y <= 92
        )

        button_color = 11 if mouse_over else 5

        pyxel.rect(24, 70, 80, 22, button_color)
        pyxel.rectb(24, 70, 80, 22, 7)
        pyxel.text(36, 78, "RECOMMENCER", 0)

        pyxel.text(39, 103, "Touche R", 6)


App()
