#encoding=utf-8
"""坦克模型"""
import random
import math

import pygame
from pygame.locals import *

from libs import *
from game import *
from bullet import *
from collision import *
from start import *
from skills import *
from renders import *


class Tankstate_both(State):
    # 判断出生时 不能和 mytank 重叠
    def __init__(self, tank):
        State.__init__(self, "both")
        self.mold = tank

    def do_actions(self):
        pass

    def check_conditions(self):
        if not collision(self.mold, rect=self.mold.rect) or not self.mold.bgmap.map_passive(self.mold.rect):
            self.mold.both = False
            print self.mold.name + "both no pass"
        else:
            self.mold.both = True
            return 'move'


class Tankstate_move(State):
    def __init__(self, tank):
        State.__init__(self, "move")
        self.mold = tank

    def do_actions(self):
        # 如果不在屏幕内 则消失
        if not SCREENRECT.contains(self.mold.rect):
            self.mold.kill()
        self.mold.new_rect = self.mold.rect.move(self.mold.direct[0] * self.mold.speed[0],
                                 self.mold.direct[1] * self.mold.speed[1])

    def check_conditions(self):
        if not SCREENRECT.contains(self.mold.new_rect)\
                            or not self.mold.bgmap.map_passive(self.mold.new_rect):
            return "thinkdirect"
        elif self.mold.conf.get("turn_rate") and random.random() < self.mold.conf["turn_rate"]:
            return "thinkdirect"

        passive = collision(self.mold)
        if passive:
            self.mold.rect = self.mold.new_rect
        if self.mold.conf.get("target"):
            return "thinkdirect"
        return


class Tankstate_thinkdirect(State):
    """思考行动方向"""
    def __init__(self, tank):
        State.__init__(self, "thinkdirect")
        self.mold = tank

    def do_actions(self):
        if self.mold.conf.get("target") and self.mold._target:
            target_pos = self.mold._target.rect.center
            self_pos = self.mold.rect.center
            path = (target_pos[0] - self_pos[0], target_pos[1] - self_pos[1])
            if abs(path[0]) > abs(path[1]):
                self.mold.direct1 = (1 if path[0] > 0 else -1, 0)
                self.mold.direct2 = (0, 1 if path[1] > 0 else -1)
            else:
                self.mold.direct2 = (1 if path[0] > 0 else -1, 0)
                self.mold.direct1 = (0, 1 if path[1] > 0 else -1)
            self.mold.direct = self.mold.direct1
            self.mold.new_rect = self.mold.rect.move(self.mold.direct[0] * self.mold.speed[0],
                     self.mold.direct[1] * self.mold.speed[1])
            if not SCREENRECT.contains(self.mold.new_rect)\
                        or not self.mold.bgmap.map_passive(self.mold.new_rect):
                l = self.mold.conf["images"].keys()
                l.remove(self.mold.direct)
                self.mold.direct = self.mold.direct2
                self.mold.new_rect = self.mold.rect.move(self.mold.direct[0] * self.mold.speed[0],
                     self.mold.direct[1] * self.mold.speed[1])
                if not SCREENRECT.contains(self.mold.new_rect)\
                        or not self.mold.bgmap.map_passive(self.mold.new_rect):
                    l.remove(self.mold.direct)
                    self.mold.direct = random.choice(l)
        else:
            l = self.mold.conf["images"].keys()
            if len(l) > 1:
                l.remove(self.mold.direct)
                direction = random.choice(l)
            else:
                direction = l[0]
            self.mold.direct = direction

    def check_conditions(self):
        return "turn"


class Tankstate_turn(State):
    def __init__(self, tank):
        State.__init__(self, "turn")
        self.mold = tank

    def do_actions(self):
        if not self.mold.conf.get("image_nochange"):
            self.mold.image = self.mold.images[self.mold.direct]

    def check_conditions(self):
        return 'move'


class Tankstate_died(State):
    def __init__(self, tank):
        State.__init__(self, "died")
        self.mold = tank

        self.mold.died_speed = 10
        self.mold.died_steps = (len(self.mold.died_images) - 1) * self.mold.died_speed
        self.mold.now_died_step = 0

    def do_actions(self):
        self.mold.image = self.mold.died_images[self.mold.now_died_step / self.mold.died_speed]
        if self.mold.now_died_step < self.mold.died_steps:
            self.mold.now_died_step = self.mold.now_died_step + 1
        else:
            self.mold.kill()

    def check_conditions(self):
        return 'died'


