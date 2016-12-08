#encoding=utf-8
"""控制关卡"""
import random

import pygame
from pygame.locals import *

from libs import *
from tanks import *
from start import *
from renders import Bgmap
from skills import *


class Stagestate_nothing(State):
    def __init__(self, stage):
        State.__init__(self, "nothing")
        self.stage = stage

    def do_actions(self):
        pass

    def check_conditions(self):
        return


class Stagestate_begin(State):
    def __init__(self, stage):
        State.__init__(self, "begin")
        self.stage = stage
        self.keeptime = 60
        self.stage.screen.blit(self.stage.start_image, (0, 0))

    def do_actions(self):
        self.keeptime = self.keeptime - 1

    def check_conditions(self):
        if self.keeptime:
            return
        else:
            self.stage.begin()
            return "servant"


class Stagestate_servant(State):
    # 打小兵阶段
    def __init__(self, stage):
        State.__init__(self, "servant")
        self.stage = stage

    def do_actions(self):
        self.stage.servant()

    def check_conditions(self):
        if self.stage.servant_over:
            return "startboss"
        elif not len(self.stage.player):
            return "fail"
        return


class Stagestate_startboss(State):
    # boss出场场景
    def __init__(self, stage):
        State.__init__(self, "startboss")
        self.stage = stage

    def do_actions(self):
        self.stage.startboss()

    def check_conditions(self):
        return "boss"


class Stagestate_boss(State):
    # 打boss阶段
    def __init__(self, stage):
        State.__init__(self, "boss")
        self.stage = stage

    def do_actions(self):
        if not self.stage.boss_both:
            self.stage.boss()

    def check_conditions(self):
        return self.stage.check_win()


class Stagestate_win(State):
    # 通关特效等
    def __init__(self, stage):
        State.__init__(self, "win")
        self.stage = stage
        self.keeptime = 100
        self.first = True

    def do_actions(self):
        if self.first:
            self.first = False
            self.stage.win()
        if self.keeptime:
            self.keeptime = self.keeptime - 1
        else:
            self.stage.statu = "win"

    def check_conditions(self):
        return


class Stagestate_fail(State):
    # 失败
    def __init__(self, stage):
        State.__init__(self, "fail")
        self.stage = stage
        self.keeptiem = 200
        self.first = True

    def do_actions(self):
        if self.first:
            self.first = False
            self.stage.fail()
        if self.keeptiem:
            self.keeptiem = self.keeptiem - 1
        else:
            self.stage.statu = "fail"

    def check_conditions(self):
        return


class Stage:
    def __init__(self, screen):
        self.screen = screen
        self.start_image = None
        self.game_items = pygame.sprite.Group()             # 世界
        self.bulletgroup = pygame.sprite.Group()            # 子弹
        self.servantgroup = pygame.sprite.Group()           # 小兵
        self.bossgroup = pygame.sprite.Group()              # boss
        self.player = pygame.sprite.Group()                 # 玩家
        self.renders = pygame.sprite.Group()                # 特效
        self.skills = pygame.sprite.Group()                 # 技能
        Mytank.containers = self.player, self.game_items

        Render.containers = self.renders, self.game_items
        Skill.containers = self.skills, self.game_items
        Tank.containers = self.servantgroup, self.game_items
        Bullet.containers = self.bulletgroup, self.game_items

        self.stage_begin = False

    def begin(self):
        self.stage_begin = True

    def process(self, keystate):
        if self.stage_begin:
            backmap = self.bgmap.update()
            self.game_items.update((keystate))
            self.skills.update((keystate))
            self.bulletgroup.draw(backmap)         # 先画子弹 为了不让覆盖坦克 应该先画
            self.servantgroup.draw(backmap)
            self.player.draw(backmap)
            self.renders.draw(backmap)
            self.skills.draw(backmap)
            self.screen.blit(backmap, (0, 0))
        self.brain.think()
        return self.statu

    def over(self):
        pass

    def both_enemy(self):
        ai_tank = None
        for left_position in (self.bgmap.get_enemy()):
            if left_position[0] == 6:
                ai_tank = Ai_tank(self.game_items, self.bgmap, (left_position[1], 0))
            elif left_position[0] == 5:
                ai_tank = Beam_Golem(self.game_items, self.bgmap, (left_position[1], 0))
            elif left_position[0] == 7:
                ai_tank = Pullwave_Golem(self.game_items, self.bgmap, (left_position[1], 0))
            elif left_position[0] == 8:
                ai_tank = Pushwave_Golem(self.game_items, self.bgmap, (left_position[1], 0))
            elif left_position[0] == 10:
                ai_tank = TankFactory(self.game_items, self.bgmap, (left_position[1], 0))
            elif left_position[0] == 11:
                ai_tank = Pillbox(self.game_items, self.bgmap, (left_position[1], 0))
            elif left_position[0] == 4:
                ai_tank = Ai_icetank(self.game_items, self.bgmap, (left_position[1], 0))
            if ai_tank and ai_tank.both:
                pass
            else:
                ai_tank.kill()
                print "both fail"

    def check_win(self):
        if self.boss_both and not len(self.servantgroup):
            return "win"
        elif not len(self.player):
            return "fail"

    def win(self):
        pass

    def fail(self):
        pass


