
import random
import pyglet
from pyglet import window
from pyglet import clock
from pyglet import font
from pyglet import image
from pyglet.window import key
import os
from datetime import datetime
from pyglet.image.codecs.png import PNGImageDecoder

directory = os.path.abspath(os.path.dirname(__file__))
directory = os.path.join(directory, 'images')
start_time = None
tutorial = 0


def image_loads(image_file_name):
    # load the image

    full_path = os.path.join(directory, image_file_name)
    return image.load(full_path)


class States(object):
    def __init__(self):
        self.buff_draw = False
        self.game_start = False
        self.game_over = False
        self.monster_bullet = False
        self.bullet_speed_up = False
        self.bullet_speed_down = False
        self.ship_speed_up = False
        self.ship_speed_down = False
        self.ship_speed_normal = False
        self.ship_power = False
        self.trible_fire  = False
        self.shoot_flag = False
        self.left_flag = False
        self.right_flag = False
        self.up_flag = False
        self.down_flag = False

    def set_buff_flag(self, buff):
        self.__dict__[buff] = True


class Buff:
    def __init__(self):
        self.buff = []

        for i in range(10):
            self.buff.append('bullet_speed_up')
            self.buff.append('ship_speed_up')
            self.buff.append('bullet_speed_down')
            self.buff.append('ship_speed_down')
        for i in range(20):
            self.buff.append('trible_fire')
        self.buff.append('single_fire')
        self.buff.append('ship_speed_normal')

    def pop(self):
        if len(self.buff) == 0:
            return 'no_buff'
        return self.buff.pop(random.randint(0, len(self.buff)-1))


