
import pyxel

TILE_FLOOR1 = (4, 1)
TILE_FLOOR2 = (4, 2)
TILE_FLOOR3 = (5, 0)
TILE_FLOOR4 = (5, 1)

TILE_SOLID = [
    TILE_FLOOR1, TILE_FLOOR2, TILE_FLOOR3, TILE_FLOOR4,
    (7, 0), (8, 0)
]

TILE_PLATFORM = (1, 0)

ORB_TYPES = [
    (0, 1),
    (1, 1),
    (2, 1),
    (2, 4),
    (3, 4)
]

XP_MAX = 5
SUPER_JUMP_FORCE = 11
GAME_OVER_Y = 136

scroll_x = 0
SCROLL_BORDER = 64


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
        self.moving = False
        self.xp = 0

    def update(self):
        self.moving = False

        if pyxel.btn(pyxel.KEY_LEFT):
            self.is_facing_right = False
            self.moving = True
            if not self.physics.is_wall(self.x - self.vx, self.y):
                self.x -= self.vx

        if pyxel.btn(pyxel.KEY_RIGHT):
            self.is_facing_right = True
            self.moving = True
            if not self.physics.is_wall(self.x + self.vx, self.y):
                self.x += self.vx

        if pyxel.btnp(pyxel.KEY_UP) and self.is_on_the_ground:
            self.is_on_the_ground = False
            self.vy = -self.jump_force

        if pyxel.btnp(pyxel.KEY_X) and self.is_on_the_ground and self.xp >= XP_MAX:
            self.is_on_the_ground = False
            self.vy = -SUPER_JUMP_FORCE
            self.xp = 0

        old_y = self.y
        self.vy = min(self.vy + self.physics.gravity, 6)
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

        platform_y = ((y + 8) // 8) * 8

        if old_y + 8 <= platform_y <= y + 8:
            if tile_left == TILE_PLATFORM or tile_right == TILE_PLATFORM:
                return True

        return False

    def is_wall(self, x, y):
        corners = [
            self.get_tile(x, y),
            self.get_tile(x + 7, y),
            self.get_tile(x, y + 7),
            self.get_tile(x + 7, y + 7)
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
        self.player = Player(50, 50)
        self.game_over = False
        self.collected_tiles = []

        pyxel.run(self.update, self.draw)

    def collect_orbs(self):
        left = int(self.player.x) // 8
        right = int(self.player.x + 7) // 8
        top = int(self.player.y) // 8
        bottom = int(self.player.y + 7) // 8

        for tile_y in range(top, bottom + 1):
            for tile_x in range(left, right + 1):
                tile = pyxel.tilemaps[0].pget(tile_x, tile_y)

                if tile in ORB_TYPES:
                    self.collected_tiles.append((tile_x, tile_y, tile))
                    pyxel.tilemaps[0].pset(tile_x, tile_y, (0, 0))
                    self.player.xp = min(self.player.xp + 1, XP_MAX)

    def restart(self):
        global scroll_x

        for tile_x, tile_y, tile in self.collected_tiles:
            pyxel.tilemaps[0].pset(tile_x, tile_y, tile)

        self.collected_tiles.clear()
        self.player = Player(50, 50)
        self.game_over = False
        scroll_x = 0

    def update(self):
        global scroll_x

        if self.game_over:
            clicked = (
                pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT)
                and 24 <= pyxel.mouse_x <= 104
                and 70 <= pyxel.mouse_y <= 92
            )

            if clicked or pyxel.btnp(pyxel.KEY_R):
                self.restart()

            return

        self.player.update()
        self.collect_orbs()

        if self.player.y > GAME_OVER_Y:
            self.game_over = True
            return

        scroll_x = self.player.x - SCROLL_BORDER
        scroll_x = max(0, min(scroll_x, self.map_width - 128))

    def draw_xp_bar(self):
        x, y = 5, 5
        width, height = 62, 8

        pyxel.rect(x, y, width, height, 1)
        pyxel.rectb(x, y, width, height, 7)

        fill_width = int((self.player.xp / XP_MAX) * (width - 2))

        if fill_width > 0:
            pyxel.rect(x + 1, y + 1, fill_width, height - 2, 12)

        pyxel.text(x, y + 11, "XP", 7)

        if self.player.xp >= XP_MAX:
            pyxel.text(27, y + 11, "X: SUPER SAUT", 10)
        else:
            pyxel.text(27, y + 11, f"{self.player.xp}/{XP_MAX}", 7)

    def draw(self):
        pyxel.cls(0)

        
        if not self.game_over:
            pyxel.bltm(0, 0, 0, scroll_x, 0, 128, 128)
            self.player.draw()
            self.draw_xp_bar()

            pyxel.text(
                10, 30,
                f"Player : {self.player.x}, {self.player.y}",
                9
            )

            tile_x, tile_y = self.physics.get_tile(
                self.player.x, self.player.y
            )
            pyxel.text(10, 40, f"Tile : {tile_x}, {tile_y}", 9)

            pyxel.text(
                10, 50,
                f"On floor : {self.player.is_on_the_ground}",
                9
            )
            return


        pyxel.cls(1)
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