class Stage1(Stage):
    def __init__(self, screen):
        Stage.__init__(self, screen)
        self.start_image = load_image("stage1_start.gif")
        # Ai_tank.containers = self.servantgroup, self.game_items
        # Terrorsmallspider.containers = self.servantgroup, self.game_items
        # Bossspider.containers = self.servantgroup, self.game_items
        # NormalBullet.containers = self.bulletgroup, self.game_items

        # 返回给game的关卡状态  None为继续   win，fail 为关卡胜利，失败
        self.statu = None
        # 关卡初始化
        self.boss_position = (160, 30)
        # 小兵打完 才出boss
        self.servant_over = False
        self.boss_both = False

        # 状态机
        self.brain = StateMachine()
        nothing_state = Stagestate_nothing(self)
        begin_state = Stagestate_begin(self)
        servant_state = Stagestate_servant(self)
        startboss_state = Stagestate_startboss(self)
        boss_state = Stagestate_boss(self)
        win = Stagestate_win(self)
        fail_state = Stagestate_fail(self)

        self.brain.add_state(nothing_state)
        self.brain.add_state(begin_state)
        self.brain.add_state(servant_state)
        self.brain.add_state(startboss_state)
        self.brain.add_state(boss_state)
        self.brain.add_state(win)
        self.brain.add_state(fail_state)
        self.brain.set_state("begin")

    def begin(self):
        self.stage_begin = True
        self.bgmap = Bgmap(map=r'maps\111.jpg', statu=None, bitmap=r"maps\111.txt", game_items=self.game_items)
        Mytank_both_point = (88, 384)
        Mytank(self.game_items, self.screen, self.bgmap, both_point=Mytank_both_point, contrlmap=True)

    def servant(self):
        self.both_enemy()
        self.servant_over = self.bgmap.map_over
        pass

    def startboss(self):
        # 出场动画
        self.animation_bothof_boss = Animation_bothof_bossspider((160, -80))

    def boss(self):
        if self.animation_bothof_boss.rect.topleft[1] >= 30:
            self.animation_bothof_boss.killself()
            Bossspider(self.game_items, self.bgmap, self.boss_position)
            self.boss_both = True


class Stage4(Stage):
    def __init__(self, screen):
        Stage.__init__(self, screen)
        self.start_image = load_image("stage4_start.gif")
        # 返回给game的关卡状态  None为继续   win，fail 为关卡胜利，失败
        self.statu = None

        # 小兵打完 才出boss
        self.boss_position = (160, 30)
        self.servant_over = False
        self.boss_both = False

        # 状态机
        self.brain = StateMachine()
        nothing_state = Stagestate_nothing(self)
        begin_state = Stagestate_begin(self)
        servant_state = Stagestate_servant(self)
        startboss_state = Stagestate_startboss(self)
        boss_state = Stagestate_boss(self)
        win = Stagestate_win(self)
        fail_state = Stagestate_fail(self)

        self.brain.add_state(nothing_state)
        self.brain.add_state(begin_state)
        self.brain.add_state(servant_state)
        self.brain.add_state(startboss_state)
        self.brain.add_state(boss_state)
        self.brain.add_state(win)
        self.brain.add_state(fail_state)
        self.brain.set_state("begin")

    def begin(self):
        self.stage_begin = True
        # 关卡初始化
        self.bgmap = Bgmap(map=r'maps\222.jpg', statu=None, bitmap=r"maps\222.txt", game_items=self.game_items)
        Mytank_both_point = (167, 500)
        #self.bgmap = Bgmap(map=None, statu=None, bitmap=None, game_items=self.game_items)
        Mytank(self.game_items, self.screen, self.bgmap, both_point=Mytank_both_point, contrlmap=True)

    def servant(self):
        self.both_enemy()
        self.servant_over = self.bgmap.map_over and not len(self.servantgroup)
        pass

    def startboss(self):
        # 出场动画
        print "me"
        #self.animation_bothof_boss = Animation_bothof_bossgoddess((160, 20))

    def boss(self):
        # self.bgmap = Bgmap(map=None, statu=None, bitmap=None, game_items=self.game_items)
        Bossgoddess(self.game_items, self.bgmap, self.boss_position)
        self.boss_both = True


