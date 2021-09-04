#encoding=utf-8
"""子弹模型 """
import pygame
from pygame.locals import *

from libs import *
from start import *
from tanks import *
from collision import *
from renders import *


class Bulletstate_move(State):
    def __init__(self, bullet):
        State.__init__(self, "move")
        self.mold = bullet

    def do_actions(self):
        self.mold.new_rect = self.mold.rect.move(self.mold.direct[0] * self.mold.speed,
                                 self.mold.direct[1] * self.mold.speed)
        self.mold.rect = self.mold.new_rect

    def check_conditions(self):
        passive = collision(self.mold)
        if not SCREENRECT.colliderect(self.mold.rect) or not self.mold.owner.bgmap.map_passive(self.mold.new_rect)\
        or not passive:
            self.mold.died()
        return
        

class Bulletstate_move_no_block(State):
    def __init__(self, bullet):
        State.__init__(self, "move")
        self.mold = bullet

    def do_actions(self):
        self.mold.new_rect = self.mold.rect.move(self.mold.direct[0] * self.mold.speed,
                                 self.mold.direct[1] * self.mold.speed)
        self.mold.rect = self.mold.new_rect

    def check_conditions(self):
        passive = collision(self.mold)
        if not SCREENRECT.colliderect(self.mold.rect) or not passive:
            self.mold.died()
        return


class Bulletstate_beammove(State):
    def __init__(self, bullet):
        State.__init__(self, "move")
        self.mold = bullet

    def do_actions(self):
        self.mold.length = self.mold.length + self.mold.speed
        if self.mold.direct[0] == 0:
            self.mold.image = pygame.Surface((self.mold.width, self.mold.length)).convert()
        else:
            self.mold.image = pygame.Surface((self.mold.length, self.mold.width)).convert()
        self.mold.image.fill((255, 0, 0))
        self.mold.rect = self.mold.get_bullet_rect(self.mold.pos)

    def check_conditions(self):
        passive = collision(self.mold, rect=self.mold.rect)
        if not SCREENRECT.colliderect(self.mold.rect) or not self.mold.owner.bgmap.map_passive(rect=self.mold.rect)\
        or not passive:
            self.mold.died()

        return


class Bullet(pygame.sprite.Sprite):
    direct_img = {(0, -1): 0,
        (1, 0): 1,
        (0, 1): 2,
        (-1, 0): 3
        }

    def __init__(self, owner):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.owner = owner
        self.game_items = owner.game_items
        self.image = None

    def get_bullet_rect(self, pos):
        if self.direct == (0, -1):
            rect = self.image.get_rect(midbottom=pos)
        elif self.direct == (1, 0):
            rect = self.image.get_rect(midleft=pos)
        elif self.direct == (0, 1):
            rect = self.image.get_rect(midtop=pos)
        elif self.direct == (-1, 0):
            rect = self.image.get_rect(midright=pos)
        return rect

    def bgmap_passive(self, rect):
        return self.owner.bgmap.map_passive(rect)

    def wounded(self, wound):
        self.health = self.health - wound
        if self.health < 0:
            self.died()


class NormalBullet(Bullet, pygame.sprite.Sprite):
    images = None
    died_images = None

    def __init__(self, pos, direct, owner):
        Bullet.__init__(self, owner)
        self.name = self.owner.name + ":normalBullet"
        self.images = load_images('shot1.gif', 'shot2.gif',
                                     'shot3.gif', 'shot4.gif')
        self.died_images = load_images('shotdied.gif')
        self.direct = direct
        self.image = self.images[self.direct_img[direct]]
        self.rect = self.get_bullet_rect(pos)
        self.speed = max(self.rect.width, self.rect.height) / 2

        self.brain = StateMachine()
        moving_state = Bulletstate_move(self)
        self.brain.add_state(moving_state)
        self.brain.set_state("move")

        self.health = 10

    def wounded(self, wound):
        self.health = self.health - wound
        if self.health < 0:
            self.died()

    def died(self):
        Explod(self.died_images, self.rect.center)
        self.kill()

    def update(self, *args):
        self.brain.think()


