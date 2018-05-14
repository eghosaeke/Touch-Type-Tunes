#Final Project Skeleton Code


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
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition

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



if os.name == "nt": 
    font_path = "C:\\Windows\\Fonts"
elif os.name == "mac" or os.name == "posix":
    font_path = ["/System/Library/Fonts","/Library/Fonts"]


# font_files = filter(lambda f: f.endswith(".ttf") or f.endswith(".TTF"),os.listdir(font_path[1]))
# print font_files

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


def system_info_label():
    l = BasicLabel("",tpos=(20, 590),font_size=25)
    return l

def end_label(text):
    if platform == "macosx":        
        l = CustomLabel(text,font_size=50,invert_text=True,font_name="Comic Sans MS")
    elif platform == "win":
        l = CustomLabel(text,font_size=50,invert_text=True,font_name="comic")
    else:
        l = CustomLabel(text,font_size=50,invert_text=True)
    return l


# Use matplotlib colors as follows:
# colors.hex2color('#ffffff')        #==> (1.0, 1.0, 1.0)
# colors.rgb2hex((1.0, 1.0, 1.0))    #==> '#ffffff'
class GameStatusChecker(object):
    """
    Class to keep track of the status of the game

    Parameters
    ----------
    gameover_cb: function
        Callback function used to signal end game status and onset of
        end game screen ui 
    """
    def __init__(self,gameover_cb):
        super(GameStatusChecker, self).__init__()
        self.game_started = False
        self.game_paused = True
        self.game_finished = False
        self.gameover_cb = gameover_cb
        self.call_once = False

    
    def audio_listener(self,data,num_ch):
        """
        Function to check audio data for silence signifying the end of the song

        Parameters
        ----------
        data: numpy.ndarray
            Audio samples
        num_ch: int
            Number of channels
        """
        if self.game_started and not self.game_paused:
            no_data = not data.any()
            if no_data:
                self.game_finished = True
                if not self.call_once:
                    self.gameover_cb()
                    self.call_once = True

class GameStatusLabel(InstructionGroup):
    def __init__(self,player_cb):
        super(GameStatusLabel, self).__init__()
        self.title_screen = True
        self.paused_screen = False
        self.end_screen = False
        self.color = Color(0,0,0,0.75)
        self.pos = (0,0)
        self.size = (Window.width,Window.height)
        self.bg_rect = Rectangle(pos=self.pos,size=self.size,source="studio_booth.jpg")

        self.label = BasicLabel("Title Screen",tpos=(Window.width*0.1,Window.height*0.85),font_size=40,halign='center')
        self.alpha_rect = Rectangle(pos=self.pos,size=self.size)
        self.fading_out = False
        self.fading_in = False
        self.player_cb = player_cb
        self.game_paused = True
        self.game_finished = False
        self.is_active = True
        self.end_text = "Game Over!"
        

    
    def activate(self):
        self.is_active = True
        if self.title_screen:
            self.add(PushMatrix())
            self.add(self.bg_rect)
            self.add(self.color)
            self.add(self.alpha_rect)
            self.add(PopMatrix())
            self.text_color = Color(1,1,1,0.85)
            self.add(self.text_color)
            self.add(self.label)
            self.title_text = "Welcome to Touch Type Tunes!\n\nWhen the music starts, type the\nthe highlighted letters on the screen.\nPress 'shift enter' to cue the music."
            self.label.text = self.title_text
            self.game_paused = False
        elif not self.game_paused and not self.game_finished:
            self.add(PushMatrix())
            self.add(self.bg_rect)
            self.add(self.color)
            self.add(self.alpha_rect)
            self.add(PopMatrix())
            self.text_color = Color(1,1,1,0.85)
            self.add(self.text_color)
            self.add(self.label)
            self.paused_text = "Studio session paused\nWhen you're ready\npress 'shift enter' to continue the game"
            self.label.text = self.paused_text
            self.game_paused = True
            self.paused_screen = True
        elif self.game_finished:
            self.add(PushMatrix())
            self.add(self.bg_rect)
            self.add(self.color)
            self.add(self.alpha_rect)
            self.add(PopMatrix())
            self.text_color = Color(1,1,1,0.85)
            self.add(self.text_color)
            self.add(self.label)
            
            self.label.text = self.end_text
            self.game_paused = True
            self.paused_screen = False

    def deactivate(self):
        self.is_active = False
        self.remove(self.label)
        self.remove(self.text_color)
        self.remove(self.alpha_rect)
        self.remove(self.color)
        self.remove(self.bg_rect)
        if self.title_screen:
            self.title_screen = False
        elif self.paused_screen:
            self.game_paused = False
            self.paused_screen = False
        elif self.game_finished:
            pass

        
    def transistion(self):
        self.time = 0
        self.fade_color = Color(0,0,0,0.75)
        self.fade_rect = Rectangle(pos=(0,0),size=(Window.width,Window.height))
        self.fade_out = KFAnim((0,0,0,0,0.75),(0.25,0,0,0,1))
        self.fade_in = KFAnim((0,0,0,0,1),(0.25,0,0,0,0))
        self.fading_out = True
        self.fading_in = False
        self.add(self.fade_color)
        self.add(self.fade_rect)
        self.on_update(0)


    def restart(self):
        self.title_screen = True
        self.paused_screen = False
        self.end_screen = False
        self.game_paused = True
        self.game_finished = False

    def paused_screen(self):
        if not self.game_paused:
            pass

    def end_screen(self):
        pass

    def on_update(self,dt):
        if self.fading_out:
            r,g,b,a = self.fade_out.eval(self.time)
            self.color = Color(r,g,b,a)
            self.add(self.color)
            self.time += dt
            if not self.fade_out.is_active(self.time):
                print "done fading out: "
                self.remove(self.bg_rect)
                self.remove(self.color)
                self.remove(self.alpha_rect)
                self.remove(self.label)
                self.fading_out = False
                self.fading_in = True
                self.time = 0
        elif self.fading_in:
            print "start fade in"
            r,g,b,a = self.fade_in.eval(self.time)
            self.color = Color(r,g,b,a)
            self.add(self.color)
            self.time += dt
            if not self.fade_in.is_active(self.time):
                self.remove(self.fade_color)
                self.remove(self.fade_rect)
                self.fading_in = False
                self.player_cb()

        return True



class GameScreen(Screen):
    pass



        



