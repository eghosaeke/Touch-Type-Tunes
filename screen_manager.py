import sys
import os
sys.path.append('..')
from common.core import *
from common.audio import *
from common.mixer import *
from common.wavegen import *
from common.wavesrc import *
from common.gfxutil import *
from common.kivyparticle import ParticleSystem

from kivy.app import App
from kivy.graphics.instructions import InstructionGroup
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.graphics import PushMatrix, PopMatrix, Translate, Scale, Rotate, ChangeState
from kivy.graphics.transformation import Matrix
from kivy.clock import Clock as kivyClock
from kivy.core.text import Label
from kivy.core.text.text_layout import layout_text
from kivy.core.text import Label as CoreLabel
from kivy.core.text.markup import MarkupLabel
from kivy.core.text import LabelBase
from kivy.utils import platform
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition, SlideTransition

import numpy as np
import bisect
import string
import matplotlib.colors as colors
from colorsys import hsv_to_rgb
from collections import deque, OrderedDict
import re
import textwrap
from customlabel import BasicLabel, CustomLabel
from random import random, randint,choice, uniform
from copy import deepcopy
from skeleton_code import AudioController, SongData, LyricsWord, LyricsPhrase, ImprovPhrase, ImprovDisplay, BeatMatchDisplay, Player, wrap_text

class ScoreLabel(InstructionGroup):
    def __init__(self):
        super(ScoreLabel, self).__init__()
        if platform == "macosx":        
            self.font_name= "Comic Sans MS"
        elif platform == "win":
            self.font_name = "comic"
        else:
            self.font_name = ""
        self.time=0
        self.objects=AnimGroup()
        self.start_size =30
        self.end_size = 50
        self.basic_label= BasicLabel("Score",tpos=(Window.width*0.8, Window.height*.6),font_size=self.start_size,font_name=self.font_name)
        self.objects.add(self.basic_label)
        self.add(self.objects)
        self.size_anim = KFAnim((0, self.start_size),(.25, self.end_size),(.5, self.start_size))

    
    def on_update(self,dt):
        new_size = self.size_anim.eval(self.time)
        self.basic_label.font_size=new_size
        self.time += dt
        if not self.size_anim.is_active(self.time):
            self.time = 0

        return True


class GameManager(ScreenManager):
    def __init__(self,**kwargs):
        super(GameManager,self).__init__()
        if not kwargs.has_key('transition'):
            self.transition = SlideTransition   

    def update_bg(self,size,pos):
        for screen in self.screens:
            screen.update_bg(size,pos)


class PauseScreen(Screen):
    def __init__(self,**kwargs):
        super(PauseScreen,self).__init__(**kwargs)
        self.color = Color(0,0,0,0.75)
        self.pos = (0,0)
        if kwargs.has_key('size'):
            self.size = kwargs['size']
        else:
            self.size = (Window.width,Window.height)
        self.bg_rect = Rectangle(pos=self.pos,size=self.size,source="studio_booth.jpg")

        self.label = BasicLabel("Title Screen",tpos=(Window.width*0.1,Window.height*0.85),font_size=40,halign='center')
        self.alpha_rect = Rectangle(pos=self.pos,size=self.size)
        self.canvas.add(PushMatrix())
        self.canvas.add(self.bg_rect)
        self.canvas.add(self.color)
        self.canvas.add(self.alpha_rect)
        self.canvas.add(PopMatrix())
        self.text_color = Color(1,1,1,0.85)
        self.canvas.add(self.text_color)
        self.canvas.add(self.label)
        self.paused_text = "Studio session paused\nWhen you're ready\nPress 'shift enter' to continue the game"
        self.label.text = self.paused_text
        self.label.tpos = (.5*(self.size[0]-self.label.size[0]),.75*self.size[1])

    def update_bg(self,size,pos):
        width=float(size[0])
        height=float(size[1])
        self.size = size
        self.pos = pos
        self.bg_rect.size = size
        self.alpha_rect.size = size
        if platform == 'macosx':
            self.label.tpos = (.5*(width-self.label.size[0]),.75*height)