class SpaceGameWindow(window.Window):
    def __init__(self, *args, **kwargs):
        global start_time
        self.max_monsters = 30
        window.Window.__init__(self, *args, **kwargs)
        self.set_mouse_visible(True)
        start_time = datetime.now()
        self.start_text = None
        self.buff = Buff()
        self.states = States()
        self.bullets = []                                               # bullets
        self.monsters = []                                              # monsters
        self.monster_bullets = []
        self.ship = SpaceShip(self.width - 150, 10, x=100, y=100)       # ship
        self.bullet_image = image_loads("bullet.png")                   # bullet image data
        self.monster_image = image_loads("monster.png")                 # monster image data
        self.background = Sprite('space.jpeg')                          # background image data
        self.monster_bullet_image = image_loads('monster_bullet.png')
        self.buff_sprite = pyglet.sprite.Sprite(image_loads('1.png'))
        self.buff_sprite.set_position(random.randint(0, self.width), self.height)

    def main_loop(self):
        ft = font.load('Arial', 20, bold=True)
        bullet_text = font.Text(ft, y=10)
        ship_text = font.Text(ft, y=40)
        clock.schedule_interval(self.create_monster, 0.4)               # create monsters every interval second
        clock.set_fps_limit(30)                                         # fps limited
        ft2 = font.load('Arial', 36, bold=True)
        title_text = font.Text(ft2, x=110, y=self.height - 100)
        doc_text = font.Text(ft, x=20, y=self.height - 200)
        self.start_text = font.Text(ft, x=210, y=self.height - 400)
        self.kill_text = font.Text(ft, x=190, y=self.height - 460)
        doc_text.text = 'Use ↑↓←→ to move ,space to shoot'
        title_text.text = 'SpaceShoot'
        self.start_text.text = 'Start'
        
        while not self.has_exit:
            self.dispatch_events()
            self.clear()
            if not self.states.game_start:
                title_text.draw()
                self.start_text.draw()
                self.kill_text.text = 'Score: %d' % self.ship.kills
                doc_text.draw()
                self.kill_text.draw()
                self.flip()
                continue
            if self.states.game_over:
                self.start_text.draw()
                self.flip()
                self.states.game_start = False
                continue

            self.update()
            self.draw()

            clock.tick()
            bullet_text.text = "Bullet Speed: %d " % Bullet.velocity
            ship_text.text = "Ship Speed: %d " % self.ship.speed
            bullet_text.draw()
            ship_text.draw()
            self.flip()                                                 # swap the OpenGL front and back buffers

    def update(self):
        to_remove = []
        for sprite in self.monsters:
            sprite.update()
            if sprite.dead:
                to_remove.append(sprite)
        for sprite in to_remove:
            self.monsters.remove(sprite)                                # remove dead monster
        to_remove = []
        for sprite in self.monster_bullets:
            sprite.y -= 4
            if sprite.y < 0:
                to_remove.append(sprite)
        for sprite in to_remove:
            self.monster_bullets.remove(sprite)

        to_remove = []
        for sprite in self.bullets:
            sprite.update()
            if not sprite.dead:
                monster_hit = sprite.collide_once(self.monsters)
                if monster_hit is not None:
                    sprite.on_kill()
                    self.monsters.remove(monster_hit)
                    to_remove.append(sprite)
                    pyglet.media.load('boom.wav').play()
            else:
                to_remove.append(sprite)                                # remove bullets and monsters when they collide
        for sprite in to_remove:
            self.bullets.remove(sprite)

        self.ship.update()
        # check if the ship collides monsters
        if self.ship.collide_once(self.monsters) is not None or self.ship.collide_once(self.monster_bullets) is not None:
            self.ship.dead = True
            self.states.game_over = True

        if self.states.buff_draw:                                       # update the buff sprite
            x, y = self.buff_sprite.position
            y -= 3
            self.buff_sprite.set_position(x, y)
            if self.buff_sprite.y < 0:
                self.states.buff_draw = False
                self.ship.buff.pop(0)
        for buff in self.ship.buff:
            if not ((self.ship.left > self.buff_sprite.x + self.buff_sprite.width)
                    or (self.ship.right < self.buff_sprite.x)
                    or (self.ship.top < self.buff_sprite.y)
                    or (self.ship.bottom > self.buff_sprite.y + self.buff_sprite.height)):
                self.states.set_buff_flag(buff)
                self.ship.buff.remove(buff)
                self.states.buff_draw = False
                self.ship.kills += 50

        if self.states.bullet_speed_down:
            Bullet.velocity -= 6
            self.states.bullet_speed_down = False

        if self.states.bullet_speed_up:
            Bullet.velocity += 3
            self.states.bullet_speed_up = False

        if self.states.ship_speed_down:
            self.ship.speed -= 4
            self.states.ship_speed_down = False

        if self.states.ship_speed_up:
            self.ship.speed += 4
            self.states.ship_speed_up = False

        if self.states.ship_speed_normal:
            self.ship.normal = 10
            self.states.ship_speed_normal = False

        if self.states.ship_power:
            self.ship.kills += len(self.monsters)
            self.monsters = []
            self.states.ship_power = False

        self.ship_shoot()
        self.ship_move()
        self.ship_buff()

    def ship_shoot(self):
        if self.states.shoot_flag and Bullet.bullet_count_control % 7 == 0:  # control the bullet counts
            pyglet.media.load('shoot.wav').play()
            if not self.states.trible_fire:
                self.bullets.append(Bullet(self.ship
                                           , self.bullet_image
                                           , self.height
                                           , x=self.ship.x + (self.ship.image.width / 2) -
                                               (self.bullet_image.width / 2)
                                           , y=self.ship.y))
            else:
                self.bullets.append(Bullet(self.ship
                                           , self.bullet_image
                                           , self.height
                                           , x=self.ship.x + (self.ship.image.width / 2)
                                           , y=self.ship.y))
                self.bullets.append(Bullet(self.ship
                                           , self.bullet_image
                                           , self.height
                                           , x=self.ship.x + (self.ship.image.width / 2) -
                                               4 * (self.bullet_image.width / 2)
                                           , y=self.ship.y))
                self.bullets.append(Bullet(self.ship
                                           , self.bullet_image
                                           , self.height
                                           , x=self.ship.x + (self.ship.image.width / 2) +
                                               4 * (self.bullet_image.width / 2)
                                           , y=self.ship.y))
        Bullet.bullet_count_control += 1

    def ship_move(self):
        if self.states.left_flag:                                         # move the ship
            self.ship.x -= self.ship.speed
            if self.ship.x < 0:
                self.ship.x = 0
                self.ship.left_flag = False

        elif self.states.right_flag:
            self.ship.x += self.ship.speed
            if self.ship.x > self.width - self.ship.sprite.width:
                self.ship.x = self.width - self.ship.sprite.width
                self.ship.right_flag = False

        elif self.states.down_flag:
            self.ship.y -= self.ship.speed
            if self.ship.y < 0:
                self.ship.y = 0
                self.ship.right_flag = False

        elif self.states.up_flag:
            self.ship.y += self.ship.speed
            if self.ship.y > self.height - self.ship.sprite.height:
                self.ship.x = self.height - self.ship.sprite.height
                self.ship.up_flag = False

    def ship_buff(self):
        global tutorial
        if (datetime.now() - start_time).seconds > 15 * tutorial:
            tutorial += 1
            buff = self.buff.pop()
            if buff == 'no_buff':
                tutorial = 99999
                return
            self.ship.buff.append(buff)
            self.states.buff_draw = True
            self.buff_sprite.set_position(random.randint(0, self.width), self.height)

    def draw(self):
        self.background.image.blit(0, 0, width=self.width, height=self.height, z=0)
        for sprite in self.bullets:
            sprite.draw()
        for sprite in self.monsters:
            sprite.draw()
        for sprite in self.monster_bullets:
            sprite.draw()
        self.ship.draw()
        if self.states.buff_draw:
            self.buff_sprite.draw()

    def create_monster(self, interval):
        if len(self.monsters) < self.max_monsters:
            x = random.randint(0, self.width)
            y = self.height
            self.monsters.append(Monster(self.monster_image, x=x, y=y))
            self.monster_bullets.append(Bullet('', self.monster_bullet_image, self.height,
                                               x=x, y=y))

    def init(self):
        self.monsters = []
        self.bullets = []
        self.monster_bullets = []
        self.ship.kills = 0
        self.ship.speed = 10
        Bullet.velocity = 20
        self.ship.x = 100
        self.ship.y = 100
        self.ship.buff = []
        self.buff = Buff()
        self.states = States()
        self.states.game_over = False
        self.states.game_start = True

    def on_mouse_press(self, x, y, button, modifiers):
        if not self.states.game_start:
            if self.start_text.x < x < self.start_text.x + self.start_text.width and self.start_text.y < y < self.start_text.y + self.start_text.height:
                self.init()

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ENTER:
            self.init()
            return
        if symbol == key.SPACE:
            self.states.shoot_flag = True
            Bullet.bullet_count_control = 0
            self.ship_shoot()
        elif symbol == key.LEFT:
            self.states.left_flag = True
        elif symbol == key.RIGHT:
            self.states.right_flag = True
        elif symbol == key.DOWN:
            self.states.down_flag = True
        elif symbol == key.UP:
            self.states.up_flag = True

    def on_key_release(self, symbol, modifiers):
        if symbol == key.SPACE:
            self.states.shoot_flag = False
            Bullet.bullet_count_control = 0
        elif symbol == key.LEFT:
            self.states.left_flag = False
        elif symbol == key.RIGHT:
            self.states.right_flag = False
        elif symbol == key.DOWN:
            self.states.down_flag = False
        elif symbol == key.UP:
            self.states.up_flag = False