class MainWidget(BaseWidget):
    def __init__(self):
        super(MainWidget, self).__init__()
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

        self.sm = ScreenManager(transition=FadeTransition())
        self.game_scrn = GameScreen(name="game")
        self.sm.add_widget(self.game_scrn)
        # self.add_widget(self.sm)
        
        with self.canvas.before:
        #     # ADD BACKGROUND IMAGE TO GAME
            self.bg_img = Rectangle(size=self.size,pos = self.pos,source="mic-booth.jpg")
            Color(0, 0, 0, 0.3)
            self.sidebar = Rectangle(size = self.size ,pos =self.pos)
            

        

        self.canvas.add(Color(1,1,1,0.8))
        self.canvas.add(self.beat_disp)

        self.improv_obj = AnimGroup()
        self.improv_obj.add(self.improv_disp)
        self.canvas.add(self.improv_obj)
        
        # self.canvas.add(PopMatrix())
        self.score_label = ScoreLabel()
        self.score_obj = AnimGroup()   
        self.score_obj.add(self.score_label)
        self.canvas.add(self.score_obj)
        self.info = system_info_label()
        self.canvas.add(self.info)
        self.particles = deque()
        self.player = Player(self.gem_data,self.beat_disp,self.improv_obj,self.improv_disp,self.audio_cont,self.stop_ps)
        self.caps_on = False
        # with self.canvas.after:
        self.gstatus = GameStatusLabel(self.player.toggle_game)
        self.gstatus_obj = AnimGroup()
        self.gstatus_obj.add(self.gstatus)
        self.canvas.add(self.gstatus_obj)
        self.gstatus.activate()
        # test_text = "HELLO WOLRD"
        # test_text += "\nFinal Score: "+"{:,}".format(65464163)
        # test_text += "\nLongest Streak: "+"{:,}".format(5264)
        # test_text += "\nAccuracy: "+"{0:.2f}".format(0.65654*100)+"%"
        # test_text += "\n\nPress 'r' to restart the game"
        # self.hello = BasicLabel(test_text,tpos=(200,400),font_size=15,invert_text=False,font_name="DejaVuSans")
        # self.hello = CustomLabel(test_text,font_size=15,font_name="DejaVuSans")
        # self.hello.set_color(6,(0,1,0))
        # # self.hello.set_bold(0)
        # self.hello.set_color(6,(0,0,1))
        # self.hello.set_bold(6)
        # self.hello.set_italic(6)
        # for i in range(5):
        #     self.hello.set_color(i,(0,1,0))
        # self.rect = Rectangle(size=self.hello.texture.size,pos=(50,50),texture=self.hello.texture)
        # self.canvas.add(self.rect)
        # self.canvas.add(self.hello)
        self.i = 0


        self.bind(pos=self.update_bg)
        self.bind(size=self.update_bg)



    def update_bg(self, *args):
        self.bg_img.pos = self.pos
        self.bg_img.size = self.size
        width=float(self.size[0])
        height=float(self.size[1])
        self.sidebar.size=[width/2,height]
        if platform == "macosx":
            ##GAME SCREEN VARIABLES
            self.gstatus.size = (width,height)
            self.gstatus.label.tpos=(.5*(width-self.gstatus.label.size[0]),.75*height)
            self.gstatus.bg_rect.size = self.gstatus.size
            self.gstatus.alpha_rect.size = self.gstatus.size

            self.score_label.basic_label.tpos =[width*.8,height*.8]
            self.improv_disp.tpos =[width*.3,height*.7]
            self.improv_disp.translate.x =width*.85
            self.improv_disp.translate.y =height*.2
            self.beat_disp.start_pos = (20,height+10)
        elif platform == "win":
            self.gstatus.size = (width,height)
            self.gstatus.label.tpos=(.5*(width-self.gstatus.label.size[0]),.75*height)
            self.gstatus.bg_rect.size = self.gstatus.size
            self.gstatus.alpha_rect.size = self.gstatus.size
            self.improv_disp.scale.origin = (0,0)
            self.score_label.basic_label.tpos =[width*.8,height*.8]
            self.improv_disp.tpos =[width*.3,height*.6]
            self.improv_disp.translate.x = width*1.25
            self.beat_disp.start_pos = (20,height+10)

   

        
    def on_key_down(self, keycode, modifiers):
        # print 'key-down', keycode, modifiers

        if keycode[1] == 'capslock':
            self.caps_on = not self.caps_on


        # Used for testing and debugging
        if keycode[1] == 'tab':
            # self.hello.text += "\nHello World Again!"
            
            if "shift" in modifiers:
                self.player.game_paused = False
                self.player.improv = True
                self.improv_disp.start()
            else:

                self.improv_disp.add_improv_word(self.vocalImprovBuffers.keys()[self.i])
                self.i += 1
                self.i %= len(self.vocalImprovBuffers)
        # play / pause toggle
        if keycode[1] == 'enter':
            if "shift" in modifiers:
                if self.gstatus.is_active:
                    self.gstatus.deactivate()
                else:
                    self.gstatus.activate()
                self.player.toggle_game()
                # self.canvas.remove(self.gstatus_obj)
                # self.gstatus.transistion()
            elif "ctrl" in modifiers:
                self.improv = False
                self.player.improv = False
                self.beat_disp.improv = False
                self.audio_cont.improv = False
                if self.gstatus.is_active:
                    self.gstatus.deactivate()
                self.gstatus.restart()
                self.gstatus.activate()
                self.player.restart_game()

        #pass spacebar values to player as " "
        if keycode[1] == 'spacebar':
            self.player.on_button_down(" ")
            # self.hello.text += " "
            # print "down ", "spacebar"
        
        
        #Use forward slash to end improv mode
        if keycode[1] == '\\':
            self.improv = False
            

        # button down
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
               
            
#        #Dev Tools for Improv:
#        #Testing buffer playback
#        bufferKeys = ['Loop1', 'Loop2', 'LoopF', 'Final']
#        if keycode[1] == 'j':
#            self.loop1 = WaveGenerator(self.buffers[bufferKeys[0]], True)
#            self.audio_cont.mixer.add(self.loop1)
#        
#        if keycode[1] == 'k':
#            self.loop2 = WaveGenerator(self.buffers[bufferKeys[1]], True)
#            self.audio_cont.mixer.add(self.loop2)
#            
#        if keycode[1] == 'l':
#            self.loopF = WaveGenerator(self.buffers[bufferKeys[2]], True)
#            self.audio_cont.mixer.add(self.loopF)
#        
#        if keycode[1] == ';':
#            self.final = WaveGenerator(self.buffers[bufferKeys[3]], True)
#            self.audio_cont.mixer.add(self.final)
            
    def on_key_up(self, keycode):
        # button up
        letter = lookup(keycode[1], string.ascii_letters, sorted(string.ascii_letters))
        if letter != None:
            self.player.on_button_up(letter)

        spec_char = lookup(keycode[1], string.punctuation, sorted(string.punctuation))
        if spec_char != None:
            self.player.on_button_up(spec_char)
            
            