class TitleScreen(Screen):
    def __init__(self,**kwargs):
        super(TitleScreen,self).__init__(**kwargs)
        self.color = Color(0,0,0,0.75)
        self.pos = (0,0)
        if kwargs.has_key('size'):
            self.size = kwargs['size']
        else:
            self.size = (Window.width,Window.height)
        self.bg_rect = Rectangle(pos=self.pos,size=self.size,source="studio_booth.jpg")

        self.label = BasicLabel("Title Screen",tpos=(Window.width*0.1,Window.height*0.85),font_size=40,halign='center')
        self.alpha_rect = Rectangle(pos=self.pos,size=self.size)
        self.canvas.add(PushMatrix())
        self.canvas.add(self.bg_rect)
        self.canvas.add(self.color)
        self.canvas.add(self.alpha_rect)
        self.canvas.add(PopMatrix())
        self.text_color = Color(1,1,1,0.85)
        self.canvas.add(self.text_color)
        self.canvas.add(self.label)
        self.title_text = "Welcome to Touch Type Tunes!\n\nWhen the music starts, type the\nthe highlighted letters on the screen.\nPress 'shift enter' to cue the music."
        self.label.text = self.title_text
        self.label.tpos = (.5*(self.size[0]-self.label.size[0]),.75*self.size[1])
    
    def update_bg(self,size,pos):
        width=float(size[0])
        height=float(size[1])
        self.size = size
        self.pos = pos
        self.bg_rect.pos = pos
        self.bg_rect.size = size
        self.alpha_rect.size = size
        if platform == 'macosx':
            self.label.tpos = (.5*(width-self.label.size[0]),.75*height)

class GameScreen(Screen):
    def __init__(self,improv_disp,beat_disp,**kwargs):
        super(GameScreen,self).__init__(**kwargs)
        # with self.canvas.before:
        # ADD BACKGROUND IMAGE TO GAME
        if kwargs.has_key('size'):
            self.size = kwargs['size']
        else:
            self.size = (Window.width,Window.height)


        self.pos = (0,0)
        self.canvas.add(PushMatrix())
        self.bg_img = Rectangle(size=self.size,pos = self.pos,source="mic-booth.jpg")
        self.canvas.add(self.bg_img)
        self.canvas.add(Color(0, 0, 0, 0.3))
        self.sidebar = Rectangle(size = (self.size[0]/2,self.size[1]) ,pos =self.pos)
        self.canvas.add(self.sidebar)
        self.canvas.add(Color(1,1,1,0.8))

        #ADD VARIOUS DISPLAYS TO GAME SCREEN
        self.improv_disp = improv_disp
        self.beat_disp = beat_disp
        self.improv_obj = AnimGroup()
        self.improv_obj.add(self.improv_disp)  
        self.score_label = ScoreLabel()
        self.score_label.basic_label.tpos = [self.size[0]*0.8,self.size[1]*0.8]
        self.improv_disp.tpos =[self.size[0]*.3,self.size[1]*.7]
        self.improv_disp.translate.x = self.size[0]*.85
        self.improv_disp.translate.y = self.size[1]*.2    

        self.score_obj = AnimGroup()   
        self.score_obj.add(self.score_label)
        self.canvas.add(self.beat_disp)
        self.canvas.add(self.improv_obj)
        self.canvas.add(self.score_obj)
        self.canvas.add(PopMatrix())

    def restart(self):
        self.canvas.clear()
        self.pos = (0,0)
        self.canvas.add(PushMatrix())
        self.bg_img = Rectangle(size=self.size,pos = self.pos,source="mic-booth.jpg")
        self.canvas.add(self.bg_img)
        self.canvas.add(Color(0, 0, 0, 0.3))
        self.sidebar = Rectangle(size = (self.size[0]/2,self.size[1]) ,pos =self.pos)
        self.canvas.add(self.sidebar)
        self.canvas.add(Color(1,1,1,0.8))

        #ADD VARIOUS DISPLAYS TO GAME SCREEN
        self.improv_obj = AnimGroup()
        self.improv_disp.restart()
        self.improv_obj.add(self.improv_disp)  
        self.score_label = ScoreLabel()
        self.score_label.basic_label.tpos = [self.size[0]*0.8,self.size[1]*0.8]
        self.improv_disp.tpos =[self.size[0]*.3,self.size[1]*.7]
        self.improv_disp.translate.x = self.size[0]*.85
        self.improv_disp.translate.y = self.size[1]*.2    

        self.score_obj = AnimGroup()   
        self.score_obj.add(self.score_label)
        self.canvas.add(self.beat_disp)
        self.canvas.add(self.improv_obj)
        self.canvas.add(self.score_obj)
        self.canvas.add(PopMatrix())


    def remove_improv_disp(self):
        self.canvas.remove(self.improv_obj)

    def add_improv_disp(self,disp):
        self.improv_disp = disp
        self.improv_obj = AnimGroup()
        self.improv_obj.add(self.improv_disp)
        self.improv_disp.tpos =[self.size[0]*.3,self.size[1]*.7]
        self.improv_disp.translate.x = self.size[0]*.85
        self.improv_disp.translate.y = self.size[1]*.2
        self.improv_obj.add(self.improv_disp)
        self.canvas.add(self.improv_obj)

    def update_bg(self,size,pos):
        width=float(size[0])
        height=float(size[1])
        self.size = size
        self.pos = pos
        self.bg_img.pos = pos
        self.bg_img.size = size
        self.sidebar.size = (width/2,height)
        if platform == 'macosx':
            self.score_label.basic_label.tpos =[width*.8,height*.8]
            self.improv_disp.tpos =[width*.3,height*.7]
            self.improv_disp.translate.x = width*.85
            self.improv_disp.translate.y = height*.2
            self.beat_disp.start_pos = (20,height+10)


