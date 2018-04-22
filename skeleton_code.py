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

import random
import numpy as np
import bisect
import string


class MainWidget(BaseWidget) :
    def __init__(self):
        super(MainWidget, self).__init__()

    def on_key_down(self, keycode, modifiers):
        # play / pause toggle
        if keycode[1] == 'p':
            pass

        #pass spacebar values to player as " "
        if keycode[1] == 'spacebar':
            pass

        # button down
        letter = lookup(keycode[1], string.ascii_letters, set(string.ascii_letters))
        if letter != None:
            print 'down', letter

        spec_char = lookup(keycode[1], string.punctuation, set(string.punctuation))
        if spec_char != None:
            print 'down', spec_char

    def on_key_up(self, keycode):
        # button up
        letter = lookup(keycode[1], string.ascii_letters, set(string.ascii_letters))
        if letter != None:
            print 'down', letter

        spec_char = lookup(keycode[1], string.punctuation, set(string.punctuation))
        if spec_char != None:
            print 'down', spec_char

    def on_update(self) :
        pass


# creates the Audio driver
# creates a song and loads it with solo and bg audio tracks
# creates snippets for audio sound fx
class AudioController(object):
    def __init__(self, song_path):
        super(AudioController, self).__init__()
        self.audio = Audio(2)

    # start / stop the song
    def toggle(self):
        pass

    # mute / unmute the solo track
    def set_mute(self, mute):
        pass

    # play a sound-fx (miss sound)
    def play_sfx(self):
        pass

    # needed to update audio
    def on_update(self):
        self.audio.on_update()


# holds data for gems and barlines.
class SongData(object):
    def __init__(self):
        super(SongData, self).__init__()

    # read the gems and song data. You may want to add a secondary filepath
    # argument if your barline data is stored in a different txt file.
    def read_data(self, filepath):
        pass

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
        self.gstatus = gstatus
        self.gem_hits = 0
        self.gem_misses = 0
        self.particle_off = stop_cb
        self.longest_streak = 0

    # called by MainWidget
    def on_button_down(self, char):
        
        curr_lyric = self.display.curr_lyric

        if curr_lyric.next_avail == char:
            self.display.on_down(char,True)

        self.display.on_down(char,False)

    # called by MainWidget
    def on_button_up(self, char):
        pass

    # needed to check if for pass gems (ie, went past the slop window)
    def on_update(self):
        pass

run(MainWidget)