#        #Dev Tools for Improv
#        #Testing buffer placback
#        if keycode[1] == 'j':
#            self.audio_cont.mixer.remove(self.loop1)
#            
#        if keycode[1] == 'k':
#            self.audio_cont.mixer.remove(self.loop2)
#            
#        if keycode[1] == 'l':
#            self.audio_cont.mixer.remove(self.loopF)
#            
#        if keycode[1] == ';':
#            self.audio_cont.mixer.remove(self.final)
            
    def improv_cb(self,end=False):
        if end:
            self.improv_disp.restart()
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
        
        self.gstatus.end_text += "\n\nAccuracy: {:.2%}".format(self.player.get_words_hit()/self.beat_disp.get_max_words())
        self.gstatus.end_text += "\nWords Hit: {}".format(self.player.get_words_hit())
        self.gstatus.game_finished = True
        self.gstatus.activate()

    def ps_cb(self,pos,color,duration=1.0):
        """
        Add particle systems to screen on succesful event
        """
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
        if len(self.particles) > 0:
            ps = self.particles.popleft()
            ps.stop(True)
        

    def on_update(self) :
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
        self.improv_obj.on_update()
        self.score_label.basic_label.text = "Score"
        self.score_label.basic_label.text += "\n"+"{:,}".format(self.player.score)
            # self.score_label.basic_label.font_size = 40.5
        if self.player.score_change ==True:
            self.score_obj.on_update()
        # else:
        #     self.score_label.basic_label.text += "\n"+"{:,}".format(self.player.score)
        #     self.score_label.basic_label.font_size = 35

        #make sure improv mode stays updated. TODO: Find out which part of the game is keeping track of improv mode. Depends on how we trigger it...
        # self.improv = self.player.improv

        
        if self.audio_cont.last_part:
            self.update_bg()
        

# creates the Audio driver
# creates a song and loads it with solo and bg audio tracks
# creates snippets for audio sound fx
class AudioController(object):
    def __init__(self, song_path,improv_cb=None,gameover_cb=None,listener=None):
        super(AudioController, self).__init__()
        if listener:
            self.audio = Audio(2,listener)
        else:
            self.audio = Audio(2)
        self.mixer = Mixer()
        self.song_path = song_path

        self.miss_sfx = WaveFile("miss2.wav")
        self.miss_sfx_gen= WaveGenerator(self.miss_sfx)
        self.bg_audio = WaveFile(self.song_path+'_inst_1.wav')
        self.solo_audio = WaveFile(self.song_path+'_vocals_1.wav')
        # self.miss_sfx = WaveFile("break.wav")
        self.improv_sect = Sequencer()
        self.bg_gen = WaveGenerator(self.bg_audio)
        self.solo_gen = WaveGenerator(self.solo_audio)
        self.audio.set_generator(self.mixer)
        self.game_paused = True
        self.game_started = False
        self.improv = False
        self.last_part = False
        self.improv_cb = improv_cb
        self.gameover_cb = gameover_cb
        self.called_gg = False

    def start(self):
        # if self.mixer.contains(self.bg_gen) or self.mixer.contains(self.improv_sect):
        #     """
        #     Needed to restart game
        #     """
        #     self.mixer.remove_all()
        #     self.bg_audio = WaveFile(self.song_path+'_inst_1.wav')
        #     self.solo_audio = WaveFile(self.song_path+'_vocals_1.wav')
        #     self.last_part = False
        self.bg_gen = WaveGenerator(self.bg_audio)
        self.solo_gen = WaveGenerator(self.solo_audio)
        self.bg_gen.set_gain(0.5)
        self.solo_gen.set_gain(0.5)
        self.mixer.add(self.bg_gen)
        self.mixer.add(self.solo_gen)
        self.game_paused = False
        self.game_started = True
        if self.called_gg:
            self.called_gg = False

    def restart(self):
        if self.mixer.contains(self.bg_gen) or self.mixer.contains(self.improv_sect):
            """
            Needed to restart game
            """
            self.mixer.remove_all()
            self.bg_audio = WaveFile(self.song_path+'_inst_1.wav')
            self.solo_audio = WaveFile(self.song_path+'_vocals_1.wav')
            self.last_part = False
            self.game_paused = True
            self.game_started = False
            self.improv = False
            self.called_gg = False

    # start / stop the song
    def toggle(self):
        self.bg_gen.play_toggle()
        self.solo_gen.play_toggle()
        self.game_paused = not self.game_paused
        
    # mute / unmute the solo track
    def set_mute(self, mute):
        if mute:
            self.solo_gen.set_gain(0.1)
        else:
            self.solo_gen.set_gain(1)

    # play a sound-fx (miss sound)
    def play_sfx(self):
        # miss_sfx = WaveFile("miss1.wav")
        # miss_sfx_gen = WaveGenerator(self.miss_sfx)
        # miss_sfx_gen.set_gain(.3)
