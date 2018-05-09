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

import random
import numpy as np
import bisect
import string
import matplotlib.colors as colors
from colorsys import hsv_to_rgb
from collections import deque, OrderedDict
import re
import textwrap
from customlabel import BasicLabel, CustomLabel
from random import random, randint,choice



if os.name == "nt": 
    font_path = "C:\\Windows\\Fonts"
elif os.name == "mac" or os.name == "posix":
    font_paths = ["/System/Library/Fonts","Library/Fonts"]

def score_label():
    if platform == "macosx":        
        font_name= "Comic Sans MS"
    elif platform == "win":
        font_name = "comic"
    else:
        font_name = ""

    l = BasicLabel("Score",tpos=(Window.width*0.8, 590),font_size=35,font_name=font_name)
    return l



def improv_label(text,tpos):
    if platform == "macosx":        
        font_name= "Comic Sans MS"
    elif platform == "win":
        font_name = "comic"
    else:
        font_name = ""
    l = BasicLabel(text,tpos=tpos,font_size=35,font_name=font_name)
    return l 

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

class MainWidget(BaseWidget):
    def __init__(self):
        super(MainWidget, self).__init__()
        self.song = 'Stems/Fetish'
        self.audio_cont = AudioController(self.song,improv_cb=self.improv_cb)
        self.gem_data = SongData()
        self.gem_data.read_data('Stems/Fetish-selected-milestone2.txt')
        self.gem_data.get_phrases()
        
        #Improv stuff
        self.loopFilepath = 'Stems/improv/Fetish-improv-loops.txt'
        self.markFilepath = 'Stems/improv/Fetish-improv-marks.txt'
        self.markRegionPath = 'Stems/improv/Fetish-improv-marks-regions.txt'
        
        #Loop = (Lyric, startTime, duration)
        #Mark  = Lyric: (startTime, endTime)
        self.loops, self.marks = self.gem_data.read_improv(self.loopFilepath, self.markFilepath)
        self.bgImprovBuffers = make_wave_buffers(self.loopFilepath, self.song + '_inst.wav') 
        self.vocalImprovBuffers = make_wave_buffers(self.markRegionPath, self.song + '_vocals.wav')
        self.marksHit = []
        
        self.improv = False 
        self.beat_disp = BeatMatchDisplay(self.gem_data)
        self.improv_disp = ImprovDisplay(self.vocalImprovBuffers,self.audio_cont.play_buf)
        with self.canvas.before:
        #     # ADD BACKGROUND IMAGE TO GAME
            self.bg_img = Rectangle(size=self.size,pos = self.pos,source="mic-booth.jpg")
            Color(0, 0, 0, 0.3)
            self.sidebar = Rectangle(size = self.size ,pos =self.pos)

        self.bind(pos=self.update_bg)
        self.bind(size=self.update_bg)


        self.canvas.add(Color(1,1,1,0.8))
        self.canvas.add(self.beat_disp)
        self.canvas.add(self.improv_disp)
        self.score_label = score_label()
        self.canvas.add(self.score_label)
        self.info = system_info_label()
        self.canvas.add(self.info)
        self.player = Player(self.gem_data,self.beat_disp,self.improv_disp,self.audio_cont)
        self.caps_on = False
        
        # test_text = "HELLO WOLRD"
        # test_text += "\nFinal Score: "+"{:,}".format(65464163)
        # test_text += "\nLongest Streak: "+"{:,}".format(5264)
        # test_text += "\nAccuracy: "+"{0:.2f}".format(0.65654*100)+"%"
        # test_text += "\n\nPress 'r' to restart the game"
        # self.hello = BasicLabel(test_text,tpos=(0,600),font_size=50,invert_text=False,font_name="DejaVuSans")
        # self.hello = CustomLabel(test_text,font_size=40,font_name="DejaVuSans")
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
    def update_bg(self, *args):
        self.bg_img.pos = self.pos
        self.bg_img.size = self.size
        self.sidebar.size=[float(self.size[0])/2,self.size[1]]

        
    def on_key_down(self, keycode, modifiers):
        # print 'key-down', keycode, modifiers

        if keycode[1] == 'capslock':
            self.caps_on = not self.caps_on

        if keycode[1] == 'tab':
            # self.hello.text += "\nHello World Again!"
            self.hello.set_font(6,"comic")
            
            self.rect.texture = self.hello.texture
        # play / pause toggle
        if keycode[1] == 'enter':
            if "shift" in modifiers:
                self.player.toggle_game()
            elif "ctrl" in modifiers:
                self.improv = False
                self.player.improv = False
                self.beat_disp.improv = False
                self.audio_cont.improv = False
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

    def on_update(self) :
        if kivyClock.get_fps() > 40:
            self.player.on_update()
            
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
        self.score_label.text = "Score"
        self.score_label.text += "\n"+"{:,}".format(self.player.word_hits)
        

        #make sure improv mode stays updated. TODO: Find out which part of the game is keeping track of improv mode. Depends on how we trigger it...
        # self.improv = self.player.improv


