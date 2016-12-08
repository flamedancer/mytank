# -*- coding: utf-8 -*-
#
# map.py
#
# File created by moptan  
"""
Tool for building 2d maps

@version: 0.0.5

@author: moptan
"""
"""alter by guochen @20121205"""
import sys, os, pygame
from pgu import gui

from pygame.locals import *
import pygame.rect

try:
    import Tkinter as tk
    import tkFileDialog
except:
    try:
        from tkinter import ttk
        import tkinter
    except:
        print ("Failed to import Tkinter")

import pickle
import random

import string

INPUT_HEIGHT = 50


class MainGui(gui.Desktop):
    menuArea = None
    # The game engine
    engine = None

    def __init__(this, disp):
        gui.Desktop.__init__(this)

        # Setup the 'game' area where the action takes place
        # Setup the gui are a  
        this.gameArea = gui.Container(
                                    height=disp.get_height() - INPUT_HEIGHT)
        this.menuArea = gui.Container(
            height=INPUT_HEIGHT)
        this.disp = disp    
        
        this.maintb = gui.Table(height=500)
        
        this.maintb.tr()
        this.maintb.td(this.menuArea)
        this.maintb.tr()
        this.maintb.td(this.gameArea)
        this.setup_menu()

        this.init(this.maintb, this.disp)

    def setup_menu(this):
        td_style = {'padding_right': 10}
        tb = gui.Table(vpadding=5, hpadding=5)
        tb.tr()
        tb.td( gui.Label(u'单元格行宽') , style=td_style )
        btn1 = gui.Input(size=20)

        tb.td(btn1, style=td_style)
        tb.td( gui.Label(u'单元格列宽') , style=td_style )
        btn = gui.Input("Pause/resume clock", size=20)
        tb.td(btn, style=td_style)
        tb.tr()
        this.menuArea.add(tb, 0, 0)
        

    def open(this, dlg, pos=None):
        # Gray out the game area before showing the popup
        rect = this.gameArea.get_abs_rect()
        dark = pygame.Surface(rect.size).convert_alpha()
        dark.fill((0,0,0,150))
        pygame.display.get_surface().blit(dark, rect)
        # Save whatever has been rendered to the 'game area' so we can
        # render it as a static image while the dialog is open.
        this.gameArea.save_background()
        # Pause the gameplay while the dialog is visible
        running = not(this.engine.clock.paused)
        this.engine.pause()
        gui.Desktop.open(this, dlg, pos)
        while (dlg.is_open()):
            for ev in pygame.event.get():
                this.event(ev)
            rects = this.update()
            if (rects):
                pygame.display.update(rects)
        if (running):
            # Resume gameplay
            this.engine.resume()

    def get_render_area(this):
        return this.gameArea.get_abs_rect()


