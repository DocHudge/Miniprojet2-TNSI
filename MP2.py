import math
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

MAP_WIDTH = 256 * 8
PLAYER_MAX_HP = 5
INVINCIBLE_FRAMES = 60
CONTACT_DAMAGE = 1
PROJECTILE_DAMAGE = 1

ENEMY_SPEED = 0.5
ENEMY_SHOOT_RANGE = 96
ENEMY_SHOOT_DELAY = 90
ENEMY_ACTIVE_RANGE = 160
PROJECTILE_SPEED = 1.5
PROJECTILE_LIFETIME = 150

ENEMY_SPAWNS = [
    (26, 11), (45, 12), (62, 14), (80, 10), (105, 14), (114, 13),
    (147, 9), (163, 9), (174, 6), (184, 11), (200, 13), (210, 8),
    (234, 11), (244, 14),
]

PORTAL_TILE = (249, 11)
PORTAL_W, PORTAL_H = 16, 24

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
        self.health = HealthBar(PLAYER_MAX_HP)

    def take_damage(self, amount):
        return self.health.damage(amount)

    def update(self):
        self.moving = False
        self.health.update()

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

        if self.health.is_invincible and (pyxel.frame_count // 3) % 2 == 0:
            return

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


class HealthBar:

    def __init__(self, max_hp, x=5, y=25, width=62, height=8):
        self.max_hp = max_hp
        self.hp = max_hp
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.invincible_timer = 0

    @property
    def is_dead(self):
        return self.hp <= 0

    @property
    def is_invincible(self):
        return self.invincible_timer > 0

    def update(self):
        if self.invincible_timer > 0:
            self.invincible_timer -= 1

    def damage(self, amount):
        if self.is_invincible or self.is_dead:
            return False
        self.hp = max(0, self.hp - amount)
        self.invincible_timer = INVINCIBLE_FRAMES
        return True

    def draw(self):
        pyxel.rect(self.x, self.y, self.width, self.height, 1)
        pyxel.rectb(self.x, self.y, self.width, self.height, 7)

        fill_width = int((self.hp / self.max_hp) * (self.width - 2))
        if fill_width > 0:
            pyxel.rect(self.x + 1, self.y + 1, fill_width, self.height - 2, 8)

        pyxel.text(self.x, self.y + 11, f"PV {self.hp}/{self.max_hp}", 7)


class Projectile:
    def __init__(self, x, y, vx, vy):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = PROJECTILE_LIFETIME
        self.alive = True

    def update(self, physics):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1

        if self.life <= 0 or self.x < 0 or self.x > MAP_WIDTH or self.y > GAME_OVER_Y + 16:
            self.alive = False
        elif physics.get_tile(self.x, self.y) in TILE_SOLID:
            self.alive = False

    def hits(self, player):
        return (
            player.x <= self.x <= player.x + 8
            and player.y <= self.y <= player.y + 8
        )

    def draw(self):
        sx = int(self.x - scroll_x)
        sy = int(self.y)
        pyxel.circ(sx, sy, 2, 8)
        pyxel.pset(sx, sy, 10)


class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vy = 0
        self.direction = -1
        self.physics = Physics()
        self.shoot_timer = ENEMY_SHOOT_DELAY // 2

    def update(self, player, projectiles):
        if abs(player.x - self.x) > ENEMY_ACTIVE_RANGE:
            return

        old_y = self.y
        self.vy = min(self.vy + self.physics.gravity, 6)
        self.y += self.vy
        on_ground = False
        if self.vy >= 0 and self.physics.is_on_floor(self.x, self.y, old_y):
            self.vy = 0
            self.y = self.physics.get_floor_y(self.x, self.y)
            on_ground = True

        if on_ground:
            new_x = self.x + self.direction * ENEMY_SPEED
            front_x = new_x + (7 if self.direction > 0 else 0)
            below = self.physics.get_tile(front_x, self.y + 8)
            hole = below not in TILE_SOLID and below != TILE_PLATFORM

            if self.physics.is_wall(new_x, self.y) or hole:
                self.direction *= -1
            else:
                self.x = new_x

        dx = (player.x + 4) - (self.x + 4)
        dy = (player.y + 4) - (self.y + 4)
        dist = math.hypot(dx, dy)

        if dist <= ENEMY_SHOOT_RANGE:
            self.shoot_timer -= 1
            if self.shoot_timer <= 0:
                self.shoot_timer = ENEMY_SHOOT_DELAY
                if dist > 0:
                    projectiles.append(Projectile(
                        self.x + 4, self.y + 4,
                        dx / dist * PROJECTILE_SPEED,
                        dy / dist * PROJECTILE_SPEED,
                    ))
        else:
            self.shoot_timer = min(self.shoot_timer, ENEMY_SHOOT_DELAY // 2)

    def touches(self, player):
        return (
            self.x + 1 < player.x + 7 and player.x + 1 < self.x + 7
            and self.y + 1 < player.y + 7 and player.y + 1 < self.y + 7
        )

    def draw(self, player):
        screen_x = int(self.x - scroll_x)
        if screen_x < -8 or screen_x > 128:
            return
        sprite_x = [16, 24][(pyxel.frame_count // 8) % 2]
        w = 8 if player.x >= self.x else -8
        pyxel.blt(screen_x, int(self.y), 0, sprite_x, 24, w, 8, 2)


class Portal:
    def __init__(self, tile_x, tile_y):
        self.x = tile_x * 8
        self.y = tile_y * 8
        self.w = PORTAL_W
        self.h = PORTAL_H

    def touches(self, player):
        return (
            self.x < player.x + 8 and player.x < self.x + self.w
            and self.y < player.y + 8 and player.y < self.y + self.h
        )

    def draw(self):
        sx = int(self.x - scroll_x)
        if sx < -self.w or sx > 128:
            return
        cx = sx + self.w // 2
        cy = int(self.y) + self.h // 2
        t = pyxel.frame_count
        pulse = (t // 6) % 3

        pyxel.elli(sx, self.y, self.w, self.h, 1)
        pyxel.ellib(sx, self.y, self.w, self.h, 12 if pulse else 6)
        pyxel.elli(sx + 3, self.y + 3, self.w - 6, self.h - 6, 2)
        pyxel.ellib(sx + 3, self.y + 3, self.w - 6, self.h - 6, 14)

        for i in range(3):
            a = t * 0.1 + i * 2.1
            pyxel.pset(cx + math.cos(a) * 4, cy + math.sin(a) * 8, 7)


class App:
    def __init__(self):
        pyxel.init(128, 128, title="Je vais tuer ce petit oiseau si git fait encore de la merde")
        pyxel.load("1.pyxres")
        pyxel.mouse(True)

        self.map_width = MAP_WIDTH
        self.physics = Physics()
        self.player = Player(50, 50)
        self.game_over = False
        self.game_over_msg = "L'oiseau est tombe"
        self.won = False
        self.collected_tiles = []
        self.portal = Portal(*PORTAL_TILE)
        self.spawn_enemies()

        pyxel.run(self.update, self.draw)

    def spawn_enemies(self):
        self.enemies = [Enemy(col * 8, (row - 1) * 8) for col, row in ENEMY_SPAWNS]
        self.projectiles = []

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
        self.won = False
        self.spawn_enemies()
        scroll_x = 0

    def update(self):
        global scroll_x

        if self.game_over or self.won:
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

        for enemy in self.enemies:
            enemy.update(self.player, self.projectiles)
            if enemy.touches(self.player):
                self.player.take_damage(CONTACT_DAMAGE)

        for projectile in self.projectiles:
            projectile.update(self.physics)
            if projectile.alive and projectile.hits(self.player):
                projectile.alive = False
                self.player.take_damage(PROJECTILE_DAMAGE)
        self.projectiles = [p for p in self.projectiles if p.alive]

        if self.player.health.is_dead:
            self.game_over = True
            self.game_over_msg = "L'oiseau est mort"
            return

        if self.player.y > GAME_OVER_Y:
            self.game_over = True
            self.game_over_msg = "L'oiseau est tombe"
            return

        if self.portal.touches(self.player):
            self.won = True
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

        
        if not self.game_over and not self.won:
            pyxel.bltm(0, 0, 0, scroll_x, 0, 128, 128)
            self.portal.draw()
            for enemy in self.enemies:
                enemy.draw(self.player)
            for projectile in self.projectiles:
                projectile.draw()
            self.player.draw()
            self.draw_xp_bar()
            self.player.health.draw()
        
#            pyxel.text(
#                10, 30,
#                f"Player : {self.player.x}, {self.player.y}",
#                9
#            )

#            tile_x, tile_y = self.physics.get_tile(
#                self.player.x, self.player.y
#            )
#            pyxel.text(10, 40, f"Tile : {tile_x}, {tile_y}", 9)

#            pyxel.text(
#                10, 50,
#                f"On floor : {self.player.is_on_the_ground}",
#                9
#            )
            return
        

        pyxel.cls(1)
        pyxel.rectb(8, 8, 112, 112, 13)

        if self.won:
            pyxel.text(44, 35, "VICTOIRE !", 10)
            pyxel.text(19, 49, "Tu as franchi le portail", 7)
            label, label_x = "REJOUER", 46
        else:
            pyxel.text(39, 35, "GAME OVER", 8)
            pyxel.text(64 - len(self.game_over_msg) * 2, 49, self.game_over_msg, 7)
            label, label_x = "RECOMMENCER", 36

        mouse_over = (
            24 <= pyxel.mouse_x <= 104
            and 70 <= pyxel.mouse_y <= 92
        )

        button_color = 11 if mouse_over else 5

        pyxel.rect(24, 70, 80, 22, button_color)
        pyxel.rectb(24, 70, 80, 22, 7)
        pyxel.text(label_x, 78, label, 0)

        pyxel.text(39, 103, "Touche R", 6)


App()