class Tank(pygame.sprite.Sprite):
    def __init__(self, game_items, bgmap):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.game_items = game_items
        self.bgmap = bgmap
        self.bullet_type = NormalBullet

    def move(self):
        pass

    def shot(self, direct=None, pos=None):
        if direct and pos:
            pass
        else:
            direct = self.direct
            if self.direct == (0, -1):
                pos = self.rect.midtop
            elif self.direct == (1, 0):
                pos = self.rect.midright
            elif self.direct == (0, 1):
                pos = self.rect.midbottom
            elif self.direct == (-1, 0):
                pos = self.rect.midleft
        self.bullet_type(pos, direct, self)

    def wounded(self, wound):
        self.health = self.health - wound
        if self.health <= 0:
            self.died()

    def died(self):
        Explod(self.died_images, self.rect.center)
        self.kill()

    def update(self):
        pass

    def bgmap_passive(self, rect):
        return self.bgmap.map_passive(rect)


class Mytank(Tank):
    conf = Readconf("conf_of_living/mytank.txt")
    shoting = 0
    images = None     # 静态变量存储，所有的实例公用同样的内存，不会再次读取图片
    died_images = None

    def __init__(self, game_items, screen, bgmap, both_point=None, contrlmap=False):
        Tank.__init__(self, game_items, bgmap)
        self.name = self.conf["name"]
        self.images = load_images_bykey(self.conf["images"])
        self.died_images = load_images(*self.conf["died_images"])
        self.direct = (0, -1)
        self.image = self.images[self.direct]
        if both_point:
            self.rect = self.image.get_rect(topleft=both_point)
        else:
            self.rect = self.image.get_rect(midbottom=SCREENRECT.center)

        # 属性状态
        self.health = self.conf["maxhealth"]
        self.movable = True
        self.skillable = True
        self.skilling = False
        self.shootable = True
        self.speed = self.conf["speed"]
        # skill
        self.maxfireshield = 15
        self.maxsnipe = 5
        # 血条
        self.screen = screen
        healthpannel(self.screen, self.health / self.conf["maxhealth"])
        # 是否控制地图
        self.contrlmap = contrlmap

    def move(self, keystate):
        direction = None
        if keystate[K_w]:
            direction = (0, -1)
        elif keystate[K_d]:
            direction = (1, 0)
        elif keystate[K_s]:
            direction = (0, 1)
        elif keystate[K_a]:
            direction = (-1, 0)
        if direction:

            if self.direct == direction:
                self.new_rect = self.rect.move(direction[0] * self.speed[0],
                                     direction[1] * self.speed[1])
                # print "#", self.new_rect.right
                if collision(self) and self.bgmap.map_passive(self.new_rect):
                    self.rect = self.new_rect
                    self.rect = self.rect.clamp(SCREENRECT)
                if self.contrlmap and direction == (0, -1) and self.rect.top <= SCREEN_HEIGHT / 2:
                    self.bgmap.move_by_player(self.speed[1])
            else:
                self.direct = direction
                self.image = self.images[self.direct]

    def update(self, keystate):
        if not self.skilling and self.skillable:
            self.do_skill(keystate)
        if self.movable:
            self.move(keystate)
        # firing 判断是否已经在开炮
        if self.shootable:
            firing = keystate[K_j]
            if not self.shoting and firing:
                self.shot()
            self.shoting = firing

    def wounded(self, wound):
        self.health = self.health - wound
        healthpannel(self.screen, self.health / self.conf["maxhealth"])
        if self.health <= 0:
            self.died()

    def do_skill(self, keystate):
        if keystate[K_u] and self.maxsnipe:
            self.maxsnipe -= 1
            Snipe(self)
        elif keystate[K_k] and self.maxfireshield > 0:
            Fireshield(self)
            self.maxfireshield = self.maxfireshield - 1