# creates the Audio driver
# creates a song and loads it with solo and bg audio tracks
# creates snippets for audio sound fx
class AudioController(object):
    def __init__(self, song_path,improv_cb=None,listener=None):
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

    def start(self):
        if self.mixer.contains(self.bg_gen) or self.mixer.contains(self.improv_sect):
            """
            Needed to restart game
            """
            self.mixer.remove_all()
            self.bg_audio = WaveFile(self.song_path+'_inst_1.wav')
            self.solo_audio = WaveFile(self.song_path+'_vocals_1.wav')
            self.last_part = False
        self.bg_gen = WaveGenerator(self.bg_audio)
        self.solo_gen = WaveGenerator(self.solo_audio)
        self.bg_gen.set_gain(0.5)
        self.solo_gen.set_gain(0.5)
        self.mixer.add(self.bg_gen)
        self.mixer.add(self.solo_gen)
        self.game_paused = False
        self.game_started = True

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
            
            #Don't put the improv words on display
            if '\/' in word:
                #TODO: 
                continue
            
            if "." not in text:
                if '*' in text:
                    # phrase+= text[:-1]+"_"
                    phrase+= text[:-1]+" "

                    # phrase_to_type += text[:-1]+"_"
                    phrase_to_type += text[:-1]+" "
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
                    self.phrases_dict[phrase] = (phrase_to_type,start_time,end_time)
                    self.phrases.append((phrase,phrase_to_type,start_time,end_time))
                    phrase = ""
                    phrase_to_type=""
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
    def __init__(self,pos,color,text,start_t,end_t,vel,point_cb,interactive=False):
        super(LyricsWord, self).__init__()
        self.text = text
        self.interactive = interactive
        self.end_of_lyric = False
        self.pos = np.array(pos, dtype=np.float)
        self.point_cb = point_cb
        if platform == "win":
            self.label = CustomLabel(text,color=color,halign=None,invert_text=True, font_size=40,font_name="comic")
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
        self.added_lyric = False
        self.on_screen = False
        # print "text to type: ",text_to_type
        # print "text: ",text
        if self.interactive:
            self.label.set_colors((0,.87,1,1),text)
        # for i in range(len(self.label.text)):
        #     self.label.set_colors((0,0,0,0),"_")

        self.rect = Rectangle(size=self.label.texture.size,pos=pos,texture=self.label.texture)


    #Use self.label set_color() function to change color of text at an index 
    def on_hit(self):

        green=(0,1,0,1)
        self.label.set_color(self.current,green)
        self.label.set_bold(self.current+1)
        new_text = self.label.texture
        self.rect.texture = new_text
        # self.add(self.rect)
        self.current += 1
        try:
            self.next_avail=self.text[self.current]
            self.end_of_lyric=False
            if self.next_avail == " ":
                self.point_cb()
            return False
        except Exception as e:
            self.end_of_lyric=True
            return True
#            print e
#            print "END OF LYRIC"


    

    def on_miss(self):
        red=(1,0,0,1)
        self.label.set_color(self.current,red)

    def on_update(self,dt):
        self.time += dt
        epsilon = (self.start_time-self.time)
        if epsilon < 0.01:
            if not self.added_lyric:
                self.add(self.rect)
                self.added_lyric = True
            self.pos[1] += self.vel * dt
            self.rect.pos = self.pos

        if self.pos[1] < Window.height - self.rect.size[1]/2.0:
            self.on_screen = True

        return self.time < self.end_time