#        print len(self.mixer.generators)
        if self.mixer.contains(self.miss_sfx_gen):
            self.miss_sfx_gen.reset()
            self.miss_sfx_gen.play()
        else:
            self.mixer.add(self.miss_sfx_gen)
            self.miss_sfx_gen.reset()
            self.miss_sfx_gen.play()

    def set_listener(self,listen_cb):
        self.audio.listen_func = listen_cb

    def play_buf(self,buf):
        gen = WaveGenerator(buf)
        gen.set_gain(1.0)
        self.mixer.add(gen)
    
    def load_improv(self,bufs):
        for buf in bufs:
            improv_bg_audio = WaveGenerator(buf)
            improv_bg_audio.set_gain(1.0)
            self.improv_sect.add(improv_bg_audio)
        self.mixer.add(self.improv_sect)

    
    def load_part2(self):
        self.bg_audio = WaveFile(self.song_path+'_inst_2.wav')
        self.solo_audio = WaveFile(self.song_path+'_vocals_2.wav')
        self.bg_gen = WaveGenerator(self.bg_audio)
        self.solo_gen = WaveGenerator(self.solo_audio)
        self.bg_gen.set_gain(0.5)
        self.solo_gen.set_gain(0.5)
        self.mixer.add(self.bg_gen)
        self.mixer.add(self.solo_gen)


    # needed to update audio
    def on_update(self):
        self.audio.on_update()
        if not self.game_paused and self.game_started and not self.last_part:
            if self.mixer.get_num_generators() == 0:
                if not self.improv and self.improv_cb:
                    self.improv_cb()
                elif self.improv and self.improv_cb:
                    self.improv_cb(end=True)
                    self.load_part2()
                    self.last_part = True
        if self.game_started  and self.last_part and self.mixer.get_num_generators() < 2:
            if self.gameover_cb and not self.called_gg:
                self.gameover_cb()
                self.called_gg = True
        elif self.game_started and self.last_part:
            self.bg_audio = WaveFile(self.song_path+'_inst_1.wav')
            self.solo_audio = WaveFile(self.song_path+'_vocals_1.wav')
        



# holds data for gems and barlines.
class SongData(object):
    def __init__(self):
        super(SongData, self).__init__()
        self.list= []
        self.all_words=[]
        self.phrases=[]
        self.phrases_dict = OrderedDict()
        
        #Loop = (Lyric, startTime, duration)

        self.loops = []
        #Mark = lyric: (startTime, endTime)
        self.marks = {}
        
    # read the gems and song data. You may want to add a secondary filepath
    # argument if your barline data is stored in a different txt file.
    def read_data(self, words_filepath):
        words = open(words_filepath).readlines()

        phrase = ""
        phrase_to_type=""
        improv_word = ""
        start_time = None
        end_time = None
        
        for word in words:
            # print "phrase: ",phrase
            # print "Start: ", start_time
            # print "End: ", end_time
            (start_sec, text) = word.strip().split('\t')
            
            #TODO: (maybe?) possible Designs:
            #1) Tag the improv section with a timestamp at the beginning/end (and return the times)
            #2) trigger the improv section when the word improv is dequed (find )
            
            if "." not in text:
                if '*' in text:
                    # phrase+= text[:-1]+"_"
                    i = text.find("*")
                    phrase+= text[:i]+" "

                    # phrase_to_type += text[:-1]+"_"
                    phrase_to_type += text[:i]+" "
                    j = text.rfind("*")
                    if i != j:
                        improv_word = text[:i]


                else:
                    # phrase += text + "_"
                    phrase += text + " "
                if not start_time:
                  start_time = float(start_sec)
            else:
                # print "phrase end: ", phrase
                # print "end text: ", text
                # split_txt = phrase.strip().split('_')
                split_txt = phrase.strip().split(' ')
                # if text[:-1] != split_txt[-1] :
                #     phrase += split_txt[-1][:-1]
                if text[:-1] != split_txt[-1] :
                    phrase += split_txt[-1][:-1]
                # phrase = phrase.rstrip("_")
                # phrase_to_type = phrase_to_type.rstrip("_")
                phrase = phrase.rstrip(" ")
                phrase_to_type = phrase_to_type.rstrip(" ")
                
                if not end_time:
                    end_time = float(start_sec)
                    self.phrases_dict[phrase] = (phrase_to_type,improv_word,start_time,end_time)
                    self.phrases.append((phrase,phrase_to_type,improv_word,start_time,end_time))
                    phrase = ""
                    phrase_to_type=""
                    improv_word = ""
                    start_time,end_time = None,None
            self.list.append((text,start_sec))
            self.all_words.append(text)
        
    def get_phrases(self):
        return self.phrases_dict

    def get_phrases_in_order(self):
        return self.phrases
    
    #Collects a list of background loop times and a dictionary of marked words (with times)
    def read_improv(self, loop_filepath, mark_filepath):
        
        loopFile = open(loop_filepath)
        lines = loopFile.readlines()
        for line in lines:
            #Lyric, startTime, duration
            time, _, duration, name = line.strip().split('\t')
            self.loops.append((name, time, duration))
        
        loopFile.close()
        
        markFile = open(mark_filepath)
        lines = markFile.readlines()
        tempMarks = []
        for line in lines:
            time, lyric = line.strip().split('\t')
            tempMarks.append((time, lyric))
            
        markFile.close()
        for i in range(len(tempMarks)):
            
            #Even entries are start times, odd entries are endTimes
            if i%2== 0:
                
                #Mark = (lyric, startTime, endTime)
                self.marks[tempMarks[i][1]] = (tempMarks[i][0], tempMarks[i+1][0])
        
        return (self.loops, self.marks)
        
def wrap_text(text,font_size,text_size):
    max_size = text_size
    space_size = 14
    chr_s = 2
    split_txt = text.split(" ")
    fin_txts = [""]
    i = 0
    for t in split_txt:
        # print "max_size: ",max_size
        # print "line_size: ",(len(t)+len(fin_txts[i]))*font_size
        if (len(t)+len(fin_txts[i]))*(font_size+chr_s) < max_size:
            fin_txts[i] += t + " "
        else:
            fin_txts.append(t+" ")
            i += 1

    return "\n".join([x.strip() for x in fin_txts])