class Ai_tank(Tank, pygame.sprite.Sprite):
    images = None
    died_images = None
    conf = Readconf("conf_of_living/ai_normal_tank.txt")

    def __init__(self, game_items, bgmap, both_position=None):
        Tank.__init__(self, game_items, bgmap)
        self.name = self.conf["name"]
        self.health = self.conf["maxhealth"]
        self.images = load_images_bykey(self.conf["images"])
        self.died_images = load_images(*self.conf["died_images"])
        # ai 行动 状态机
        self.brain = StateMachine()
        bothing_state = Tankstate_both(self)
        moving_state = Tankstate_move(self)
        turning_state = Tankstate_turn(self)
        thinkingdirect_state = Tankstate_thinkdirect(self)
        dieding_state = Tankstate_died(self)

        self.brain.add_state(bothing_state)
        self.brain.add_state(moving_state)
        self.brain.add_state(turning_state)
        self.brain.add_state(thinkingdirect_state)
        self.brain.add_state(dieding_state)
        self.both = None
        self.brain.set_state("both")
        self.direct = random.choice(self.images.keys())
        self.image = self.images[self.direct]
        if both_position:
            left, top = both_position
        else:
            left = random.randint(0, SCREENRECT.width - self.image.get_width())
            top = random.randint(0, SCREENRECT.height - self.image.get_height())
        self.rect = self.image.get_rect(topleft=(left, top))
        # ai坦克 属性
        self.aitank_shot_time_range = time_to_frams(self.conf["shot_time_range"])
        self.shot_time = random.randint(*self.aitank_shot_time_range)
        self.speed = self.conf["speed"]
        self.shoting = 0
        self.brain.think()

    def update(self, *args):

        if self.shot_time == 0:
            self.shot()
            self.shot_time = random.randint(*self.aitank_shot_time_range)
        else:
            self.shot_time = self.shot_time - 1
        self.brain.think()


class Terrorsmallspider(Tank, pygame.sprite.Sprite):
    images = None
    died_images = None

    def __init__(self, game_items, bgmap, both_position=None):
        Tank.__init__(self, game_items, bgmap)
        self.conf = Readconf("conf_of_living/ai_terrorsmallspider.txt")
        self.name = self.conf["name"]
        self.health = self.conf["maxhealth"]
        self.images = load_images_bykey(self.conf["images"])
        self.died_images = load_images(*self.conf["died_images"])
        #  确定目标
        self._target = None
        for item in self.game_items:
            if item.name == "mytank":
                self._target = item
                break

        self.brain = StateMachine()
        bothing_state = Tankstate_both(self)
        moving_state = Tankstate_move(self)
        turning_state = Tankstate_turn(self)
        thinkingdirect_state = Tankstate_thinkdirect(self)
        dieding_state = Tankstate_died(self)

        self.brain.add_state(bothing_state)
        self.brain.add_state(moving_state)
        self.brain.add_state(turning_state)
        self.brain.add_state(thinkingdirect_state)
        self.brain.add_state(dieding_state)
        self.both = None
        self.brain.set_state("both")

        self.direct = random.choice(self.images.keys())
        self.image = self.images[self.direct]

        if both_position:
            left, top = both_position
        else:
            left = random.randint(0, SCREENRECT.width - self.image.get_width())
            top = random.randint(0, SCREENRECT.height - self.image.get_height())
        self.rect = self.image.get_rect(topleft=(left, top))

        self.speed = self.conf["speed"]
        self.Movable = True
        self.brain.think()

    def update(self, *args):
        self.brain.think()


