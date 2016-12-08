#encoding=utf-8
"""渲染 背景 面板 地图  特效 动画等"""
import pygame
from pygame.locals import *

from start import *
from libs import *


def healthpannel(screen, rate):
    """hp 面板"""
    if rate <= 0.3:
        color = (255, 0, 0)
    elif rate <= 0.7:
        color = (255, 255, 0)
    else:
        color = (0, 255, 0)
    heathwidth = 380 * rate
    screen.fill(color, (4, 2 + SCREEN_HEIGHT + BOUNDARY_LINE_HEIGHT, heathwidth, 20))
    screen.fill((125, 100, 100), (2 + heathwidth, 2 + SCREEN_HEIGHT + BOUNDARY_LINE_HEIGHT, 600 - heathwidth - 2, 20))


class Bgmap(pygame.sprite.Sprite):
    """背景图片 和位图"""
    speed = 6

    def __init__(self, map=None, statu=None, bitmap=False, game_items=None):
        self.background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)).convert()
        self.statu = statu
        if map:
            self.map = load_image(map)
        else:
            self.map = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)).convert()
            self.map.fill((0, 0, 0))
        self.bitmap = bitmap
        self.game_background = pygame.Surface((SCREEN_WIDTH, self.map.get_height()))
        self.game_background = self.game_background.convert()
        for x in range(0, SCREEN_WIDTH, self.map.get_width()):
            self.game_background.blit(self.map, (x, 0))

        self.image = self.background
        self.clip_rect = Rect(0, self.map.get_height() - SCREEN_HEIGHT,
                    SCREEN_WIDTH, SCREEN_HEIGHT)
        self.image.blit(self.game_background, (0, 0), self.clip_rect)

        if self.bitmap:
            self.read_bitmap()
            # 记录视图所占对应位图行数
            self.screen_bit_row = SCREEN_HEIGHT // self.bitmap_point_height
        if game_items != None:
            self.game_items = game_items
            # 记录当前视图距离大地图顶端的位移
            self.map_distance = self.map.get_height() - SCREEN_HEIGHT
            # 记录地图是否走完
            self.map_over = False if self.map_distance > 0 else True

    def update(self, *args):
        if self.statu == "move":
            self.clip_rect.move_ip(0, -self.speed)
            self.image.blit(self.game_background, (0, 0), self.clip_rect)
        return self.image.copy()

    def move_by_player(self, speed):
        self.clip_rect.move_ip(0, -speed)
        if not self.map_over:
            self.map_distance = self.map_distance - speed
            if self.map_distance < 0:
                self.map_distance = 0
                self.map_over = True
            else:
                self.image.blit(self.game_background, (0, 0), self.clip_rect)
                for item in self.game_items:
                    item.rect.move_ip(0, speed)

    def read_bitmap(self):
        # 全大位图
        self.bitmap = load_bitmap(self.bitmap)

        self.bitmap_point_width = self.map.get_width() / len(self.bitmap[0])
        self.bitmap_point_height = self.map.get_height() / len(self.bitmap)

        # 地图大小不合理 将影响位图的准确性
        # print self.map.get_height(), len(self.bitmap), self.bitmap_point_height

    def get_enemy(self):
        # 返回敌人代码 和 纵坐标
        self.now_bitmap_rowtop = self.map_distance // self.bitmap_point_height
        enemy_left_point_list = []
        for left_bit_point in range(0, len(self.bitmap[0])):
            if self.bitmap[self.now_bitmap_rowtop][left_bit_point] not in [0, 1]:
                enemy_left_point_list.append((self.bitmap[self.now_bitmap_rowtop][left_bit_point], left_bit_point * self.bitmap_point_width))
                self.bitmap[self.now_bitmap_rowtop][left_bit_point] = 0
        return enemy_left_point_list

    def map_passive(self, rect):
        if self.bitmap:
            top, left, bottom, right = rect.top, rect.left, rect.bottom - 1, rect.right - 1
            point_x_range = left / self.bitmap_point_width, right / self.bitmap_point_width + 1
            point_y_range = (top + self.map_distance) // self.bitmap_point_height, (self.map_distance + bottom) // self.bitmap_point_height + 1
            for point_x in range(*point_x_range):
                for point_y in range(*point_y_range):
                    # print point_x, point_y
                    try:
                        if self.bitmap[point_y][point_x] != 0:
                            return False
                    except Exception, e:
                        # print left, self.bitmap_point_width, right, self.bitmap_point_width
                        # print top , self.bitmap_point_height, bottom , self.bitmap_point_height
                        # print point_x, point_y, point_x_range, point_y_range
                        # raise e
                        return False
        return True