class LyricsWord(InstructionGroup):
    def __init__(self,pos,color,text,start_t,end_t,vel,point_cb,improv_cb,interactive=False,improv="",anim_cb=None):
        super(LyricsWord, self).__init__()
        self.text = text
        self.interactive = interactive
        self.end_of_lyric = False
        self.pos = np.array(pos, dtype=np.float)
        self.point_cb = point_cb
        self.improv_cb = improv_cb
        self.color = color
        if platform == "win":
            self.label = CustomLabel(text,color=color,halign=None,invert_text=False, font_size=40,font_name="comic")
        elif platform == "macosx":
            self.label = CustomLabel(text,color=color,invert_text=True, font_size=40,font_name="Microsoft Sans Serif")
        else:
            self.label = CustomLabel(text,color=color,invert_text=True, font_size=40)

        self.current=0
        self.num_words = len(self.text.strip().split(" "))
        self.next_avail = self.text[self.current]
        self.start_time = start_t
        self.end_time = end_t
        self.scroll_t = self.end_time - self.start_time
        # self.scroll_t = 25
        # self.vel = -self.pos[1]/self.scroll_t
        self.vel = vel
        self.time = 0
        self.pulse_time=0
        self.char_time={}


        self.added_lyric = False
        self.on_screen = False
        self.below_screen = False
        self.improv_word = False
        self.anim_cb = anim_cb
        self.flying = False
        self.called_fly = False
        self.pulsing = False
        self.pulsing_char= False
        self.start_size=40
        # print "text to type: ",text_to_type
        # print "text: ",text
        self.improv = improv
        if improv == self.text.strip():
            self.improv_word = True
            self.label.set_colors((1,(215.0/255),0),text)
        elif self.interactive:
            self.label.set_colors((0,.87,1,1),text)
        # for i in range(len(self.label.text)):
        #     self.label.set_colors((0,0,0,0),"_")
        
        self.rect = Rectangle(size=self.label.texture.size,pos=pos,texture=self.label.texture)


    #Use self.label set_color() function to change color of text at an index 
    def on_hit(self):
        r=float(np.interp(self.current,(0,len(self.text)),(19,43)))/255
        g=float(np.interp(self.current,(0,len(self.text)),(109,224)))/255
        b=float(np.interp(self.current,(0,len(self.text)),(14,33)))/255
        green=(r,g,b)

        r=1
        g=215.0/255
        b=0
        a=float(np.interp(self.current,(0,len(self.text)),(0.3,1)))
        gold=(r,g,b,a)

        
        if self.improv_word:
            self.label.set_colors(gold,None,None,self.current+1)
    
        else:
            self.label.set_colors(green,None,None,self.current+1)

        # self.label.set_bold(self.current+1)
        new_text = self.label.texture
        self.rect.texture = new_text
        self.rect.size=self.label.texture.size

        self.pulse_char(self.current)
        
        self.current += 1

        try:
            self.next_avail=self.text[self.current]
            self.end_of_lyric=False
            
            if self.next_avail == " ":
                self.point_cb()
                self.pulse_word()
                self.rect.size=self.label.texture.size
                self.rect.texture=self.label.texture
                if self.improv_word and not self.called_fly:
                    if self.anim_cb:
                        copy_word = self.copy()
                        copy_word.fly()
                        self.anim_cb(copy_word)
                        self.called_fly = True
            return False
        except Exception as e:
            self.end_of_lyric=True
            self.pulse_word()
            self.rect.size=self.label.texture.size
            if self.improv_word and not self.called_fly:
                if self.anim_cb:
                    copy_word = self.copy()
                    copy_word.fly()
                    self.anim_cb(copy_word)
                    self.called_fly = True
                
            return True
#            print e
#            print "END OF LYRIC"


    def copy(self):
        label_copy = self.label.copy()
        new_word = LyricsWord(self.pos.copy(),self.color,self.text,self.start_time,self.end_time,self.vel,self.point_cb,self.improv_cb,interactive=self.interactive,improv=self.improv)
        new_word.label = label_copy
        new_word.rect.texture = label_copy.texture
        return new_word

    def on_miss(self):
        red=(1,0,0,1)
        self.label.set_color(self.current,red)
        self.pulse_word()

    def fly(self):
        x = np.array([self.pos[0],Window.width*0.65])
        y = np.array([self.pos[1],Window.height*0.5])
        t = np.array([0,0.3])
        self.anim = zip(t,x,y)
        self.flying_anim = KFAnim(*self.anim)
        self.time = 0
        self.flying = True
        self.rect.size=self.label.texture.size
        self.add(self.rect)

    def pulse_word(self):
        start_size = self.label.font_size       
        end_size = self.label.font_size + 10
        self.pulse_anim = KFAnim((0, start_size),(.1, end_size),(.2,start_size))
        self.pulse_time = 0
        self.pulsing = True
        self.rect.size=self.label.texture.size

    def pulse_char(self,idx):
        start_size = self.label.font_size       
        end_size = self.label.font_size + 10
        self.char_anim = KFAnim((0, start_size),(.1, end_size),(.2,start_size))
        self.char_time[idx]=0
        self.pulsing_char = True
        self.rect.size=self.label.texture.size
        self.anim_idx=idx
        


    def on_update(self,dt):
        if self.flying:
            # print "should be animating"
            x,y = self.flying_anim.eval(self.time)
            pos = (x,y)
            self.pos = np.array(pos)
            # print "new pos: ",pos
            self.rect.pos = pos
            self.time += dt
            if not self.flying_anim.is_active(self.time):
                self.improv_cb(self.text.strip())
            return self.flying_anim.is_active(self.time)
        else:
            self.time += dt
            self.pulse_time+=dt
            for i in range(len(self.char_time)):
                self.char_time[i]+=dt
            epsilon = (self.start_time-self.time)
            if epsilon < 0.01:
                if not self.added_lyric:
                    self.add(self.rect)
                    self.added_lyric = True
                self.pos[1] += self.vel * dt
                self.rect.pos = self.pos


            if self.pos[1] < Window.height - self.rect.size[1]/2.0:
                self.on_screen = True
            if self.pos[1] < 0 :
                self.below_screen = True

            if self.pulsing_char:
                char_size= self.char_anim.eval(self.char_time[self.anim_idx])
                self.label.set_size(self.anim_idx,int(char_size))
                self.rect.size=self.label.texture.size
                self.rect.texture=self.label.texture

                


            if self.pulsing:
                new_size= self.pulse_anim.eval(self.pulse_time)
                if new_size > 0:
                    self.label.font_size = (int(new_size))
                    self.rect.size=self.label.texture.size
                    self.rect.texture = self.label.texture
                    
                if not self.pulse_anim.is_active(self.pulse_time):
                    self.pulsing = False
                    self.label.font_size = self.start_size
                    self.rect.size=self.label.texture.size
                    self.rect.texture=self.label.texture

                    for i in range(len(self.char_time)):
                        if not self.char_anim.is_active(self.char_time[i]):
                            self.label.set_size(i,40)
                            self.rect.size=self.label.texture.size
                            self.rect.texture=self.label.texture
            
            return self.time < self.end_time

        