class Bossspider(Tank, pygame.sprite.Sprite):
    images = None
    died_images = None

    def __init__(self, game_items, bgmap, both_position=None):
        Tank.__init__(self, game_items, bgmap)
        self.conf = Readconf("conf_of_living/ai_bossspider.txt")
        self.name = self.conf["name"]
        self.health = self.conf["maxhealth"]
        self.images = load_images_bykey(self.conf["images"])
        self.died_images = load_images(*self.conf["died_images"])
        self.brain = StateMachine()
        bothing_state = Tankstate_both(self)
        moving_state = Tankstate_move(self)
        turning_state = Tankstate_turn(self)
        thinkingdirect_state = Tankstate_thinkdirect(self)
        dieding_state = Tankstate_died(self)

        self.brain.add_state(bothing_state)
        self.brain.add_state(moving_state)
        self.brain.add_state(turning_state)
        self.brain.add_state(thinkingdirect_state)
        self.brain.add_state(dieding_state)
        self.both = None
        self.brain.set_state("both")

        self.direct = (0, 1)
        self.image = self.images[self.direct]

        if both_position:
            left, top = both_position
        else:
            left = random.randint(0, SCREENRECT.width - self.image.get_width())
            top = random.randint(0, SCREENRECT.height - self.image.get_height())
        self.rect = self.image.get_rect(topleft=(left, top))

        self.speed = self.conf["speed"]
        self.moveable = True
        self.aitank_shot_time_range = [time * SCREEN_PER_SEC for time in self.conf["shot_time_range"]]
        self.shot_time = random.randint(*self.aitank_shot_time_range)
        self.brain.think()

    def shot(self, pos=None):
        pos = self.rect.midbottom[0] - 10, self.rect.midbottom[1] - 20
        Terrorsmallspider(self.game_items, self.bgmap, both_position=pos)

    def died(self):
        Explod(self.died_images, self.rect.center, replaytime=5)
        self.kill()

    def update(self, *args):
        if self.shot_time == 0:
            self.shot()
            self.shot_time = random.randint(*self.aitank_shot_time_range)
        else:
            self.shot_time = self.shot_time - 1
        self.brain.think()


class Beam_Golem(Tank, pygame.sprite.Sprite):
    # 激光机器人
    def __init__(self, game_items, bgmap, both_position=None):
        Tank.__init__(self, game_items, bgmap)
        self.conf = Readconf("conf_of_living/ai_beamgolem.txt")
        self.name = self.conf["name"]
        self.health = self.conf["maxhealth"]
        self.images = load_images_bykey(self.conf["images"])
        self.died_images = load_images(*self.conf["died_images"])
        # ai 行动 状态机
        self.brain = StateMachine()
        bothing_state = Tankstate_both(self)
        moving_state = Tankstate_move(self)
        turning_state = Tankstate_turn(self)
        thinkingdirect_state = Tankstate_thinkdirect(self)
        dieding_state = Tankstate_died(self)

        self.brain.add_state(bothing_state)
        self.brain.add_state(moving_state)
        self.brain.add_state(turning_state)
        self.brain.add_state(thinkingdirect_state)
        self.brain.add_state(dieding_state)
        self.both = None
        self.brain.set_state("both")
        self.direct = random.choice(self.images.keys())
        self.image = self.images[self.direct]
        if both_position:
            left, top = both_position
        else:
            left = random.randint(0, SCREENRECT.width - self.image.get_width())
            top = random.randint(0, SCREENRECT.height - self.image.get_height())
        self.rect = self.image.get_rect(topleft=(left, top))
        # ai坦克 属性
        self.aitank_shot_time_range = time_to_frams(self.conf["shot_time_range"])
        self.shot_time = random.randint(*self.aitank_shot_time_range)
        self.speed = self.conf["speed"]
        self.shoting = 0
        self.brain.think()

        self.bullet_type = BeamBullet

    def update(self, *args):

        if self.shot_time == 0:
            self.shot()
            self.shot_time = random.randint(*self.aitank_shot_time_range)
        else:
            self.shot_time = self.shot_time - 1
        self.brain.think()


class Bossgoddess(Tank, pygame.sprite.Sprite):
    """女神boss"""
    health = 500

    def __init__(self, game_items, bgmap, both_position=None):
        Tank.__init__(self, game_items, bgmap)
        self.name = "ai_bossgoddess"
        self.images = loadimage_to_slices("bossgoddess.gif", 18)
        self.died_images = self.images
        self.imageindex = 0
        self.image = self.images[self.imageindex]
        self.rect = self.image.get_rect(topleft=both_position)
        self.keeptime = 5  # 控制每幅图的静止帧数
        self.nowkeeptime = self.keeptime

        # self.skilltime = time_to_frams(3)
        # self.nowskilltime = self.skilltime

    def killself(self):
        self.kill()

    def update(self, *args):
        if self.nowkeeptime == 0:
            self.nowkeeptime = self.keeptime
            if self.imageindex < len(self.images) - 1:
                self.imageindex = self.imageindex + 1
                self.image = self.images[self.imageindex]
                if self.imageindex == 10:
                    IcePicr(self, (self.rect.left - 100, 40))
                    IcePicr(self, (self.rect.left - 90, 60))
                    IcePicr(self, (self.rect.left + 20, 40))
                    IcePicr(self, (self.rect.left + 130, 40))
                    IcePicr(self, (self.rect.left + 120, 60))
                elif self.imageindex == 15:
                    for item in self.game_items:
                        if item.name == "mytank":
                            targetpoint = item.rect.center
                            Meteor(self, (self.rect.left - 150, 10), targetpoint)
                            break
                elif self.imageindex == 5:
                    for item in self.game_items:
                        if item.name == "mytank":
                            targetpoint = item.rect.center
                            Rattan(self, (item.rect.left - 50, item.rect.top - 50))
                            break
            else:
                self.imageindex = 0
                #self.killself()
        else:
            self.nowkeeptime = self.nowkeeptime - 1

    def wounded(self, wound):
        self.health = self.health - wound
        if self.health <= 0:
            self.died()

    def died(self):
        Explod(self.died_images, self.rect.center, replaytime=5)
        self.kill()