class EndScreen(Screen):
    def __init__(self,**kwargs):
        super(EndScreen,self).__init__(**kwargs)
        self.color = Color(0,0,0,0.75)
        self.pos = (0,0)
        if kwargs.has_key('size'):
            self.size = kwargs['size']
        else:
            self.size = (Window.width,Window.height)
        self.bg_rect = Rectangle(pos=self.pos,size=self.size,source="studio_booth.jpg")

        self.label = BasicLabel("Title Screen",tpos=(Window.width*0.1,Window.height*0.85),font_size=40,halign='center')
        self.alpha_rect = Rectangle(pos=self.pos,size=self.size)
        self.canvas.add(PushMatrix())
        self.canvas.add(self.bg_rect)
        self.canvas.add(self.color)
        self.canvas.add(self.alpha_rect)
        self.canvas.add(PopMatrix())
        self.text_color = Color(1,1,1,0.85)
        self.canvas.add(self.text_color)
        self.canvas.add(self.label)
        self.end_text = "Game Over!"
        self.label.text = self.end_text
        self.label.tpos = (.5*(self.size[0]-self.label.size[0]),.75*self.size[1])
    
    def update_bg(self,size,pos):
        width=float(size[0])
        height=float(size[1])
        self.size = size
        self.pos = pos
        self.bg_rect.pos = pos
        self.bg_rect.size = size
        self.alpha_rect.size = size
        if platform == 'macosx':
            self.label.tpos = (.5*(width-self.label.size[0]),.75*height)



