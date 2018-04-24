#Final Project Skeleton Code


import sys
sys.path.append('..')
from common.core import *
from common.audio import *
from common.mixer import *
from common.wavegen import *
from common.wavesrc import *
from common.gfxutil import *

from kivy.graphics.instructions import InstructionGroup
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.graphics import PushMatrix, PopMatrix, Translate, Scale, Rotate
from kivy.clock import Clock as kivyClock
from kivy.core.text import Label
from kivy.core.text.text_layout import layout_text

import random
import numpy as np
import bisect
import string
import matplotlib.colors as colors
from colorsys import hsv_to_rgb
from collections import deque

def score_label():
    l = Label(text = "Score", valign='top', font_size='20sp',
              pos=(Window.width*1.3, Window.height*0.4),
              text_size=(Window.width, Window.height))
    return l

def end_label(text):
    l = Label(text = text, valign = 'top', halign = 'center',font_size = '50sp',
              pos = (Window.width*0.35,Window.height*0.25),
              text_size = (Window.width,Window.height), color=(1,0,0,1))
    return l

# Use matplotlib colors as follows:
# colors.hex2color('#ffffff')        #==> (1.0, 1.0, 1.0)
# colors.rgb2hex((1.0, 1.0, 1.0))    #==> '#ffffff'

class MainWidget(BaseWidget):
    def __init__(self):
        super(MainWidget, self).__init__()
        self.song = 'Stems/Fetish'
        self.audio_cont = AudioController(self.song)
        self.gem_data = SongData()
        self.gem_data.read_data('Stems/Fetish-Full.txt')
        self.beat_disp = BeatMatchDisplay(self.gem_data)
        # with self.canvas.before:
        #     # ADD BACKGROUND IMAGE TO GAME
        #     self.bg_img = Rectangle(size=(Window.width,Window.height),pos = (0,0),source="bg_pic3.jpg")
        self.canvas.add(self.beat_disp)
        # self.score_label = score_label()
        # self.add_widget(self.score_label)
        self.player = Player(self.gem_data,self.beat_disp,self.audio_cont)

    def on_key_down(self, keycode, modifiers):
        print 'key-down', keycode, modifiers

        # play / pause toggle
        if keycode[1] == 'enter':
            self.player.toggle_game()

        #pass spacebar values to player as " "
        if keycode[1] == 'spacebar':
            self.player.on_button_down(" ")
            print "down ", "spacebar"

        # button down
        letter = lookup(keycode[1], string.ascii_letters, list(set(string.ascii_letters)))
        if letter != None:
            self.player.on_button_down(letter)
            print "down ", letter 

        spec_char = lookup(keycode[1], string.punctuation, list(set(string.punctuation)))
        if spec_char != None:
            self.player.on_button_down(spec_char)
            print "down ", spec_char

    def on_key_up(self, keycode):
        # button up
        letter = lookup(keycode[1], string.ascii_letters, list(set(string.ascii_letters)))
        if letter != None:
            self.player.on_button_up(letter)

        spec_char = lookup(keycode[1], string.punctuation, list(set(string.punctuation)))
        if spec_char != None:
            self.player.on_button_up(spec_char)

    def on_update(self) :
        self.player.on_update()