class Pullwave_Golem(Tank, pygame.sprite.Sprite):
    # 吸引波机器人
    def __init__(self, game_items, bgmap, both_position=None):
        Tank.__init__(self, game_items, bgmap)
        self.conf = Readconf("conf_of_living/ai_pullwavegolem.txt")
        self.name = self.conf["name"]
        self.health = self.conf["maxhealth"]
        self.images = load_images_bykey(self.conf["images"])
        self.died_images = load_images(*self.conf["died_images"])
        # ai 行动 状态机
        self.brain = StateMachine()
        bothing_state = Tankstate_both(self)
        moving_state = Tankstate_move(self)
        turning_state = Tankstate_turn(self)
        thinkingdirect_state = Tankstate_thinkdirect(self)
        dieding_state = Tankstate_died(self)

        self.brain.add_state(bothing_state)
        self.brain.add_state(moving_state)
        self.brain.add_state(turning_state)
        self.brain.add_state(thinkingdirect_state)
        self.brain.add_state(dieding_state)
        self.both = None
        self.brain.set_state("both")
        self.direct = random.choice(self.images.keys())
        self.image = self.images[(0, 1)]
        if both_position:
            left, top = both_position
        else:
            left = random.randint(0, SCREENRECT.width - self.image.get_width())
            top = random.randint(0, SCREENRECT.height - self.image.get_height())
        self.rect = self.image.get_rect(topleft=(left, top))
        # ai坦克 属性
        self.aitank_shot_time_range = time_to_frams(self.conf["shot_time_range"])
        self.shot_time = random.randint(*self.aitank_shot_time_range)
        self.speed = self.conf["speed"]
        self.shoting = 0
        self.brain.think()

        self.bullet_type = PullWave

        # 放波的持续时间
        self.keepshottime = time_to_frams(5)
        self.now_keepshottime = self.keepshottime

    def update(self, *args):

        if self.shot_time == 0:
            if self.shoting:
                if self.now_keepshottime > 0:
                    if self.now_keepshottime % 5 == 0:
                        self.shot()

                    self.now_keepshottime = self.now_keepshottime - 1
                else:
                    self.shooting = 0
                    self.shot_time = random.randint(*self.aitank_shot_time_range)
                    self.now_keepshottime = self.keepshottime
            else:
                self.shoting = 1
        else:
            self.shot_time = self.shot_time - 1
            self.brain.think()


class Pushwave_Golem(Ai_tank, pygame.sprite.Sprite):
    # 推动波机器人
    images = None
    died_images = None
    conf = Readconf("conf_of_living/ai_pushwavegolem.txt")

    def __init__(self, game_items, bgmap, both_position=None):
        Ai_tank.__init__(self, game_items, bgmap, both_position)
        self.bullet_type = PushWave


class Obstruction (Tank, pygame.sprite.Sprite):
    # 障碍物父类
    conf = None

    def __init__(self, game_items, bgmap, both_position=None):
        Tank.__init__(self, game_items, bgmap)
        self.name = self.conf["name"]
        self.health = self.conf["maxhealth"]
        self.died_images = load_images(*self.conf["died_images"])

        self.image = load_image(self.conf["images"].values()[0])
        if both_position:
            left, top = both_position
        else:
            left = random.randint(0, SCREENRECT.width - self.image.get_width())
            top = random.randint(0, SCREENRECT.height - self.image.get_height())
        self.rect = self.image.get_rect(topleft=(left, top))

        self.both = True
        # 属性

    def ablity(self):
        # 特殊能力
        pass

    def update(self, *args):
        pass


