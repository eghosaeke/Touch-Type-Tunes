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
from kivy.core.text import Label as CoreLabel
from kivy.core.text.markup import MarkupLabel

import random
import numpy as np
import bisect
import string
import matplotlib.colors as colors
from colorsys import hsv_to_rgb
from collections import deque
import re

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
        test_text = "HELLO WOLRD"
        test_text += "\nFinal Score: "+"{:,}".format(65464163)
        test_text += "\nLongest Streak: "+"{:,}".format(5264)
        test_text += "\nAccuracy: "+"{0:.2f}".format(0.65654*100)+"%"
        test_text += "\n\nPress 'r' to restart the game"
        self.hello = CustomLabel(test_text,font_size=50,invert_text=True)
        self.hello.set_color(6,(0,1,0))
        # self.hello.set_bold(0)
        self.hello.set_color(6,(0,0,1))
        self.hello.set_bold(6)
        self.hello.set_italic(6)
        for i in range(5):
            self.hello.set_color(i,(0,1,0))
        self.rect = Rectangle(size=self.hello.texture.size,pos=(50,50),texture=self.hello.texture)
        self.canvas.add(self.rect)

        
        

    def on_key_down(self, keycode, modifiers):
        print 'key-down', keycode, modifiers


        if keycode[1] == 'tab':
            print "CLEARING MARKUP"
            self.hello.clear_all_markups()
            self.rect.texture=self.hello.texture
        # play / pause toggle
        if keycode[1] == 'enter':
            self.player.toggle_game()

        #pass spacebar values to player as " "
        if keycode[1] == 'spacebar':
            # self.player.on_button_down(" ")
            print "down ", "spacebar"

            

        # button down
        letter = lookup(keycode[1], string.ascii_letters, sorted(string.ascii_letters))
        if letter != None:
            self.player.on_button_down(letter)

            print "down ", letter , keycode[1]

        spec_char = lookup(keycode[1], string.punctuation, sorted(string.punctuation))
        if spec_char != None:
            self.player.on_button_down(spec_char)
            print "down ", spec_char

    def on_key_up(self, keycode):
        # button up
        letter = lookup(keycode[1], string.ascii_letters, sorted(string.ascii_letters))
        if letter != None:
            self.player.on_button_up(letter)

        spec_char = lookup(keycode[1], string.punctuation, sorted(string.punctuation))
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

