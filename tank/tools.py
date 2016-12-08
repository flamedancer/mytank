#encoding=utf-8
"""一些文件处理工具"""
import os
#import json
import ast

import pygame
from pygame.locals import *


def load_image(name):
    """ Load image and return image object"""
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
        if image.get_alpha is None:
            image = image.convert()
        else:
            image = image.convert_alpha()

    except pygame.error, SystemExits:
        print 'Cannot load image:', fullname
        raise SystemExits

    return image


def load_images(*files):
    imgs = []
    for file in files:
        imgs.append(load_image(file))
    return imgs


def load_images_bykey(keyfiles):
    keyimages = {}
    for key in keyfiles:
        keyimages[key] = load_image(keyfiles[key]) if keyfiles[key] else None
    return keyimages


def load_bitmap(name):
    fullname = os.path.join('data', name)
    bitmap_file = open(fullname)
    bitmap = []
    for line in bitmap_file.readlines():
        line = line.strip()
        line_list = [int(item) for item in line.split(" ")]
        bitmap.append(line_list)
    bitmap_file.close()
    return bitmap


def Readconf(name):
    collisonsfile = open(os.path.join('data', 'conf', name))
    conf_str = "".join([line.strip() for line in collisonsfile.readlines()])
    
    #config = json.load(collisonsfile)   # 无法加载以序列为主键的字典
    try:
    
        config = ast.literal_eval(conf_str)
    except Exception, e:
        print conf_str
        raise e
    return config


def loadimage_to_slices(name, slicenum, colorkey=(0, 4, 0)):
    # 加载一个长图片 并且切成若干部分
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
        #image.set_colorkey(colorkey)
        if image.get_alpha is None:
            image = image.convert()
        else:
            image = image.convert_alpha()
    except pygame.error, SystemExits:
        print 'Cannot load image:', fullname
        raise SystemExits

    imageheight = image.get_height()
    slicewidth = image.get_width()
    sliceheight = imageheight // slicenum

    images = []
    now_top = 0
    while now_top < imageheight:
        thisimage = pygame.Surface((slicewidth, sliceheight))
        thisimage.fill(colorkey)
        thisimage.set_colorkey(colorkey)
        thisimage.blit(image, (0, 0), Rect(0, now_top, slicewidth, sliceheight))

        images.append(thisimage)
        now_top = now_top + sliceheight
    return images



    