class TankFactory(Obstruction, pygame.sprite.Sprite):
    # 工厂
    conf = Readconf("conf_of_living/ai_tank_factory.txt")

    def __init__(self, game_items, bgmap, both_position=None):
        Obstruction.__init__(self, game_items, bgmap, both_position)
        # 属性
        self.aitank_shot_time_range = time_to_frams(self.conf["shot_time_range"])
        self.shot_time = random.randint(*self.aitank_shot_time_range)

    def ablity(self):
        if self.shot_time == 0:
            Ai_tank(self.game_items, self.bgmap, both_position=(self.rect.midbottom[0] - 16, self.rect.midbottom[1]))
            self.shot_time = random.randint(*self.aitank_shot_time_range)
        else:
            self.shot_time = self.shot_time - 1

    def update(self, *args):
        self.ablity()
        # 如果不在屏幕内 则消失
        if not SCREENRECT.contains(self.rect):
            self.kill()

    def wounded(self, wound):
        self.health = self.health - wound
        if self.health <= 0:
            self.died()


class Pillbox(Obstruction, pygame.sprite.Sprite):
    # 碉堡
    conf = Readconf("conf_of_living/ai_pillbox.txt")

    def __init__(self, game_items, bgmap, both_position=None):
        Obstruction.__init__(self, game_items, bgmap, both_position)
        self.nochange_image = self.image.copy()
        self.direct = (0, 1)
        self.angle = None
        self.new_direct = self.direct
        self.center_point = self.rect.center
        self.aitank_shot_time_range = time_to_frams(self.conf["shot_time_range"])
        self.shot_time = random.randint(*self.aitank_shot_time_range)
        self.shot = PillboxBullet

    def change_direct(self):
        for item in self.game_items:
            if item.name == "mytank":
                targetpoint = item.rect.center
                targetvector = pygame.math.Vector2(targetpoint)
                selfvector = pygame.math.Vector2(self.rect.center)

                self.new_direct = (targetvector - selfvector).normalize()
                self.angle = math.acos(self.new_direct * self.direct) * 180 / math.pi
                if item.rect.center[0] < self.rect.center[0]:
                    self.angle = -self.angle
                self.image = pygame.transform.rotate(self.nochange_image, self.angle)
                self.center_point = self.rect.center
                self.rect = self.image.get_rect(center=self.center_point)
                break

    def ablity(self):

        if self.shot_time == 0:
            self.change_direct()
            if self.angle:
                self.shot(direct=self.new_direct, angle=self.angle, owner=self)
            self.shot_time = random.randint(*self.aitank_shot_time_range)
        else:
            self.shot_time = self.shot_time - 1

    def update(self, *args):
        self.ablity()
        # 如果不在屏幕内 则消失
        if not SCREENRECT.contains(self.rect):
            self.kill()

    def wounded(self, wound):
        self.health = self.health - wound
        if self.health <= 0:
            self.died()


class Ai_icetank(Ai_tank, pygame.sprite.Sprite):
    # 冰弹机器人
    images = None
    died_images = None
    conf = Readconf("conf_of_living/ai_icetank.txt")

    def __init__(self, game_items, bgmap, both_position=None):
        Ai_tank.__init__(self, game_items, bgmap, both_position)
        self.bullet_type = IceBullet

    def more_effect(self, target):
        Frozen(target)