class LyricsPhrase(InstructionGroup):
    def __init__(self,pos,color,text,text_to_type,improv_word,start_t,end_t,queue_cb,point_cb,improv_cb,anim_cb):
        super(LyricsPhrase, self).__init__()
        self.text=text
        self.text_to_type=text_to_type
        self.improv_word = improv_word
        self.end_of_lyric=False
        self.color = color
        self.objects = AnimGroup()
        self.pos = np.array(pos, dtype=np.float)
        self.text_size = (Window.width/2.0-pos[0],None)
        
        self.word_deque = deque()
        self.start_time = start_t
        self.end_time = end_t
        self.scroll_t = self.end_time - self.start_time
        # self.scroll_t = 25
        self.vel = -self.pos[1]/self.scroll_t
        self.point_cb = point_cb
        self.improv_cb = improv_cb
        self.anim_cb = anim_cb
        self.create_phrases()
        self.num_words = len(self.word_deque)
        # print "len of interactive: ",self.num_words
        # print "interactive in phrase: ",self.word_deque
        self.current_word = self.word_deque[0]
        self.time = 0
        self.queue_cb = queue_cb
        
        self.added_lyric = False
        self.on_screen = False
        self.below_screen = False

        self.add(self.objects)

    def create_word(self,phrase,interactive):
        # print "curr_phrase: %s, line num: %d" % (curr_phrase,l)
        pos = (self.prev_pos[0]+self.size[0],self.prev_pos[1])
        # print "curr_phrase: %s, line num: %d" % (curr_phrase,l)
        word = LyricsWord(pos,self.color,phrase,self.start_time,self.end_time,self.vel,self.point_cb,self.improv_cb,interactive=interactive,improv=self.improv_word)
        self.prev_pos = pos
        self.size = word.label.texture.size
        self.objects.add(word)
        if interactive:
            self.word_deque.append(word)
            word.anim_cb = self.anim_cb


    def create_phrases(self):
        wrapped_text = wrap_text(self.text,17,self.text_size[0])
        phrases = self.text.split(self.text_to_type)
        lines = wrapped_text.split("\n")
        # print "phrases: ",phrases
        # print "lines: ",lines
        print self.text
        print self.text_to_type
        reg = re.compile(" "+self.text_to_type+" ")
        reg_beg = re.compile(self.text_to_type+" ")
        reg_end = re.compile(" "+self.text_to_type)
        match = reg.search(self.text)
        if match:
            start_ty = match.start()+1
        else:
            match = reg_beg.search(self.text)
            if match:
                start_ty = match.start()
            else:
                match = reg_end.search(self.text)
                if match:
                    start_ty = match.start()+1
        end_ty = start_ty + len(self.text_to_type)
        i = 0
        glob_dict = OrderedDict()
        for st in lines:
            for l_i in range(len(st)):
                glob_dict[i+l_i] = st[l_i]
            i += len(st)
            glob_dict[i] = " "
            i += 1
            
        curr_phrase = ""
        i = 0
        self.size = [0,0]
        prev_size = [0,0]
        self.prev_pos = self.pos
        for l in range(len(lines)):
            line = lines[l]
            ### Change - to + to invert text ###
            self.prev_pos = (self.pos[0],self.pos[1]-(l*self.size[1]))
            self.size = [0,0]
            for s in range(len(line)):
                char = line[s]
                if i < start_ty:
                    curr_phrase += glob_dict[i]
                    if s == len(line)-1:
                        self.create_word(curr_phrase,False)
                        curr_phrase = ""
                        i+=1
                elif i == start_ty:
                    if s == 0:
                        curr_phrase += glob_dict[i]
                    else:
                        self.create_word(curr_phrase,False)
                        curr_phrase = ""
                        curr_phrase += glob_dict[i]
                elif i > start_ty and i < end_ty:
                    curr_phrase += glob_dict[i]
                    if s == len(line)-1:
                        if l < len(lines)-1 and len(lines) > 1 and i + 1 != end_ty:
                            curr_phrase += " "
                        i += 1
                        self.create_word(curr_phrase,True)
                        curr_phrase = ""
                    else:
                        if glob_dict[i] == " ":
                            self.create_word(curr_phrase,True)
                            curr_phrase = ""
                elif i == end_ty:
                    self.create_word(curr_phrase,True)
                    curr_phrase = ""
                    curr_phrase += glob_dict[i]
                elif i > end_ty:
                    curr_phrase += glob_dict[i]
                    if s == len(line)-1:
                        self.create_word(curr_phrase,False)
                        curr_phrase = ""
                        i+=1
                i+=1


    #Use self.label set_color() function to change color of text at an index 
    def on_hit(self,char):
        if self.current_word.next_avail == char and not self.end_of_lyric:
            end = self.current_word.on_hit()
            if end:
                self.word_deque.popleft()
                if len(self.word_deque) > 0:

                    self.current_word = self.word_deque[0]
        # self.add(self.rect)
        if len(self.word_deque) == 0 and not self.end_of_lyric:
            self.end_of_lyric = True
            self.point_cb(end=True)

            return True
        else:
            return False
#            print e
#            print "END OF LYRIC"


    

    def on_miss(self,char):
        if self.current_word.next_avail != char:
            self.current_word.on_miss()
        # self.add(self.rect)

    def on_update(self,dt):

        self.time += dt
        self.objects.on_update()
        if any([x.on_screen for x in self.objects.objects]):
            self.on_screen = True
        if any([x.below_screen for x in self.objects.objects]):
            self.below_screen = True
        
        if self.time > self.end_time:
            self.queue_cb()
        # if self.pos[1] < 0:
        #     self.queue_cb()

        return self.time < self.end_time
        # return self.pos[1] > 0


class ImprovPhrase(InstructionGroup):
    def __init__(self,phrase,letter,tpos,color):
        super(ImprovPhrase, self).__init__()
        self.phrase = phrase
        self.og_pos = tpos
        self.letter_idx=self.phrase.find(letter)
        self.vel = np.array((randint(50,150),randint(-50,50)), dtype=np.float)
        self.cust = CustomLabel(phrase,font_size=35)
        self.cust.set_colors((0,.87,1,1),letter)
        self.label = Rectangle(size=self.cust.texture.size,pos=tpos,texture=self.cust.texture)
        self.size = self.cust.texture.size
        self.np_tpos = np.array(tpos,dtype=np.float)
        self.tpos = tpos
        self.add(self.label)

    def get_tpos(self):
        return (self.pos[0], self.pos[1] + self.size[1])

    # setter method for tpos of label. Allows for dynamic changes to the label
    def set_tpos(self, p):
        if isinstance(p,np.ndarray):
            p = tuple(p.tolist())
        self.pos = (p[0], p[1] - self.size[1])
        if p != self.pos:
            self.label.pos = self.pos
            self.og_pos = p


    def on_update(self, dt):
        # integrate vel to get pos
        self.np_tpos += self.vel * dt
        # collision with floor
        if self.np_tpos[1] - self.size[1] < 0:
            self.vel[1] = -self.vel[1]
            self.np_tpos[1] =  self.size[1]
        # collision with ceiling
        if self.np_tpos[1] > Window.height:
            self.vel[1] = -self.vel[1]
            self.np_tpos[1] = Window.height
        # collision with left wall
        if self.np_tpos[0] < 0:
            self.vel[0] = -self.vel[0]
            self.np_tpos[0] = 0
        # collision with right wall
        if self.np_tpos[0] + self.size[0] > Window.width:
            self.vel[0] = -self.vel[0]
            self.np_tpos[0] = Window.width - self.size[0]
        self.tpos = self.np_tpos
        self.label.pos = self.tpos
        return True
    tpos = property(get_tpos, set_tpos)

    # cpos = property(get_cpos, set_cpos)
    # size = property(get_csize, set_csize)