class BeamBullet(Bullet, pygame.sprite.Sprite):
    # 激光
    images = None

    def __init__(self, pos, direct, owner):
        Bullet.__init__(self, owner)
        self.name = self.owner.name + ":beamBullet"
        self.direct = direct
        self.pos = pos
        self.width = 5
        self.length = 16
        if self.direct[0] == 0:
            self.image = pygame.Surface((self.width, self.length)).convert()
        else:
            self.image = pygame.Surface((self.length, self.width)).convert()
        self.image.fill((255, 0, 0))
        self.rect = self.get_bullet_rect(pos)
        self.speed = max(self.rect.width, self.rect.height) * 3

        self.brain = StateMachine()
        moving_state = Bulletstate_beammove(self)
        self.brain.add_state(moving_state)
        self.brain.set_state("move")

        self.health = 10

    def wounded(self, wound):
        self.health = self.health - wound
        if self.health < 0:
            self.died()

    def died(self):
        self.kill()

    def update(self, *args):
        self.brain.think()


class PullWave(Bullet, pygame.sprite.Sprite):
    # 吸引波
    image = None

    def __init__(self, pos, direct, owner):
        Bullet.__init__(self, owner)
        self.name = self.owner.name + ":pullwave"
        self.width = 205
        self.length = 3
        self.image = pygame.Surface((self.width, self.length)).convert()
        self.image.fill((255, 0, 0))
        self.direct = (0, 1)
        # 吸引波的目标点 ， 吸引力
        self.pullpoint = owner.rect.midbottom
        self.power = 4
        self.rect = self.image.get_rect(center=(self.pullpoint[0], self.pullpoint[1] + 200))
        self.speed = 5
        self.livetime = time_to_frams((1))
        self.now_livetime = self.livetime

    def wounded(self, wound):
        pass

    def died(self):
        self.kill()

    def more_effect(self, target):
        targetvector = pygame.math.Vector2(target.rect.center)
        selfvector = pygame.math.Vector2(self.pullpoint)
        vector = selfvector - targetvector

        if vector.length() > 0:
            targetmovevector = (vector).normalize() * self.power    # 运行方向单位向量 * 行动速度
            target.new_rect = target.rect.move(targetmovevector.x, targetmovevector.y)
            if collision(target) and target.bgmap_passive(target.new_rect):
                target.rect = target.new_rect
                target.rect = target.rect.clamp(SCREENRECT)

    def update(self, *args):
        collision(self, rect=self.rect)
        if self.now_livetime > 0 and self.rect.width > 5:
            self.image = pygame.transform.scale(self.image, (self.rect.width - 5, self.rect.height))
            self.rect = self.image.get_rect(center=self.rect.center)
            self.rect.move_ip((0, -self.speed))
            self.now_livetime = self.now_livetime - 1
        else:
            self.died()


class PushWave(Bullet, pygame.sprite.Sprite):
    # 推进波
    image = None

    def __init__(self, pos, direct, owner):
        Bullet.__init__(self, owner)
        self.name = self.owner.name + ":pushwave"
        self.images = load_images('pushwave1.gif', 'pushwave2.gif',
                                     'pushwave3.gif', 'pushwave4.gif')
        self.direct = direct
        self.image = self.images[self.direct_img[direct]]
        self.rect = self.get_bullet_rect(pos)
        self.speed = 10
        # 推动波的推动力
        self.power = 8
        self.livetime = time_to_frams((1))
        self.now_livetime = self.livetime

    def wounded(self, wound):
        pass

    def died(self):
        self.kill()

    def more_effect(self, target):
        target.new_rect = target.rect.move(self.direct[0] * self.power, self.direct[1] * self.power)
        if collision(target) and target.bgmap_passive(target.new_rect):
            target.rect = target.new_rect
            target.rect = target.rect.clamp(SCREENRECT)

    def update(self, *args):
        collision(self, rect=self.rect)
        if self.now_livetime > 0:
            self.rect.move_ip((self.direct[0] * self.speed, self.direct[1] * self.speed))
            self.now_livetime = self.now_livetime - 1
        else:
            self.died()