class Render:
    # 渲染 特效父类
    def __init__(self):
        pass


class Explod(Render, pygame.sprite.Sprite):
    """爆炸 渲染"""
    def __init__(self, expold_imags, center_pos, expold_time=None, replaytime=1):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.name = "explod"
        self.expold_imags = expold_imags
        self.pos = center_pos
        self.expold_time = expold_time or 4
        self.image = self.expold_imags[0]
        self.rect = self.image.get_rect(center=self.pos)
        self.expold_steps = len(self.expold_imags)
        self.now_expold_step = 0
        self.counting_down = self.expold_time
        self.replaytime = replaytime
        self.nowreplaytime = 1

    def do_actions(self):
        if self.now_expold_step < self.expold_steps:
            self.image = self.expold_imags[self.now_expold_step]
            self.rect = self.image.get_rect(center=self.pos)
        elif self.nowreplaytime < self.replaytime:
            self.now_expold_step = 0
            self.counting_down = self.expold_time
            self.nowreplaytime = self.nowreplaytime + 1
        else:
            self.kill()

    def update(self, *args):
        if self.counting_down == 0:
            self.do_actions()
            self.now_expold_step = self.now_expold_step + 1
            self.counting_down = self.expold_time
        else:
            self.counting_down = self.counting_down - 1


class Frozen(Render, pygame.sprite.Sprite):
    # 冰冻状态特效
    def __init__(self, target):
        pygame.sprite.Sprite.__init__(self, self.containers)

        self.name = "frozen"
        self.image = load_image('frozen.gif')
        self.rect = self.image.get_rect(center=target.rect.center)

        self.target = target

        self.keeptime = time_to_frams(2)    # 冰冻时长
        self.now_time = self.keeptime

    def killself(self):
        self.kill()

    def update(self, *args):
        self.now_time = self.now_time - 1
        judge = (self.now_time == 0)
        self.target.movable = judge
        self.target.skillable = judge
        self.target.shootable = judge
        if judge:
            self.killself()


class Animation(pygame.sprite.Sprite):
    """动画 渲染"""
    def __init__(self, animation_imags, center_pos, animation_time=None):
        pygame.sprite.Sprite.__init__(self, self.containers)
        pass

    def do_actions(self):
        pass

    def update(self, *args):
        pass


class Animation_bothof_bossspider(Render, pygame.sprite.Sprite):
    """大蜘蛛出场动画 渲染"""
    def __init__(self, topleft):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.name = "bothof_bossspider"
        self.image = load_image("bossspider.gif")
        self.rect = self.image.get_rect(topleft=topleft)

    def killself(self):
        self.kill()

    def update(self, *args):
        self.rect = self.rect.move(0, 1)


class Animation_bothof_bossgoddess(Render, pygame.sprite.Sprite):
    """女神出场动画 渲染"""
    def __init__(self, topleft):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.name = "bothof_bossgoddess"
        self.images = loadimage_to_slices("bossgoddess.gif", 18)
        self.imageindex = 0
        self.image = self.images[self.imageindex]
        self.rect = self.image.get_rect(topleft=topleft)

        self.keeptime = 5  # 控制每幅图的静止帧数
        self.nowkeeptime = self.keeptime

    def killself(self):
        self.kill()

    def update(self, *args):
        if self.nowkeeptime == 0:
            self.nowkeeptime = self.keeptime
            if self.imageindex < len(self.images) - 1:
                self.imageindex = self.imageindex + 1
                self.image = self.images[self.imageindex]
            else:
                self.imageindex = 0
                #self.killself()
        else:
            self.nowkeeptime = self.nowkeeptime - 1


class Animation_bothof_bossbouncer(Render, pygame.sprite.Sprite):
    """弹球boss出场动画 渲染"""
    def __init__(self, topleft):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.name = "bothof_bossspider"
        self.image = load_image("bouncebullet.gif")
        self.rect = self.image.get_rect(topleft=topleft)

    def killself(self):
        self.kill()

    def update(self, *args):
        self.rect = self.rect.move(0, 1)


class Speak(Render, pygame.sprite.Sprite):
    """话语 渲染"""
    def __init__(self, topleft, word_image_path):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.name = "word"
        self.image = load_image(word_image_path)
        self.rect = self.image.get_rect(topleft=topleft)

    def killself(self):
        self.kill()

    def update(self, *args):
        self.rect = self.rect.move(0, -1)
        if not SCREENRECT.colliderect(self.rect):
            self.killself()