class LyricsPhrase(InstructionGroup):
    def __init__(self,pos,color,text,text_to_type,start_t,end_t,queue_cb,point_cb):
        super(LyricsPhrase, self).__init__()
        self.text=text
        self.text_to_type=text_to_type
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
        self.create_phrases()
        self.num_words = len(self.word_deque)
        # print "len of interactive: ",self.num_words
        # print "interactive in phrase: ",self.word_deque
        self.current_word = self.word_deque[0]
        self.time = 0
        self.queue_cb = queue_cb
        
        self.added_lyric = False
        self.on_screen = False
        # print "text to type: ",text_to_type
        # print "text: ",text
        # for i in range(len(self.label.text)):
        #     self.label.set_colors((0,0,0,0),"_")

        self.add(self.objects)


    def create_phrases(self):
        wrapped_text = wrap_text(self.text,17,self.text_size[0])
        phrases = self.text.split(self.text_to_type)
        lines = wrapped_text.split("\n")
        # print "phrases: ",phrases
        # print "lines: ",lines
        if len(lines) == 1:
            phrases.insert(1,self.text_to_type)
            size = (0,0)
            prev_pos = self.pos
            for phrase in phrases:
                if phrase != '':
                    interactive = phrase == self.text_to_type
                    pos = (prev_pos[0]+size[0],prev_pos[1])
                    word = LyricsWord(pos,self.color,phrase,self.start_time,self.end_time,self.vel,self.point_cb,interactive=interactive)
                    prev_pos = pos
                    size = word.label.texture.size
                    self.objects.add(word)
                    if interactive:
                        # print "word from og: ",phrase
                        # print "ADDING TEXT TO TYPE ",phrase
                        self.word_deque.append(word)
        else:
            i = 0
            size = [0,0]
            prev_size = [0,0]
            prev_pos = self.pos
            for l in range(len(lines)):
                line = lines[l]
                try:
                    words = line.split(phrases[i])
                    # print "split words: ",words
                    split_work = True
                except:
                    words = [line]
                    # print "split word except: ",words
                    split_work = False


                prev_pos = (self.pos[0],self.pos[1]+size[1])
                size = [0,0]
                for w in range(len(words)):
                    word = words[w]
                    # print "word: ",word
                    if len(words) == 1 or (len(words) > 1 and word != ''):
                        # print "split didn't work ",i
                        ty_check = word.split(self.text_to_type)
                        if all([x=='' for x in ty_check]):
                            interactive = True

                            # phrase = self.text_to_type
                            int_phrases = self.text_to_type.split(" ")
                            for p in range(len(int_phrases)):
                                phrase = int_phrases[p]
                                if p != len(int_phrases) - 1:
                                    phrase += " " 
                                pos = (prev_pos[0]+size[0],prev_pos[1])
                                lword = LyricsWord(pos,self.color,phrase,self.start_time,self.end_time,self.vel,self.point_cb,interactive=interactive)
                                prev_pos = pos
                                size = lword.label.texture.size
                                self.objects.add(lword)
                                if interactive:
                                    # print "word from 1: ",word
                                    # print "ADDING TEXT TO TYPE ",phrase
                                    self.word_deque.append(lword)
                        else:
                            # print "Ty_check not all empty: ",ty_check
                            end_line = False
                            for ty in ty_check:
                                if ty == '':
                                    phrase = self.text_to_type
                                else:
                                    phrase = ty

                                interactive = phrase == self.text_to_type
                                if len(ty_check) == 1:
                                    interactive = phrase in self.text_to_type
                                    if interactive and w == len(words)-1:
                                        # print "adding end of line space"
                                        phrase += " "
                                        end_line = True
                                if interactive:
                                    int_phrases = phrase.strip().split(" ")
                                    for p in range(len(int_phrases)):
                                        phrase = int_phrases[p]
                                        if p != len(int_phrases) - 1 or end_line:
                                            phrase += " "
                                        pos = (prev_pos[0]+size[0],prev_pos[1])
                                        lword = LyricsWord(pos,self.color,phrase,self.start_time,self.end_time,self.vel,self.point_cb,interactive=interactive)
                                        prev_pos = pos
                                        size = lword.label.texture.size
                                        self.objects.add(lword)
                                        if interactive:
                                            # print "word from 2: ",word
                                            # print "ADDING TEXT TO TYPE ",phrase
                                            self.word_deque.append(lword)
                                else:
                                    pos = (prev_pos[0]+size[0],prev_pos[1])
                                    lword = LyricsWord(pos,self.color,phrase,self.start_time,self.end_time,self.vel,self.point_cb,interactive=interactive)
                                    prev_pos = pos
                                    size = lword.label.texture.size
                                    self.objects.add(lword)
                        # phrase = word
                        # interactive = phrase == self.text_to_type
                        i = min(i+1,len(phrases)-1)
                        # print "phrase[i]=%s" % phrases[i]
                        # pos = (prev_pos[0]+size[0],prev_pos[1])
                        # lword = LyricsWord(pos,self.color,phrase,self.start_time,self.end_time,self.vel,interactive=interactive)
                        # prev_pos = pos
                        # size = lword.label.texture.size
                        # self.objects.add(lword)
                        # if interactive:
                        #         print "ADDING TEXT TO TYPE ",phrase
                        #         self.word_deque.append(lword)
                    else:
                        if word == '':
                            interactive = False
                            phrase = phrases[i]
                            i = min(i+1,len(phrases)-1)
                            pos = (prev_pos[0]+size[0],prev_pos[1])
                            lword = LyricsWord(pos,self.color,phrase,self.start_time,self.end_time,self.vel,self.point_cb,interactive=interactive)
                            prev_pos = pos
                            size = lword.label.texture.size
                            self.objects.add(lword)
                        # else:
                        #     ty_check = word.split(self.text_to_type)
                        #     if all([x=='' for x in ty_check]):
                        #         interactive = True

                        #         phrase = self.text_to_type
                        #         int_phrases = phrase.split(" ")
                        #         for p in range(len(int_phrases)):
                        #             phrase = int_phrases[p]
                        #             if p != len(int_phrases) - 1:
                        #                     phrase += " "
                        #             pos = (prev_pos[0]+size[0],prev_pos[1])
                        #             lword = LyricsWord(pos,self.color,phrase,self.start_time,self.end_time,self.vel,self.point_cb,interactive=interactive)
                        #             prev_pos = pos
                        #             size = lword.label.texture.size
                        #             self.objects.add(lword)
                        #             if interactive:
                        #                 # print "word from 3: ",word
                        #                 # print "ADDING TEXT TO TYPE ",phrase
                        #                 self.word_deque.append(lword)
                        #     else:
                        #         # print "Ty_check not all empty: ",ty_check
                        #         end_line = False
                        #         for ty in ty_check:
                        #             if ty == '':
                        #                 phrase = self.text_to_type
                        #             else:
                        #                 phrase = ty

                        #             interactive = phrase == self.text_to_type
                        #             if len(ty_check) == 1:
                        #                 interactive = phrase in self.text_to_type
                        #                 if interactive and w == len(words)-1:
                        #                     # print "adding end of line space"
                        #                     phrase += " "
                        #                     end_line = True
                        #             if interactive:
                        #                 int_phrases = phrase.strip().split(" ")
                        #                 for p in range(len(int_phrases)):
                        #                     phrase = int_phrases[p]
                        #                     if p != len(int_phrases) - 1 or end_line:
                        #                         phrase += " "
                        #                     pos = (prev_pos[0]+size[0],prev_pos[1])
                        #                     lword = LyricsWord(pos,self.color,phrase,self.start_time,self.end_time,self.vel,self.point_cb,interactive=interactive)
                        #                     prev_pos = pos
                        #                     size = lword.label.texture.size
                        #                     self.objects.add(lword)
                        #                     if interactive:
                        #                         # print "word from 4: ",word
                        #                         # print "ADDING TEXT TO TYPE ",phrase
                        #                         self.word_deque.append(lword)
                        #             else:
                        #                 pos = (prev_pos[0]+size[0],prev_pos[1])
                        #                 lword = LyricsWord(pos,self.color,phrase,self.start_time,self.end_time,self.vel,self.point_cb,interactive=interactive)
                        #                 prev_pos = pos
                        #                 size = lword.label.texture.size
                        #                 self.objects.add(lword)




    #Use self.label set_color() function to change color of text at an index 
    def on_hit(self,char):
        green=(0,1,0,1)
        if self.current_word.next_avail == char:
            end = self.current_word.on_hit()
            if end:
                self.word_deque.popleft()
                if len(self.word_deque) > 0:
                    self.current_word = self.word_deque[0]
        # self.add(self.rect)
        if len(self.word_deque) == 0:
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
        # epsilon = (self.start_time-self.time)
        # if epsilon < 0.01:
        #     if not self.added_lyric:
        #         self.add(self.rect)
        #         self.added_lyric = True
        
        self.objects.on_update()
        if any([x.on_screen for x in self.objects.objects]):
            self.on_screen = True
        
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
        if self.np_tpos[1] > Window.height:
            self.vel[1] = -self.vel[1]
            self.np_tpos[1] = Window.height
        #collision with left wall
        if self.np_tpos[0] < 0:
            self.vel[0] = -self.vel[0]
            self.np_tpos[0] = 0
        #collision with right wall
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
    def __init__(self,phrases,audio_cb=None):
        super(ImprovDisplay, self).__init__()
        self.phrases = phrases
        self.objects = AnimGroup()
        self.improv_word = ""
        self.user_input = BasicLabel("",tpos=(400,300),color=(0,1,0,1),font_size=35)
        self.improvise = BasicLabel("Improvise!!!",tpos=(150,550),font_size=50)
        self.improv_labels = []
        self.audio_cb = audio_cb
        self.letter_buf = OrderedDict()
        
    def start(self):
        self.add(self.user_input)
        self.add(self.improvise)
        self.add(self.objects)
        self.create_hit_dict(self.phrases.keys())
        tpos = [(100,400),(100,350),(100,300),(100,250)]
        i = 0
        for phrase in self.phrases:
            letter_to_hit = self.letter_buf.keys()[i]
            improv_label = ImprovPhrase(phrase,letter_to_hit,tpos[i],(1,1,1))
            self.objects.add(improv_label)
            self.improv_labels.append(improv_label)
            i += 1

    def restart(self):
        self.remove(self.user_input)
        self.remove(self.improvise)
        self.remove(self.objects)
        self.objects = AnimGroup()
        self.improv_labels = []
        self.improv_word = ""

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


    def on_hit(self,char):
        buf = self.letter_buf.get(char,None)
        if buf and self.audio_cb:
            self.audio_cb(buf)
        self.improv_word = ""
        self.user_input.text = ""

    def on_update(self):
        self.objects.on_update()