class Sprite(object):
    def __get_left(self):
        return self.x
    left = property(__get_left)

    def __get_right(self):
        return self.x + self.image.width
    right = property(__get_right)

    def __get_top(self):
        return self.y + self.image.height
    top = property(__get_top)

    def __get_bottom(self):
        return self.y
    bottom = property(__get_bottom)

    def __init__(self, image_file, image_data=None, **kwargs):
        self.image_file = image_file
        if image_data is None:
            self.image = image_loads(image_file)
        else:
            self.image = image_data
        self.x = 0
        self.y = 0
        self.dead = False
        self.__dict__.update(kwargs)

    def draw(self):
        self.image.blit(self.x, self.y)

    def update(self):
        pass

    def intersect(self, sprite):

        return not ((self.left > sprite.right)or (self.right < sprite.left) or (self.top < sprite.bottom) or
                    (self.bottom > sprite.top))

    def collide(self, sprite_list):
        lst_return = []
        for sprite in sprite_list:
            if self.intersect(sprite):
                lst_return.append(sprite)
                print(12345)
        return lst_return

    def collide_once(self, sprite_list):
        for sprite in sprite_list:
            if self.intersect(sprite):
                return sprite
        return None

    def get_texture(self):
        return self.image.get_texture()


class SpaceShip(Sprite):

    def __init__(self, text_x, text_y, **kwargs):

        self.kills = 0
        self.speed = 10
        self.buff = []

        self.sprite = pyglet.sprite.Sprite(image_loads('fighter.png'))
        Sprite.__init__(self, "fighter.png", **kwargs)

        self.font = font.load('Arial', 20)
        self.kill_text = font.Text(self.font, y=text_y, x=text_x)

    def draw(self):
        self.sprite.set_position(self.x, self. y)
        self.sprite.draw()
        self.kill_text.text = "Score: %d" % self.kills
        self.kill_text.draw()

    def on_kill(self):
        self.kills += 1


class Bullet(Sprite):
    bullet_count_control = 0
    velocity = 20

    def __init__(self, parent_ship, image_data, top, **kwargs):
        self.velocity = Bullet.velocity
        self.screen_top = top
        self.parent_ship = parent_ship
        Sprite.__init__(self, "", image_data, **kwargs)

    def update(self):
        self.y += self.velocity
        if self.bottom > self.screen_top:
            self.dead = True

    def on_kill(self):
        self.parent_ship.on_kill()


class Monster(Sprite):

    def __init__(self, image_data, **kwargs):
        self.y_velocity = 5
        self.set_x_velocity()
        self.x_move_count = 0
        self.x_velocity
        Sprite.__init__(self, "", image_data, **kwargs)
        self.sprite = pyglet.sprite.Sprite(image_data)

    def update(self):
        self.y -= self.y_velocity
        self.x += self.x_velocity
        self.x_move_count += 1

        if self.y < 0:
            self.dead = True

        if self.x_move_count >= 20:
            self.x_move_count = 0
            self.set_x_velocity()

    def draw(self):
        self.sprite.set_position(self.x, self.y)
        self.sprite.draw()

    def set_x_velocity(self):
        self.x_velocity = random.randint(-2, 2)

if __name__ == "__main__":
    space = SpaceGameWindow(width=500, height=650)
    space.set_location(400, 50)
    space.main_loop()