class ImprovDisplay(InstructionGroup):
    def __init__(self,phrases,audio_cb=None,ps_cb=None):
        super(ImprovDisplay, self).__init__()
        self.phrases = phrases
        self.add(PushMatrix())
        
        self.letter_colors={}

        self.objects = AnimGroup()
        self.improv_labels = {}

        
        if platform == "macosx":
            self.scale = Scale(0.7,0.7,0.7)
            self.translate = Translate(-Window.width*0.3,0)
        elif platform == "win":
            self.scale = Scale(.5,.5,0)
            self.scale.origin = (0,0)
            self.translate = Translate(Window.width*1.25,Window.height*0.55)
        self.add(self.scale)
        self.add(self.translate)

        self.audio_cb = audio_cb
        self.ps_cb = ps_cb
        self.letter_buf = OrderedDict()
        self.create_hit_dict(self.phrases.keys())
        self.pre_started = True
        if platform == "win":
            self.tpos = (Window.width*.3,Window.height*.5)
        if platform == "macosx":
            self.tpos = (Window.width*.3, Window.height*.7)
        self.time = 0
        self.add(self.objects)
        self.add(PopMatrix())

    # def pre_start(self):
    #     self.add(PushMatrix())
    #     self.scale = Scale(0.5,0.5,0)

    #     self.scale.origin = (0,0)
    #     self.add(self.scale)
    #     self.add(Translate(1000,0))
    #     self.add(self.objects)
        


        
    def start(self):
        self.pre_started = False
        # self.add(PushMatrix())
        # self.scale = Scale(0.5,0.5,0)

        # self.scale.origin = (0,0)
        # self.add(self.scale)
        #self.add(Translate(-Window.width*.8,Window.height*.65))
        # self.add(self.objects)
        self.scale_anim = KFAnim((0, self.scale.x,self.scale.y,self.scale.z), (0.5,1,1,0))
        if platform == "win" or platform == 'linux':
            self.trans_anim = KFAnim((0, self._trans[0],self._trans[1]),(0.5,0,-45))
        elif platform == 'macosx':
            self.trans_anim = KFAnim((0, self._trans[0],self._trans[1]),(0.5,0,0))
        # self.add(PopMatrix())

        
        # tpos = [(100,400),(100,350),(100,300),(100,250)]
        # i = 0
        # for phrase in self.phrases:
        #     letter_to_hit = self.letter_buf.keys()[i]
        #     improv_label = ImprovPhrase(phrase,letter_to_hit,tpos[i],(1,1,1))
        #     self.objects.add(improv_label)
        #     self.improv_labels.append(improv_label)
        #     i += 1

    def restart(self):
        self.remove(self.objects)
        self.add(PushMatrix())
        
        self.letter_colors={}

        self.objects = AnimGroup()
        self.improv_labels = {}

        
        if platform == "macosx":
            self.scale = Scale(0.7,0.7,0.7)
            self.translate = Translate(-Window.width*0.3,0)
        elif platform == "win":
            self.scale = Scale(.5,.5,0)
            self.scale.origin = (0,0)
            self.translate = Translate(Window.width*1.25,Window.height*0.55)
        self.add(self.scale)
        self.add(self.translate)
        self.pre_started = True
        self.tpos = (Window.width*.3,Window.height*.5)
        self.time = 0
        self.add(self.objects)
        self.add(PopMatrix())


    def create_hit_dict(self,phrases):
        for i in range(len(phrases)):
            string = phrases[i]
            for letter in string:
                buf = self.letter_buf.get(letter,None)
                if not buf:
                    self.letter_buf[letter] = self.phrases[string]
                    if len(phrases) == 1:
                        return True
                    else:
                        res = self.create_hit_dict(phrases[i+1:])

                    if not res:
                        self.letter_buf.pop(letter)
                    else:
                        return True
                else:
                    continue

            return False
        return True

    def add_improv_word(self,word):
        print "adding improv word"
        try:
            i = self.phrases.keys().index(word)
            letter_to_hit = self.letter_buf.keys()[i]
            hue=uniform(0.0, 0.9)
            random_color = hsv_to_rgb(hue, 1, 1)

            self.letter_colors[letter_to_hit]=random_color
            improv_label = ImprovPhrase(word,letter_to_hit,self.tpos,(1,1,1))
            self.objects.add(improv_label)
            self.improv_labels[letter_to_hit] = improv_label
            self.tpos = (self.tpos[0],self.tpos[1]-50)



        except Exception as e:
            print e

    def on_hit(self,char):
        buf = self.letter_buf.get(char,None)
        word = self.improv_labels.get(char,None)
        if buf and word and self.audio_cb:
            word.cust.set_color(word.letter_idx,self.letter_colors[char])
            self.audio_cb(buf)
            if self.ps_cb:
                self.ps_cb(word.tpos,self.letter_colors[char])

    def on_up(self,char):

        word = self.improv_labels.get(char,None)
        if word:
            word.cust.set_color(word.letter_idx,(0,.87,1,1))


    def on_update(self,dt):
        if not self.pre_started:
            x,y,z = self.scale_anim.eval(self.time)
            dx,dy = self.trans_anim.eval(self.time)
            
            self._scale = (x,y,z)
            self._trans = (dx,dy)
            self.time += dt
            
            if not self.scale_anim.is_active(self.time):
                self.objects.on_update()
        return True
    def get_scale(self):
        return (self.scale.x,self.scale.y,self.scale.z)
    def set_scale(self, sc):
        self.scale.x = sc[0]
        self.scale.y = sc[1]
        self.scale.z = sc[2]

    def get_trans(self):
        return (self.translate.x,self.translate.y)
    def set_trans(self, sc):
        self.translate.x = sc[0]
        self.translate.y = sc[1]

    _scale = property(get_scale,set_scale)
    _trans = property(get_trans,set_trans)