class PillboxBullet(Bullet, pygame.sprite.Sprite):
    # 碉堡子弹
    images = None
    died_images = None
    gap = 5

    def __init__(self, direct, angle, owner):
        Bullet.__init__(self, owner)
        self.name = self.owner.name + ":normalBullet"
        self.nochange_image = load_image('fire.gif')
        self.died_images = load_images('shotdied.gif')
        self.image = pygame.transform.rotate(self.nochange_image, angle)
        self.direct = direct
        self.rect = self.image.get_rect(center=owner.rect.center)
        self.rect.move_ip(self.direct[0] * self.gap, self.direct[1] * self.gap)
        self.speed = max(self.rect.width, self.rect.height) / 2

        self.brain = StateMachine()
        moving_state = Bulletstate_move_no_block(self)
        self.brain.add_state(moving_state)
        self.brain.set_state("move")

        self.health = 10

    def wounded(self, wound):
        self.health = self.health - wound
        if self.health < 0:
            self.died()

    def died(self):
        Explod(self.died_images, self.rect.center)
        self.kill()

    def update(self, *args):
        self.brain.think()


class IceBullet(Bullet, pygame.sprite.Sprite):
    # 冰冻弹
    images = None
    speed = 8
    health = 20

    def __init__(self, pos, direct, owner):
        Bullet.__init__(self, owner)
        self.name = self.owner.name + ":iceBullet"
        self.image = load_image('icebullet.gif')
        self.direct = direct
        self.rect = self.get_bullet_rect(pos)

        self.brain = StateMachine()
        moving_state = Bulletstate_move(self)
        self.brain.add_state(moving_state)
        self.brain.set_state("move")

    def wounded(self, wound):
        self.health = self.health - wound
        if self.health < 0:
            self.died()

    def more_effect(self, target):
        Frozen(target)

    def died(self):
        self.kill()

    def update(self, *args):
        self.brain.think()


class BounceBullet(Bullet, pygame.sprite.Sprite):
    # 弹球弹
    image = None
    speed = 6
    health = 10

    def __init__(self, pos, direct, owner):
        Bullet.__init__(self, owner)
        self.name = self.owner.name + ":bounceBullet"
        self.image = load_image('bouncebullet.gif')
        self.direct = direct
        self.rect = self.image.get_rect(center=pos)
        # 最多弹得次数
        self.bouncetime = 10
        self.now_bouncetimetime = self.bouncetime
        if collision(self, rect=self.rect) and SCREENRECT.colliderect(self.rect) and self.owner.bgmap.map_passive(self.rect):
            pass
        else:
            self.died()
            print "bounceBullet died"

    def died(self):
        self.kill()

    def more_effect(self, target):
        Frozen(target)

    def change_direct(self, direct):
        self.new_rect = self.rect.move((direct[0] * self.speed, direct[1] * self.speed))
        if collision(self, rect=self.new_rect) and SCREENRECT.colliderect(self.new_rect) and self.owner.bgmap.map_passive(self.new_rect):
            self.direct = direct
            self.rect = self.new_rect
            return True

    def update(self, *args):
        all_directs = [self.direct, (-self.direct[0], self.direct[1]), (self.direct[0], -self.direct[1]), (-self.direct[0], -self.direct[1])]
        for direct in all_directs:
            if self.change_direct(direct):
                #print self.direct, all_directs[0]
                if self.direct != all_directs[0]:
                    self.bouncetime = self.bouncetime - 1
                    if self.bouncetime <= 0:
                        self.died()
                break