class CustomLabel(object):
    """
    Class to encapsulate CoreLabel() and MarkupLabel() for more text editing
    flexibility

    Creates labels for interactivity

    Parameters
    ----------
    text: str
        String representing text you want the texture for
    font_size: int
        Number representing pixel size of text
        Default: 20
    color: tuple(r,g,b,a)
        tuple containing rgba values mapped on scale from 0 to 1
        Default: (1,1,1,1)
    invert_text: bool
        Flag to signify if multi-line text should be displayed from top to bottom or vice versa.
        Original index order of text is preserved
        Default: False (i.e top to bottom) 
    **kwargs: args
        Additional arguments need for more fine control of label placement
        See https://kivy.org/docs/api-kivy.core.text.html
    """
    def __init__(self,text,font_size=20,color=(1,1,1,1),invert_text=False,**kwargs):
        super(CustomLabel, self).__init__()
        if len(color) == 3:
            color = [c for c in color]+[1]
        self.invert_text = invert_text
        self.text_dict = {i:text[i] for i in range(len(text))}
        self.text = self.parse_text(text,invert_text)
        self.label = MarkupLabel(text=self.text,font_size=font_size,color=color,**kwargs)
        self.markup_regex = re.compile("(\[.+\])")
        self.def_regex = re.compile("(\[/*(color(=#\w+)*|b|i)\])")
        
        self.label.refresh()

    def parse_text(self,text,invert):
        fin_txt = ""
        if invert:
            split_txt = text.strip().split("\n")
            split_txt = split_txt[::-1]
            stitched = "\n".join(split_txt)
            return stitched
        else:
            return text
        



    def set_color(self,idx,color):
        """
        Function to change the color of an individual character in the label

        Parameters
        ----------
        idx: int
            Number representing index in string of the char to manipulate
        color: tuple(r,g,b,a)
            tuple containing rgba values mapped on scale from 0 to 1
        """
        hexcolor = colors.to_hex(color,keep_alpha=True)
        old_text = self.text_dict[idx]
        color_regex = re.compile("\[/*color(=#\w+)*\]")
        match = color_regex.match(old_text)
        if match:
            new_text = re.sub('#\w+',hexcolor,old_text)
        else:
            markups = self.markup_regex.split(old_text)
            new_text = ["[color=%s]" % hexcolor] + markups+ ["[/color]"]
            new_text = "".join(new_text)
        self.text_dict[idx] = new_text
        render_text = self.join_text()
        self.label.text = render_text
        self.label.refresh()

    def set_bold(self,idx):
        """
        Function to bold an individual character in the label

        Parameters
        ----------
        idx: int
            Number representing index in string of the char to manipulate
        """
        old_text = self.text_dict[idx]
        bold_regex = re.compile("\[/*b\]")
        match = bold_regex.match(old_text)
        if match:
            new_text = bold_regex.sub("",old_text)
        else:
            markups = self.markup_regex.split(old_text)
            new_text = ["[b]"] + markups+ ["[/b]"]
            new_text = "".join(new_text)
        self.text_dict[idx] = new_text
        render_text = self.join_text()
        self.label.text = render_text
        self.label.refresh()


    def set_italic(self,idx):
        """
        Function to italicize an individual character in the label

        Parameters
        ----------
        idx: int
            Number representing index in string of the char to manipulate
        """
        old_text = self.text_dict[idx]
        italic_regex = re.compile("\[/*i\]")
        match = italic_regex.match(old_text)
        if match:
            new_text = italic_regex.sub("",old_text)
        else:
            markups = self.markup_regex.split(old_text)
            new_text = ["[i]"] + markups+ ["[/i]"]
            new_text = "".join(new_text)
        self.text_dict[idx] = new_text
        render_text = self.join_text()
        self.label.text = render_text
        self.label.refresh()

    def clear_markups(self,idx):
        """
        Function to clear all markups currently affecting a character at idx

        Parameters
        ----------
        idx: int
            Number representing index in string of the char to manipulate
        """
        old_text = self.text_dict[idx]
        match = self.def_regex.match(old_text)
        if match:
            new_text = self.def_regex.sub("",old_text)
            self.text_dict[idx] = new_text
            render_text = self.join_text()
            self.label.text = render_text
            self.label.refresh()

    def clear_all_markups(self):
        """
        Clears all user added markups to the text
        """
        map(self.clear_markups,self.text_dict)

    
    def join_text(self):
        """
        Function to join the values of the text_dict into a single string for rendering
        """
        if not self.invert_text:
            text = "".join(self.text_dict.values())
            return text
        else:
            text = "".join(self.text_dict.values())
            split_txt = text.strip().split("\n")
            split_txt = split_txt[::-1]
            stitched = "\n".join(split_txt)
            return stitched

    @property
    def texture(self):
        return self.label.texture

    



class LyricsPhrase(InstructionGroup):
    def __init__(self,pos,color,text):
        super(LyricsPhrase, self).__init__()
        self.text=text
        self.label = CustomLabel(text, pos=pos,color=color, font_size=50)
        self.current=0
        self.next_avail= text[self.current]
        for i in range(len(text)):
            self.label.set_color(i,color)

        self.rect = Rectangle(size=self.label.texture.size,pos=pos,texture=self.label.texture)
        self.add(self.rect)
        print self.next_avail, "TYPE THIS"






    #Use self.label set_color() function to change color of text at an index 
    def on_hit(self,letter_idx):
        green=(0,1,0,1)
        self.label.set_color(letter_idx,green)
        self.label.set_bold(letter_idx+1)
        self.add(self.rect)
        self.current +=1
        self.next_avail=self.text[self.current]


    

    def on_miss(self,letter_idx):
        red=(1,0,0,1)
        self.label.set_color(letter_idx,red)
        self.add(self.rect)






    # cpos = property(get_cpos, set_cpos)
    # size = property(get_csize, set_csize)


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
        self.lyric= LyricsPhrase((Window.width/3,Window.height/2),(1,1,1),"lyric goes here")
        self.add(self.lyric)

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
        char=char.lower()
        curr_lyric = self.display.lyric
       

        if curr_lyric.next_avail == char:
            self.display.on_button_down(char,True)
            print curr_lyric.current
            self.display.lyric.on_hit(curr_lyric.current)
        else:
           self.display.lyric.on_miss(curr_lyric.current) 


        #self.display.on_button_down(char,False)

    # called by MainWidget
    def on_button_up(self, char):
        self.display.on_button_up(char)
        print self.display.lyric.next_avail, "TYPE THIS"

    # needed to check if for pass gems (ie, went past the slop window)
    def on_update(self):
        self.audio_ctrl.on_update()
        self.display.on_update()

run(MainWidget)