class map_maker():
    
    def __init__(self):
        pygame.init()
        
        self.window = pygame.display.set_mode((800, 600), RESIZABLE)
        pygame.display.set_caption('Map Maker - v0.5.1')
        self.screen = pygame.display.get_surface()
        #self.screen = pygame.Surface((self.window.get_width(), self.window.get_height() - INPUT_HEIGHT))
        print self.screen
        self.listArray = []
        self.boundArray = []
        
        self.rect_x = 32
        self.rect_y = 32
        
        self.paintset_movex = 0
        self.paintset_movey = 0
        
        self.tileset_movex = 0
        self.tileset_movey = 0
        
        self.counter = 0
        self.cut_surface = None
        
        try:
            tk_root = tk.Tk()
        except:
            try:
                tk_root = tkinter.TK()
            except:
                pass
        tk_root.withdraw()
        
        #self.preGame()
        
        self.ctrl_pressed = False
        self.alt_pressed = False
        
        self.surface_setup()
        self.tileset_set = pygame.image.load("town1.png")

        self.app = MainGui(self.window).menuArea

        self.game()
        
        
    #***********************************#
    #        Functions - Setup          #
    #***********************************#
    
    def surface_setup(self):
        surfset_height = ((self.window.get_height() - self.rect_y) // self.rect_y) * self.rect_y
        
        self.tileset_surf = pygame.Surface(((self.rect_x*8), surfset_height))
        self.tileset_surf.fill((255,255,255))
        self.tileset_grid = self.gridsurface_setup(self.tileset_surf)
        
        self.center_distance_width = self.tileset_surf.get_width() + (self.rect_x*2)
        self.paintset_width = ((self.window.get_width() - self.tileset_surf.get_width() - self.rect_x*2) // self.rect_x) * self.rect_x
        
        self.paintset_surf = pygame.Surface((self.paintset_width, surfset_height))
        self.paintset_surf.fill((255,255,255))
        self.paintset_grid = self.gridsurface_setup(self.paintset_surf)
            
    def gridsurface_setup(self, surface):
        temp = surface.copy()
        temp.set_colorkey((255,255,255))
        left = 0
        top = 0
        x = self.rect_x
        y = self.rect_y
        while top < temp.get_height():
            while left < temp.get_width():
                pygame.draw.rect(temp, (140,140,140), pygame.Rect(left, top, x, y), 1)
                left = left + x
            left = 0
            top = top + y
            
        return temp
        
            
    #***********************************#
    #        Functions - Save/Load      #
    #***********************************#
    
    def save_paint(self):
        filename = tkFileDialog.asksaveasfilename(defaultextension='.mpy', filetypes=[('supported', ('*.mpy', '*.png', '*.jpg', '*.bmp')), ('map files', '*.mpy'),('tileset', ('*.png', '*.jpg', '*.bmp'))])
        if filename.endswith(".mpy"):
            try:
                pickle_open = open(filename, 'wb')
            except:
                print ("not supported")
                return
            pickle.dump(51, pickle_open)
            pickle.dump(self.boundArray, pickle_open)
            for tiles in self.listArray:
                temp = tiles.toString()
                pickle.dump(temp, pickle_open)
            pickle_open.close()
        elif filename.endswith(".png") or filename.endswith(".jpg") or filename.endswith(".bmp"):
            self.save(filename)
        
    def load_paint(self):
        filename = tkFileDialog.askopenfilename(defaultextension='.mpy', filetypes=[('supported', ('*.mpy', '*.png', '*.jpg', '*.bmp')), ('map files', '*.mpy'), ('tilesets', ('*.png', '*.jpg', '*.bmp'))])
        if filename.endswith(".mpy"):
            try:
                pickle_open = open(filename, 'rb')
            except:
                print ("not supported")
                return
            self.listArray = []
            self.paintset_movex = 0
            self.paintset_movey = 0
            self.boundArray = []
            check = pickle.load(pickle_open)
            if isinstance(check, int):
                self.boundArray = pickle.load(pickle_open)
                temp = pickle.load(pickle_open)
            elif len(check) > 0 and len(check[0]) == 2:
                temp = check
            while 1:
                self.listArray.append(local_tile(temp[0], temp[1], None, temp[2]))
                try:
                    temp = pickle.load(pickle_open)
                except:
                    break
            pickle_open.close()
        elif filename.endswith(".png") or filename.endswith(".jpg") or filename.endswith(".bmp"):
            self.tileset_movex = 0
            self.tileset_movey = 0
            self.tileset_set = pygame.image.load(filename)
    
    def save(self, filename):
        save_width_max = 0
        save_height_max = 0
        save_width_min = 9999999999
        save_height_min = 9999999999
        
        for tiles in self.listArray:
            if tiles.get_X() > save_width_max:
                save_width_max = tiles.get_X()
            if tiles.get_X() < save_width_min:
                save_width_min = tiles.get_X()
                
            if tiles.get_Y() > save_height_max:
                save_height_max = tiles.get_Y()
            if tiles.get_Y() < save_height_min:
                save_height_min = tiles.get_Y()
        
        save_width_max = save_width_max + self.rect_x - save_width_min
        save_height_max = save_height_max + self.rect_y - save_height_min
        
        save_surface = pygame.Surface((save_width_max, save_height_max))
        
        for tiles in self.listArray:
            for clips in tiles.get_Surface():
                save_surface.blit(clips, (tiles.get_X() - save_width_min, tiles.get_Y() - save_height_min))
            
        pygame.image.save(save_surface, filename)
    
    #***********************************#
    #        Functions - Events\Other   #
    #***********************************#
    
    def input(self, events):
        for event in events:
            if event.type == KEYUP and event.key == K_ESCAPE or event.type == QUIT:
                sys.exit(0)
            else:
                pass
                #print (str(event))
            
            if event.type == VIDEORESIZE:
                width = event.w
                height = event.h
                if width < self.rect_x*8:
                    width = self.rect_x*8
                if height < self.rect_y*8:
                    height = self.rect_y*8
                
                self.window = pygame.display.set_mode((width, height), RESIZABLE)
                self.screen = pygame.display.get_surface()
                self.surface_setup()
            
            if event.type == MOUSEBUTTONDOWN:
                mouseX, mouseY = self.mouse_pos()
                if mouseY > INPUT_HEIGHT: # 判断 鼠标在图片编辑框里
                    if self.alt_pressed == True:
                        self.bound_drawer()
                    else:
                        self.mouse_listener()
                else:
                    self.app.loop()
            
            if event.type == KEYDOWN:
                if event.key == K_LCTRL or event.key == K_RCTRL:
                    self.ctrl_pressed = True
                if self.ctrl_pressed:
                    if event.key == K_s and len(self.listArray) > 0:
                        self.save_paint()
                        return
                    if event.key == K_l:
                        self.load_paint()
                        return
                if event.key == K_LALT:
                    self.alt_pressed = True
            
            if event.type == KEYUP:
                if event.key == K_LCTRL or event.key == K_RCTRL:
                    self.ctrl_pressed = False
                if event.key == K_LALT:
                    self.alt_pressed = False

            if event.type == KEYDOWN:
            
                if event.key == K_w:
                    self.tileset_movey = self.tileset_movey - self.rect_y
                elif event.key == K_s:
                    self.tileset_movey = self.tileset_movey + self.rect_y
                elif event.key == K_a:
                    self.tileset_movex = self.tileset_movex - self.rect_x
                elif event.key == K_d:
                    self.tileset_movex = self.tileset_movex + self.rect_x
                
                if event.key == K_UP:
                    self.paintset_movey = self.paintset_movey - self.rect_y
                elif event.key == K_DOWN:
                    self.paintset_movey = self.paintset_movey + self.rect_y
                elif event.key == K_LEFT:
                    self.paintset_movex = self.paintset_movex - self.rect_x
                elif event.key == K_RIGHT:
                    self.paintset_movex = self.paintset_movex + self.rect_x
                
                self.counter = self.counter - event.dict['key']
                if self.counter < 0:
                    self.counter = 0
    
    def mouse_pos(self):
        """
        Grabs the current X and Y position of the mouse
        """
        mouseX, mouseY = pygame.mouse.get_pos()
        print "1",mouseX, mouseY
        return mouseX, mouseY
    
    def calc_mouse_pos(self):
        """
        Calculates the X and Y position for painting
        """
        mouseX, mouseY = self.mouse_pos()
        absolute_mouseY = mouseY - INPUT_HEIGHT
        return ((mouseX // self.rect_x) * self.rect_x), ((absolute_mouseY // self.rect_y) * self.rect_y)
        
    def bound_drawer(self):
        pygame.mouse.get_rel()
        pygame.mouse.get_rel()
        left, top = self.mouse_pos()
        left = left - self.center_distance_width
        movex = 0
        movey = 0
        first_timer = True
        while pygame.mouse.get_pressed()[0] == True:
            self.draw()
            pygame.event.poll()
            
            mouseX, mouseY = self.mouse_pos()
            paintX, paintY = pygame.mouse.get_rel()
            print "3", mouseY , self.paintset_surf.get_height() + INPUT_HEIGHT
            if mouseX > self.center_distance_width and mouseY < self.paintset_surf.get_height() + INPUT_HEIGHT:
                if len(self.boundArray) > 0 and first_timer == False:
                    self.boundArray = self.boundArray[0:-1]
                movex = movex + paintX
                movey = movey + paintY
                absolutetop = top - INPUT_HEIGHT
                temp_rect = pygame.Rect(left, absolutetop, movex, movey)
                self.boundArray.append(temp_rect)
                first_timer = False
        
        temp = []
        if pygame.mouse.get_pressed()[2] == True:
            mouseX, mouseY = self.mouse_pos()
            if mouseX > self.center_distance_width and mouseY < self.paintset_surf.get_height() + INPUT_HEIGHT:
                mouseX = mouseX - self.center_distance_width
                mouseY = mouseY - INPUT_HEIGHT
                for rect in self.boundArray:
                    if rect.collidepoint(mouseX, mouseY) == True:
                        temp.append(rect)
                
                if len(temp) > 1:
                    save_left_min = 999999999
                    save_top_min = 999999999
                    save_width_min = 999999999
                    save_height_min = 999999999
        
                    for rect in temp:
                        if rect.left - mouseX < save_left_min:
                            save_left_min = rect.left
                        if rect.top - mouseY < save_top_min:
                            save_top_min = rect.top
                        if rect.width - mouseX < save_width_min:
                            save_width_min = rect.width
                        if rect.height - mouseY < save_height_min:
                            save_height_min = rect.height
                    
                    self.boundArray.remove(pygame.Rect(save_left_min, save_top_min, save_width_min, save_height_min))
                    
                elif len(temp) == 1:
                    self.boundArray.remove(temp[0])
                
                
    def mouse_listener(self):
        fail_Safe = random.random()
        mouseX, mouseY = self.mouse_pos()
        paintX, paintY = self.calc_mouse_pos()
        if pygame.mouse.get_pressed()[0] == True:
            if mouseX < self.tileset_surf.get_width() and mouseY < self.tileset_surf.get_height() - INPUT_HEIGHT:
                self.cut_surface = self.tileset_surf.subsurface(pygame.Rect(paintX, paintY, self.rect_x, self.rect_y)).copy()
        
        while pygame.mouse.get_pressed()[0] == True or pygame.mouse.get_pressed()[2] == True:
            pygame.event.poll()
            mouseX, mouseY = self.mouse_pos()
            paintX, paintY = self.calc_mouse_pos()
            paintX = paintX - self.center_distance_width
            if mouseX > self.center_distance_width:
                if pygame.mouse.get_pressed()[0] and self.cut_surface != None:
                    found = False
                    for clips in self.listArray:
                        if clips.get_X() + self.paintset_movex == paintX and clips.get_Y() + self.paintset_movey == paintY:
                            found = True
                            clips.add_elevation(self.cut_surface)
                    if found == False:
                        self.listArray.append(local_tile((paintX - self.paintset_movex, paintY - self.paintset_movey), self.cut_surface.get_size(), self.cut_surface, None))
                elif pygame.mouse.get_pressed()[2] == True:
                    if mouseX > self.center_distance_width:
                        for clips in self.listArray:
                            if clips.get_X() + self.paintset_movex == paintX and clips.get_Y() + self.paintset_movey == paintY:
                                if clips.remove_elevation(fail_Safe) == False:
                                    self.listArray.remove(clips)
                                break
                elif pygame.mouse.get_pressed()[1] == True:
                    pass
            self.draw()
        
        
    #***********************************#
    #        Functions - Loops/Other    #
    #***********************************#
        
    def preGame(self):
        font = pygame.font.SysFont(*('arial', 20))
        preGame_getX_text = "Input the width of the cut square: "
        preGame_getY_text = "Input the height of the cut square: "
        position = 1
        current_string = []
        keyin = None
        keypress = False
        while True:
            self.screen.fill((255,255,255))
            
            event = pygame.event.poll()
            
            if event.type == KEYUP and event.key == K_ESCAPE or event.type == QUIT:
                sys.exit(0)
            
            if event.type == KEYDOWN:
                keyin = event.key
            else:
                keyin = None
                
            if keyin == K_BACKSPACE:
                current_string = current_string[0:-1]
            elif keyin == K_RETURN:
                if len(current_string) == 0:
                    pass
                elif position == 1:
                    self.rect_x = int(string.join(current_string,""))
                    if self.rect_x != 0:
                        position = 2
                        current_string = []
                elif position == 2:
                    self.rect_y = int(string.join(current_string,""))
                    if self.rect_y != 0:
                        position = 3
                        current_string = []
            elif 48 <= keyin <= 57:
                current_string.append(chr(keyin))
                
            if position == 1:
                text_render = font.render(preGame_getX_text + string.join(current_string,""), True, ((255,255,255)))
                self.screen.blit(text_render, (50, 50))
            elif position == 2:
                text_render = font.render(preGame_getY_text + string.join(current_string,""), True, ((255,255,255)))
                self.screen.blit(text_render, (50, 50))
            elif position == 3:
                break
            pygame.display.flip()
    
    def game(self):
        self.app.loop()
        pygame.display.flip()
        while True:
            self.draw()
            self.input(pygame.event.get())
            pass
        #self.app.update()
        #pygame.display.flip()
        #done = False
        #while not done:
        #    # Process events
        #    for ev in pygame.event.get():
        #        if (ev.type == pygame.QUIT or 
        #            ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE):
        #            done = True
    
    def draw(self):
       
        self.paintset_surf.fill((255,255,255))
        self.tileset_surf.fill((255,255,255))
        
        for slices in self.listArray:
            for elevated in slices.get_Surface():
                self.paintset_surf.blit(elevated, (slices.get_X() + self.paintset_movex, slices.get_Y() + self.paintset_movey))
        
        if self.tileset_set != None:
            self.tileset_surf.blit(self.tileset_set, (0 + self.tileset_movex,0 + self.tileset_movey))
            
        self.paintset_surf.blit(self.paintset_grid, (0,0))
        
        for rect in self.boundArray:
            pygame.draw.rect(self.paintset_surf, (255,0,0), rect, 1)
        self.app.loop()
        self.screen.blit(self.paintset_surf, (self.center_distance_width, INPUT_HEIGHT))
        
        self.screen.blit(self.tileset_surf, (0, INPUT_HEIGHT))
        self.screen.blit(self.tileset_grid, (0, INPUT_HEIGHT))
        
        #self.screen.blit(self.paintset_grid, (self.center_distance_width, 0))

        
        pygame.display.flip()
        pygame.time.wait(10)

class local_tile():

    def __init__(self, pos, size, surface = None, str = None):
        self.xPos = pos[0]
        self.yPos = pos[1]
        self.xSize = size[0]
        self.ySize = size[1]
        self.elevated_surface = []
        if str != None:
            for x in str:
                temp_surf = pygame.image.fromstring(x,(self.xSize,self.ySize), "RGBA")
                temp_surf.set_colorkey((255,255,255))
                self.elevated_surface.append(temp_surf)
        elif surface != None:
            surface.set_colorkey((255,255,255))
            self.elevated_surface.append(surface)
            
        self.fail_Safe = 0
    
    def toString(self):
        temp_str = []
        for clips in self.elevated_surface:
            temp_str.append(pygame.image.tostring(clips, "RGBA"))
        return (self.xPos, self.yPos), (self.xSize, self.ySize), temp_str
    
    def get_Surface(self):
        return self.elevated_surface
        
    def get_X(self):
        return self.xPos
        
    def get_Y(self):
        return self.yPos
        
    def add_elevation(self, surface):
        surface.set_colorkey((255,255,255))
        for clips in self.elevated_surface:
            if clips == surface:
                return
        
        if len(self.elevated_surface) > 2:
            return
        else:
            self.elevated_surface.append(surface)
            
    def remove_elevation(self, failSafe):
        if failSafe == self.fail_Safe:
            return True
        self.fail_Safe = failSafe
        if len(self.elevated_surface) < 2:
            return False
        else:
            self.elevated_surface = self.elevated_surface[0:-1]
            
        return True
        
if __name__ == '__main__':
    map_maker()