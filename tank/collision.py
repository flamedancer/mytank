#encoding=utf-8
"""碰撞处理"""
from start import *


COLLISONS_JUDGE = Readconf("cof_of_collsion.txt")


def collision(mold, game_items=None, rect=None):
    if not game_items:
        game_items = mold.game_items
    if not rect:
        rect = mold.new_rect
    for item in game_items:
        if mold != item and rect.colliderect(item.rect):
            conf = COLLISONS_JUDGE[mold.name].get(item.name)
            if conf:
                mold.wounded(conf[1])
                item.wounded(conf[2])
                if len(conf) > 3:
                    mold.more_effect(item)
                if conf[0]:     # 如果conf[0]是 1  表示不通过
                    return False
    return True