# Displays and controls all game elements: Nowbar, Buttons, BarLines, Gems.
class BeatMatchDisplay(InstructionGroup):
    def __init__(self, gem_data):
        super(BeatMatchDisplay, self).__init__()
        self.start_pos = (20,Window.height+10)
        self.gem_data = gem_data
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

    def start(self):
        phrases = self.gem_data.get_phrases_in_order()
        # print phrases
        for data in phrases:
            phrase,phrase_to_type,start,end = data
            # print "phrase to type: ",phrase_to_type
            lyric = LyricsPhrase(self.start_pos,(1,1,1),phrase,phrase_to_type,start,end,self.pop_lyric,self.add_points)
            self.objects.add(lyric)
            self.lyrics_deque.append(lyric)
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
            self.start()

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
        self.score += 100
        if end:
            print "curr score: ",self.score
            print "num words: ",self.curr_lyric.num_words
            self.score += 100*self.curr_lyric.num_words
            print "new score: ",self.score
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

    # call every frame to make gems and barlines flow down the screen
    def on_update(self) :
        if not self.game_paused and not self.improv:
            self.objects.on_update()
        



# Handles game logic and keeps score.
# Controls the display and the audio
class Player(object):
    def __init__(self, gem_data, display, improv_display, audio_ctrl):
        super(Player, self).__init__()
        self.game_started = False
        self.game_paused = True
        self.audio_ctrl = audio_ctrl
        self.display = display
        self.improv_display = improv_display
        self.gem_data = gem_data
        # self.word_hits = 0
        self.gem_misses = 0
        self.longest_streak = 0
        self.improv = False
        


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
        self.audio_ctrl.start()
        self.improv_display.restart()
        # self.word_hits = 0
        self.longest_streak = 0
        self.game_paused = False


    # called by MainWidget
    def on_button_down(self, char):
        if not self.game_paused and not self.improv:
            curr_lyric = self.display.curr_lyric
            if curr_lyric.on_screen:
#                print curr_lyric.next_avail
                hit = self.display.letter_hit(char)
                if hit:
                    self.audio_ctrl.set_mute(False)
                # if curr_lyric.next_avail == " " or curr_lyric.end_of_lyric==True:
                #     self.word_hits+=100
                #     # print self.word_hits, "SCORE"

                else:
                   self.audio_ctrl.play_sfx()
                   self.audio_ctrl.set_mute(True)

        elif not self.game_paused and self.improv:
                self.improv_display.on_hit(char)
    @property
    def word_hits(self):
        return self.display.score
        #self.display.on_button_down(char,False)

    # called by MainWidget
    def on_button_up(self, char):
        if not self.game_paused and not self.improv:
            self.display.on_button_up(char)

    # needed to check if for pass gems (ie, went past the slop window)
    def on_update(self):
        self.audio_ctrl.on_update()
        self.display.on_update()
        if self.improv:
            self.improv_display.on_update()

run(MainWidget)