class Bossflowerfairy(Tank, pygame.sprite.Sprite):
    """花仙boss"""
    health = 500

    def __init__(self, game_items, bgmap, both_position=None):
        Tank.__init__(self, game_items, bgmap)
        self.name = "ai_bossflowerfairy"
        self.image = load_image("bossflowerfairy.gif")
        self.died_images = None

        self.rect = self.image.get_rect(topleft=both_position)

        self.keeptime = time_to_frams(10)  # 控制一轮现形和隐形的时间
        self.nowkeeptime = self.keeptime

        self.skill_disperse_flower_starttime = time_to_frams(8)     # 撒花技能开始时间
        self.showtime = time_to_frams(5)    # 现形的时间
        self.skill_rain_flower_starttime = time_to_frams(4)     # 落花技能开始时间

        # self.skilltime = time_to_frams(3)
        # self.nowskilltime = self.skilltime
        self.tops = [5, 40, 80]
        self.lefts = [5, 40, 70, 100, 130, 160]

        # 撒花时花的所有方向
        self.firstvector = pygame.math.Vector2((0, 1))
        self.allvector = []
        self.disperse_flower_num = 36
        angle = 360 / self.disperse_flower_num
        for i in range(0, self.disperse_flower_num):
            vector = self.firstvector.rotate(angle * i)
            self.allvector.append(vector)
        # 每次落花 数量  与boss中心间距范围
        self.rain_flower_num = 10
        self.rain_flower_gap = 100
        # 放花时间间隔, 放花次数  放花具体时间
        self.disperse_flower_interval_time = time_to_frams(0.8)
        self.rain_flower_interval_time = time_to_frams(0.5)
        self.skill_disperse_flower_frequency = 4
        self.skill_rain_flower_frequency = 8

        def get_times(start_time, interval_time, frequency):
            times = []
            for i in range(0, frequency):
                times.append(start_time - interval_time * i)
            return times
        self.skill_disperse_flower_time = get_times(self.skill_disperse_flower_starttime, self.disperse_flower_interval_time, self.skill_disperse_flower_frequency)
        self.skill_rain_flower_time = get_times(self.skill_rain_flower_starttime, self.rain_flower_interval_time, self.skill_rain_flower_frequency)

    def killself(self):
        self.kill()

    def show(self):
        self.rect = self.image.get_rect(topleft=(self.top, self.left))

    def hide(self):
        self.rect = self.image.get_rect(topleft=(-1000, 0))
        self.top = random.choice(self.tops)
        self.left = random.choice(self.lefts)

    def disperse_flower(self):
        for vector in self.allvector:
            Flower(self, self.rect.center, vector)

    def rain_flower(self):
        leftrange = (self.left - self.rain_flower_gap, self.left + self.image.get_width() + self.rain_flower_gap)
        for i in range(0, self.rain_flower_num):
            left = random.randint(*leftrange)
            Flower(self, (left, 0), self.firstvector)

    def update(self, *args):
        self.nowkeeptime = self.nowkeeptime - 1
        if self.nowkeeptime == 0:
            self.nowkeeptime = self.keeptime
            self.show()
        elif self.nowkeeptime == self.showtime:
            self.hide()
        elif self.nowkeeptime in self.skill_disperse_flower_time:
            self.disperse_flower()
        elif self.nowkeeptime in self.skill_rain_flower_time:
            self.rain_flower()

    def wounded(self, wound):
        self.health = self.health - wound
        if self.health <= 0:
            self.died()

    def died(self):
        #Explod(self.died_images, self.rect.center, replaytime=5)
        self.kill()


class swordsman(Tank, pygame.sprite.Sprite):
    """剑客boss   未完成"""
    health = 500

    def __init__(self, game_items, bgmap, both_position=None):
        Tank.__init__(self, game_items, bgmap)
        self.name = "ai_bossswordsman"
        self.image = load_image("bossswordsman.gif")
        pass

    def wounded(self, wound):
        self.health = self.health - wound
        if self.health <= 0:
            self.died()

    def died(self):
        #Explod(self.died_images, self.rect.center, replaytime=5)
        self.kill()


class Bossbouncer(Ai_tank, pygame.sprite.Sprite):
    # 弹球机器人
    images = None
    died_images = None
    conf = Readconf("conf_of_living/bossbouncer.txt")
    shot_gap = 50

    def __init__(self, game_items, bgmap, both_position=None):
        Ai_tank.__init__(self, game_items, bgmap, both_position)
        self.bullet_type = BounceBullet

    def shot(self, direct=None, pos=None):
        if direct and pos:
            pass
        else:
            direct = self.direct
            pos = self.rect.center[0] + self.shot_gap * self.direct[0], self.rect.center[1] + self.shot_gap * self.direct[1]
        self.bullet_type(pos, direct, self)