class Stage3(Stage):
    def __init__(self, screen):
        Stage.__init__(self, screen)
        self.start_image = load_image("stage3_start.gif")
        # 返回给game的关卡状态  None为继续   win，fail 为关卡胜利，失败
        self.statu = None

        # 小兵打完 才出boss
        self.boss_position = (160, 30)
        self.servant_over = False
        self.boss_both = False

        # 状态机
        self.brain = StateMachine()
        nothing_state = Stagestate_nothing(self)
        begin_state = Stagestate_begin(self)
        servant_state = Stagestate_servant(self)
        startboss_state = Stagestate_startboss(self)
        boss_state = Stagestate_boss(self)
        win = Stagestate_win(self)
        fail_state = Stagestate_fail(self)

        self.brain.add_state(nothing_state)
        self.brain.add_state(begin_state)
        self.brain.add_state(servant_state)
        self.brain.add_state(startboss_state)
        self.brain.add_state(boss_state)
        self.brain.add_state(win)
        self.brain.add_state(fail_state)
        self.brain.set_state("begin")

    def begin(self):
        self.stage_begin = True
        #  关卡初始化
        self.bgmap = Bgmap(map=r'maps\333.jpg', statu=None, bitmap=r"maps\333.txt", game_items=self.game_items)
        Mytank_both_point = (167, 500)
        self.mytank = Mytank(self.game_items, self.screen, self.bgmap, both_point=Mytank_both_point, contrlmap=True)

    def servant(self):
        self.both_enemy()
        self.servant_over = self.bgmap.map_over and not len(self.servantgroup)

    def startboss(self):
        # 出场动画
        #self.animation_bothof_boss = Animation_bothof_bossgoddess((160, 20))
        pass

    def boss(self):
        self.bossflowerfairy = Bossflowerfairy(self.game_items, self.bgmap, self.boss_position)
        self.boss_both = True

    def win(self):
        Speak(self.bossflowerfairy.rect.bottomright, "boss_word1.gif")

    def fail(self):
        if self.boss_both:
            Speak(self.mytank.rect.center, "boss_word2.gif")


class Stage2(Stage):
    def __init__(self, screen):
        Stage.__init__(self, screen)
        self.start_image = load_image("stage2_start.gif")
        # 返回给game的关卡状态  None为继续   win，fail 为关卡胜利，失败
        self.statu = None

        self.born_boss_num = 0
        self.boss_position = (180, 450)
        # 小兵打完 才出boss
        self.servant_over = False
        self.boss_both = False

        # 状态机
        self.brain = StateMachine()
        nothing_state = Stagestate_nothing(self)
        begin_state = Stagestate_begin(self)
        servant_state = Stagestate_servant(self)
        startboss_state = Stagestate_startboss(self)
        boss_state = Stagestate_boss(self)
        win = Stagestate_win(self)
        fail_state = Stagestate_fail(self)

        self.brain.add_state(nothing_state)
        self.brain.add_state(begin_state)
        self.brain.add_state(servant_state)
        self.brain.add_state(startboss_state)
        self.brain.add_state(boss_state)
        self.brain.add_state(win)
        self.brain.add_state(fail_state)
        self.brain.set_state("begin")

    def begin(self):
        self.stage_begin = True
        # 关卡初始化
        self.bgmap = Bgmap(map=r'maps\444.jpg', statu=None, bitmap=r"maps\444.txt", game_items=self.game_items)
        Mytank_both_point = (168, 300)
        Mytank(self.game_items, self.screen, self.bgmap, both_point=Mytank_both_point, contrlmap=True)

    def servant(self):
        self.both_enemy()
        self.servant_over = self.bgmap.map_over and not len(self.servantgroup)
        #self.servant_over = True

    def startboss(self):
        # 出场动画
        self.animation_bothof_boss = Animation_bothof_bossbouncer((self.boss_position[0], 320))
        pass

    def boss(self):
        if self.animation_bothof_boss.rect.topleft[1] >= 450:
            self.animation_bothof_boss.killself()
            Bossbouncer(self.game_items, self.bgmap, self.boss_position)
            self.boss_both = True


class Stage5(Stage):
    def __init__(self, screen):
        Stage.__init__(self, screen)
        self.start_image = load_image("stage_start.gif")
        # Ai_tank.containers = self.servantgroup, self.game_items
        # Terrorsmallspider.containers = self.servantgroup, self.game_items
        # Bossspider.containers = self.servantgroup, self.game_items
        # NormalBullet.containers = self.bulletgroup, self.game_items

        # 返回给game的关卡状态  None为继续   win，fail 为关卡胜利，失败
        self.statu = None
        # 关卡初始化
        self.boss_position = (160, 30)
        # 小兵打完 才出boss
        self.servant_over = False
        self.boss_both = False

        # 状态机
        self.brain = StateMachine()
        nothing_state = Stagestate_nothing(self)
        begin_state = Stagestate_begin(self)
        servant_state = Stagestate_servant(self)
        startboss_state = Stagestate_startboss(self)
        boss_state = Stagestate_boss(self)
        win = Stagestate_win(self)
        fail_state = Stagestate_fail(self)

        self.brain.add_state(nothing_state)
        self.brain.add_state(begin_state)
        self.brain.add_state(servant_state)
        self.brain.add_state(startboss_state)
        self.brain.add_state(boss_state)
        self.brain.add_state(win)
        self.brain.add_state(fail_state)
        self.brain.set_state("begin")