class MainWidget(BaseWidget,ScreenManager):
    def __init__(self):
        super(MainWidget,self).__init__()
        self.song = 'Stems/Fetish'
        self.audio_cont = AudioController(self.song,improv_cb=self.improv_cb,gameover_cb=self.gameover_cb)
        self.gem_data = SongData()
        self.gem_data.read_data('Stems/Fetish-selected-finalpresentation-buffers-fixed.txt')
        self.gem_data.get_phrases()
        
        #Improv stuff
        self.loopFilepath = 'Stems/improv/Fetish-improv-loops-better.txt'
        self.markFilepath = 'Stems/improv/Fetish-improv-marks.txt'
        self.markRegionPath = 'Stems/improv/Fetish-improv-marks-regions.txt'
        
        #Loop = (Lyric, startTime, duration)
        #Mark  = Lyric: (startTime, endTime)
        self.loops, self.marks = self.gem_data.read_improv(self.loopFilepath, self.markFilepath)
        self.bgImprovBuffers = make_wave_buffers(self.loopFilepath, self.song + '_inst.wav') 
        self.vocalImprovBuffers = make_wave_buffers(self.markRegionPath, self.song + '_vocals.wav')
        self.marksHit = []
        
        self.improv = False 
        self.improv_disp = ImprovDisplay(self.vocalImprovBuffers,self.audio_cont.play_buf,self.ps_cb)
        self.beat_disp = BeatMatchDisplay(self.gem_data,self.improv_disp.add_improv_word)

        self.particles = deque()

        self.size = (Window.width,Window.height)
        self.game_manager = GameManager(transition=FadeTransition())
        self.title_scrn = TitleScreen(name="title",size=self.size)
        self.game_scrn = GameScreen(improv_disp=self.improv_disp,beat_disp=self.beat_disp,name="game",size=self.size)
        self.pause_scrn = PauseScreen(name="pause",size=self.size)
        self.end_scrn = EndScreen(name="end",size=self.size)
        self.player = Player(self.gem_data,self.beat_disp,self.game_scrn.improv_obj,self.improv_disp,self.audio_cont,self.stop_ps)
        self.transition = FadeTransition()
        self.add_widget(self.title_scrn)
        self.add_widget(self.game_scrn)
        self.add_widget(self.pause_scrn)
        self.add_widget(self.end_scrn)
        
        
        self.bind(pos=self.update_bg)
        self.bind(size=self.update_bg)

        self.caps_on = False
        self.particles_work = False



    def update_bg(self, *args):
        self.title_scrn.update_bg(self.size,self.pos)
        self.game_scrn.update_bg(self.size,self.pos)
        self.pause_scrn.update_bg(self.size,self.pos)
        self.end_scrn.update_bg(self.size,self.pos)
        # self.game_scrn.bg_img.pos = self.pos
        # self.game_scrn.bg_img.size = self.size
        # width=float(self.size[0])
        # height=float(self.size[1])
        # self.game_scrn.sidebar.size=[width/2,height]
        # if platform == "macosx":
        #     ##GAME SCREEN VARIABLES
        #     # self.gstatus.size = (width,height)
        #     # self.gstatus.label.tpos=(.5*(width-self.gstatus.label.size[0]),.75*height)
        #     # self.gstatus.bg_rect.size = self.gstatus.size
        #     # self.gstatus.alpha_rect.size = self.gstatus.size
        #     self.title_scrn.size = self.size
        #     self.game_scrn.size = self.size
        #     self.pause_scrn.size = self.size
        #     self.game_scrn.score_label.basic_label.tpos =[width*.8,height*.8]
        #     # self.improv_disp.tpos =[width*.3,height*.7]
        #     # self.improv_disp.translate.x =width*.85
        #     # self.improv_disp.translate.y =height*.2
        #     # self.beat_disp.start_pos = (20,height+10)
        # elif platform == "win":
        #     self.gstatus.size = (width,height)
        #     self.gstatus.label.tpos=(.5*(width-self.gstatus.label.size[0]),.75*height)
        #     self.gstatus.bg_rect.size = self.gstatus.size
        #     self.gstatus.alpha_rect.size = self.gstatus.size
        #     self.improv_disp.scale.origin = (0,0)
        #     self.score_label.basic_label.tpos =[width*.8,height*.8]
        #     self.improv_disp.tpos =[width*.3,height*.6]
        #     self.improv_disp.translate.x = width*1.25
        #     self.beat_disp.start_pos = (20,height+10)



    def on_key_down(self, keycode, modifiers):
        print 'key-down', keycode, modifiers

        if keycode[1] == 'capslock':
            self.caps_on = not self.caps_on


        if keycode[1] == 'enter':
            if "shift" in modifiers:
                if self.current == 'title':
                    self.current = 'game'
                elif self.current == 'game':
                    self.current = 'pause'
                elif self.current == 'pause':
                    self.current = 'game'
                self.player.toggle_game()
            elif "ctrl" in modifiers:
                self.improv = False
                self.player.improv = False
                self.beat_disp.improv = False
                self.audio_cont.improv = False
                if self.current != 'title':
                    self.current = 'title'
                self.player.restart_game()
                # new_disp = ImprovDisplay(self.vocalImprovBuffers,self.audio_cont.play_buf,self.ps_cb)
                # self.game_scrn.remove_improv_disp()
                # self.game_scrn.add_improv_disp(new_disp)
                # self.player.improv_disp = new_disp
                # self.player.improv_group = self.game_scrn.improv_obj
                self.game_scrn.restart()

        if keycode[1] == 'spacebar':
            self.player.on_button_down(" ")

        letter = lookup(keycode[1], string.ascii_letters, string.ascii_letters)
        if letter != None:
            if self.caps_on or 'shift' in modifiers:
                letter = letter.upper()
            self.player.on_button_down(letter)
            # self.hello.text += letter

            # print "down ", letter , keycode[1]
        
        #Disable punctuation in improv mode:
        if not self.improv:
            spec_char = lookup(keycode[1], string.punctuation, string.punctuation)
            if spec_char != None:
                self.player.on_button_down(spec_char)