# creates the Audio driver
# creates a song and loads it with solo and bg audio tracks
# creates snippets for audio sound fx
class AudioController(object):
    def __init__(self, song_path,listener=None):
        super(AudioController, self).__init__()
        if listener:
            self.audio = Audio(2,listener)
        else:
            self.audio = Audio(2)
        self.mixer = Mixer()
        self.song_path = song_path
        self.bg_audio = WaveFile(self.song_path+'_inst.wav')
        self.solo_audio = WaveFile(self.song_path+'_vocals.wav')
        # self.miss_sfx = WaveFile("break.wav")
        self.bg_gen = WaveGenerator(self.bg_audio)
        self.solo_gen = WaveGenerator(self.solo_audio)
        # self.miss_sfx_gen = WaveGenerator(self.miss_sfx)
        # self.miss_sfx_gen.set_gain(2.0)
        self.audio.set_generator(self.mixer)

    def start(self):
        if self.mixer.contains(self.bg_gen):
            """
            Needed to restart game
            """
            self.bg_gen.release()
            self.solo_gen.release()
        self.bg_gen = WaveGenerator(self.bg_audio)
        self.solo_gen = WaveGenerator(self.solo_audio)
        self.bg_gen.set_gain(0.5)
        self.solo_gen.set_gain(0.5)
        self.mixer.add(self.bg_gen)
        self.mixer.add(self.solo_gen)

    # start / stop the song
    def toggle(self):
        self.bg_gen.play_toggle()
        self.solo_gen.play_toggle()
        
    # mute / unmute the solo track
    def set_mute(self, mute):
        if mute:
            self.solo_gen.set_gain(0.1)
        else:
            self.solo_gen.set_gain(1)

    # play a sound-fx (miss sound)
    def play_sfx(self):
        miss_sfx = WaveFile("break.wav")
        miss_sfx_gen = WaveGenerator(self.miss_sfx)
        miss_sfx_gen.set_gain(1.5)
        if self.mixer.contains(miss_sfx_gen):
            miss_sfx_gen.reset()
            miss_sfx_gen.play()
        else:
            self.mixer.add(miss_sfx_gen)

    def set_listener(self,listen_cb):
        self.audio.listen_func = listen_cb

    # needed to update audio
    def on_update(self):
        self.audio.on_update()


# holds data for gems and barlines.
class SongData(object):
    def __init__(self):
        super(SongData, self).__init__()
        self.word_list= []
    # read the gems and song data. You may want to add a secondary filepath
    # argument if your barline data is stored in a different txt file.
    def read_data(self, words_filepath):
        words = open(words_filepath).readlines()

        for word in words:
            (start_sec, text) = word.strip().split('\t')
            self.word_list.append((float(start_sec),text))



    # TODO: figure out how gem and barline data should be accessed...



# display for a single gem at a position with a color (if desired)
class GemDisplay(InstructionGroup):
    def __init__(self, pos, color):
        super(GemDisplay, self).__init__()

    # change to display this gem being hit
    def on_hit(self):
        pass

    # change to display a passed gem
    def on_pass(self):
        pass

    # useful if gem is to animate
    def on_update(self, dt):
        pass


# Displays one button on the nowbar
class ButtonDisplay(InstructionGroup):
    def __init__(self, pos, color):
        super(ButtonDisplay, self).__init__()

    # displays when button is down (and if it hit a gem)
    def on_down(self, hit):
        pass

    # back to normal state
    def on_up(self):
        pass



# Displays and controls all game elements: Nowbar, Buttons, BarLines, Gems.
class BeatMatchDisplay(InstructionGroup):
    def __init__(self, gem_data):
        super(BeatMatchDisplay, self).__init__()

    def start(self):
        pass

    def toggle(self):
        pass
    # called by Player. Causes the right thing to happen
    def gem_hit(self, gem_idx):
        pass

    # called by Player. Causes the right thing to happen
    def gem_pass(self, gem_idx):
        pass

    # called by Player. Causes the right thing to happen
    def on_button_down(self, char, hit):
        pass

    # called by Player. Causes the right thing to happen
    def on_button_up(self, char):
        pass

    # call every frame to make gems and barlines flow down the screen
    def on_update(self) :
        pass



# Handles game logic and keeps score.
# Controls the display and the audio
class Player(object):
    def __init__(self, gem_data, display, audio_ctrl):
        super(Player, self).__init__()
        self.game_started = False
        self.game_paused = True
        self.audio_ctrl = audio_ctrl
        self.display = display
        self.gem_data = gem_data
        self.gem_hits = 0
        self.gem_misses = 0
        self.longest_streak = 0


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


    # called by MainWidget
    def on_button_down(self, char):
        
        curr_lyric = self.display.curr_lyric

        if curr_lyric.next_avail == char:
            self.display.on_button_down(char,True)

        self.display.on_button_down(char,False)

    # called by MainWidget
    def on_button_up(self, char):
        self.display.on_button_up(char)

    # needed to check if for pass gems (ie, went past the slop window)
    def on_update(self):
        self.audio_ctrl.on_update()
        self.display.on_update()

run(MainWidget)