# Displays and controls all game elements: Nowbar, Buttons, BarLines, Gems.
class BeatMatchDisplay(InstructionGroup):
    def __init__(self, gem_data,improv_cb):
        super(BeatMatchDisplay, self).__init__()
        self.start_pos = (20,Window.height+10)
        self.gem_data = gem_data
        self.improv_cb = improv_cb
        self.objects = AnimGroup()
        self.score = 0
        # self.add(PushMatrix(stack='projection_mat'))

        # m1 = Matrix()
        # scale_x = 1.5
        # m1.set(array=[
        #     [0.0025 * scale_x, 0.0, 0.0, 0.0],
        #     [0.0, 0.003333, 1.0 / Window.height, 0.003333],
        #     [0.0, 0.0, 1.0, 0.0],
        #     [-1.0 * scale_x, -1.0, 1.0, 1.0]
        # ])
        # mi = ChangeState(projection_mat=m1)
        # self.add(mi)

        self.add(self.objects)
        # self.add(PopMatrix(stack='projection_mat'))
        self.game_paused = True
        self.game_started = False
        self.improv = False
        self.lyrics_deque = deque()
        #Max possible interactive words
        self.maxWords = 0.0

    def start(self):
        phrases = self.gem_data.get_phrases_in_order()
        # print phrases
        for data in phrases:
            phrase,phrase_to_type,improv_word,start,end = data
            lyric = LyricsPhrase(self.start_pos,(1,1,1),phrase,phrase_to_type,improv_word,start,end,self.pop_lyric,self.add_points,self.improv_cb,
                                    self.fly_cb)
            self.objects.add(lyric)
            self.lyrics_deque.append(lyric)
            
            #Count the number of interactive words
            self.maxWords+=lyric.num_words
        self.game_paused = False
        self.game_started = True
        self.curr_lyric = self.lyrics_deque[0]

    def restart(self):
        if self.game_started:
            self.remove(self.objects)
            self.objects = AnimGroup()
            self.add(self.objects)
            self.lyrics_deque = deque()
            self.score = 0
            # self.start()

    def toggle(self):
        self.game_paused = not self.game_paused
        
    # called by Player. Causes the right thing to happen
    def letter_hit(self, char):
        if self.curr_lyric.current_word.next_avail == char:
            self.curr_lyric.on_hit(char)
            return True
        else:
            self.curr_lyric.on_miss(char)
            return False

    def add_points(self,end=False):
        self.score_change=True
        self.score += 100
        if end:
            self.score += 100*self.curr_lyric.num_words

    def fly_cb(self,word):
        self.objects.add(word)
    # called by Player. Causes the right thing to happen
    def gem_pass(self):
        pass

    # called by Player. Causes the right thing to happen
    def on_button_down(self, char, hit):
        pass

    # called by Player. Causes the right thing to happen
    def on_button_up(self, char):
        pass

    def pop_lyric(self):
        self.lyrics_deque.popleft()
        if len(self.lyrics_deque) != 0:
            self.curr_lyric = self.lyrics_deque[0]
    
    def get_max_words(self):
        return self.maxWords

    # call every frame to make gems and barlines flow down the screen
    def on_update(self) :

#        if not self.game_paused and not self.improv:
        if not self.game_paused:
            self.objects.on_update()
        



# Handles game logic and keeps score.
# Controls the display and the audio
class Player(object):
    def __init__(self, gem_data, display, improv_group,improv_display, audio_ctrl,stop_cb=None):
        super(Player, self).__init__()
        self.game_started = False
        self.game_paused = True
        self.audio_ctrl = audio_ctrl
        self.display = display
        self.improv_display = improv_display
        self.improv_group = improv_group
        self.gem_data = gem_data
        self.particle_off = stop_cb
        self.gem_misses = 0
        self.longest_streak = 0
        self.improv = False
        self.score_change=False
        
        self.words_hit = 0
        


    # called by MainWidget to play/pause game
    def toggle_game(self):
        if not self.game_started:
            self.audio_ctrl.start()
            self.display.start()
            self.game_started = True
            self.game_paused = False
        else:
            self.audio_ctrl.toggle()
            self.display.toggle()
            self.game_paused = not self.game_paused

    def restart_game(self):
        self.display.restart()
        self.audio_ctrl.restart()
        self.improv_display.restart()
        # self.word_hits = 0
        self.longest_streak = 0
        self.game_paused = True
        self.game_started = False
        self.improv = False
        self.score_change = False
    
    def get_words_hit(self):
        return self.words_hit


    # called by MainWidget
    def on_button_down(self, char):
        if not self.game_paused and not self.improv:
            curr_lyric = self.display.curr_lyric
            if curr_lyric.on_screen:
#                print curr_lyric.next_avail
                hit = self.display.letter_hit(char)
                if hit:
                    self.audio_ctrl.set_mute(False)
                    if char == " " or curr_lyric.end_of_lyric==True:
                        self.score_change=True
                        self.words_hit+=1
                    # self.word_hits+=100
                    # print self.word_hits, "SCORE"
                elif curr_lyric.end_of_lyric:
                    pass
                else:
                    self.score_change=False
                    self.audio_ctrl.play_sfx()
                    self.audio_ctrl.set_mute(True)


        elif not self.game_paused and self.improv:
                self.improv_display.on_hit(char)
    @property
    def score(self):
        return self.display.score
        #self.display.on_button_down(char,False)

    # called by MainWidget
    def on_button_up(self, char):
        if not self.game_paused and not self.improv:
            self.score_change=False
            self.display.on_button_up(char)
        elif not self.game_paused and self.improv:
            self.improv_display.on_up(char)

    # needed to check if for pass gems (ie, went past the slop window)
    def on_update(self):
        self.audio_ctrl.on_update()
        self.display.on_update()
        if self.improv:
            self.improv_group.on_update()
        if self.game_started:
            if self.display.curr_lyric.below_screen:
                if not self.display.curr_lyric.end_of_lyric:
                    self.audio_ctrl.set_mute(True)



run(MainWidget)