#                print "down ", spec_char
#                self.hello.text += spec_char

    def improv_cb(self,end=False):
        if end:
            self.improv_disp = ImprovDisplay(self.vocalImprovBuffers,self.audio_cont.play_buf,self.ps_cb)

            self.improv = False
            self.player.improv = False
            self.beat_disp.improv = False
            self.audio_cont.improv = False
        else:
            self.audio_cont.load_improv([self.bgImprovBuffers["Loop1"],self.bgImprovBuffers["Loop2"],self.bgImprovBuffers["Final"]])
            self.improv_disp.start()
            self.improv = True
            self.player.improv = True
            self.beat_disp.improv = True
            self.audio_cont.improv = True

    def gameover_cb(self):
        
        self.end_scrn.end_text += "\n\nAccuracy: {:.2%}".format(self.player.get_words_hit()/self.beat_disp.get_max_words())
        self.end_scrn.end_text += "\nWords Hit: {}".format(self.player.get_words_hit())
        self.end_scrn.end_text += "\n\nPress 'ctrl enter' to restart the game"
        self.end_scrn.label.text = self.end_scrn.end_text
        self.end_scrn.update_bg((Window.width,Window.height),(0,0))
        self.current = 'end'
        self.end_scrn.end_text = "Game Over!"

    def ps_cb(self,pos,color,duration=1.0):
        """
        Add particle systems to screen on succesful event
        """
        if self.particles_work:
            ps = ParticleSystem('particle/particle.pex')
            ps.emitter_x = pos[0]
            ps.emitter_y = pos[1]
            ps.life_span = 10
            ps.life_span_variance = 0
            # ps.speed = 500
            # color = color
            # rgb_color = hsv_to_rgb(*color)
            ps.start_color = [x for x in color]+[1.0]
            ps.end_color = [x for x in color]+[1.0]
            self.add_widget(ps)
            self.particles.append(ps)
            ps.stop(True)
            ps.start()

            kivyClock.schedule_once(self.stop_ps,duration)
        # ps.stop(True)

    def stop_ps(self,dt):
        if self.particles_work:
            if len(self.particles) > 0:
                ps = self.particles.popleft()
                ps.stop(True)

    def on_update(self):
        if kivyClock.get_fps() > 40:
            self.player.on_update()

            
            # if not self.improv_disp.pre_started:
            #     self.improv_disp._scale = (self.improv_disp._scale[0]+0.001,self.improv_disp._scale[1]+0.001,0)
            #     self.improv_disp._trans = (self.improv_disp._trans[0]-5,self.improv_disp._trans[1]+0.1)
            #Optimization for paused
#            self.player.game_paused = False
#            self.beat_disp.game_paused = False
#        elif kivyClock.get_fps() <= 40:
#            self.player.game_paused = True
#            self.beat_disp.game_paused = True
        # self.info.text = str(Window.mouse_pos)
        # self.info.text += '\nload:%.2f' % self.audio_cont.audio.get_cpu_load()
        # self.info.text += '\nfps:%d' % kivyClock.get_fps()
        # self.info.text += '\nobjects:%d' % len(self.beat_disp.objects.objects)
        # if not self.player.game_started:
        #     self.gstatus_obj.on_update()
            self.game_scrn.improv_obj.on_update()
            self.game_scrn.score_label.basic_label.text = "Score"
            self.game_scrn.score_label.basic_label.text += "\n"+"{:,}".format(self.player.score)
                # self.score_label.basic_label.font_size = 40.5
            if self.player.score_change == True:
                self.game_scrn.score_obj.on_update()
        # else:
        #     self.score_label.basic_label.text += "\n"+"{:,}".format(self.player.score)
        #     self.score_label.basic_label.font_size = 35

        #make sure improv mode stays updated. TODO: Find out which part of the game is keeping track of improv mode. Depends on how we trigger it...
        # self.improv = self.player.improv

        
        if self.audio_cont.last_part:
            self.update_bg()


run(MainWidget)