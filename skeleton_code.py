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
from kivy.graphics import PushMatrix, PopMatrix, Translate, Scale, Rotate
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
from customlabel import BasicLabel, CustomLabel



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
        self.audio_cont = AudioController(self.song)
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
        with self.canvas.before:
        #     # ADD BACKGROUND IMAGE TO GAME
            self.bg_img = Rectangle(size=self.size,pos = self.pos,source="mic-booth.jpg")
            Color(0, 0, 0, 0.3)
            self.sidebar = Rectangle(size = self.size ,pos =self.pos)

        self.bind(pos=self.update_bg)
        self.bind(size=self.update_bg)


        self.canvas.add(Color(1,1,1,0.8))
        self.canvas.add(self.beat_disp)
        self.score_label = score_label()
        self.canvas.add(self.score_label)
        self.info = system_info_label()
        self.canvas.add(self.info)
        self.player = Player(self.gem_data,self.beat_disp,self.audio_cont)

        self.caps_on = False
        # test_text = "HELLO WOLRD"
        # test_text += "\nFinal Score: "+"{:,}".format(65464163)
        # test_text += "\nLongest Streak: "+"{:,}".format(5264)
        # test_text += "\nAccuracy: "+"{0:.2f}".format(0.65654*100)+"%"
        # test_text += "\n\nPress 'r' to restart the game"
        # self.hello = BasicLabel(test_text,tpos=(0,600),font_size=50,invert_text=False,font_name="DejaVuSans")
        # # self.hello.set_color(6,(0,1,0))
        # # # self.hello.set_bold(0)
        # # self.hello.set_color(6,(0,0,1))
        # # self.hello.set_bold(6)
        # # self.hello.set_italic(6)
        # # for i in range(5):
        # #     self.hello.set_color(i,(0,1,0))
        # # self.rect = Rectangle(size=self.hello.texture.size,pos=(50,50),texture=self.hello.texture)
        # # self.canvas.add(self.rect)
        # self.canvas.add(self.hello)
    def update_bg(self, *args):
        self.bg_img.pos = self.pos
        self.bg_img.size = self.size
        self.sidebar.size=[float(self.size[0])/2,self.size[1]]

        
    def on_key_down(self, keycode, modifiers):
        # print 'key-down', keycode, modifiers

        if keycode[1] == 'capslock':
            self.caps_on = not self.caps_on

        # if keycode[1] == 'tab':
        #     # self.hello.text += "\nHello World Again!"
        #     print "prev tpos: ", self.info.tpos
        #     self.info.tpos = (self.info.tpos[0],self.info.tpos[1]-20)
        #     print "new tpos: ", self.info.tpos
        # play / pause toggle
        if keycode[1] == 'enter':
            if "shift" in modifiers:
                self.player.toggle_game()
            elif "ctrl" in modifiers:
                self.player.restart_game()

        #pass spacebar values to player as " "
        if keycode[1] == 'spacebar':
            # self.player.on_button_down("_")
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
            

    def on_update(self) :
        if kivyClock.get_fps() > 40:
            self.player.on_update()
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
        self.miss_sfx = WaveFile("miss2.wav")
        self.miss_sfx_gen= WaveGenerator(self.miss_sfx)
        self.bg_gen = WaveGenerator(self.bg_audio)
        self.solo_gen = WaveGenerator(self.solo_audio)
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
        # miss_sfx = WaveFile("miss1.wav")
        # miss_sfx_gen = WaveGenerator(self.miss_sfx)
        # miss_sfx_gen.set_gain(.3)
        print len(self.mixer.generators)
        if self.mixer.contains(self.miss_sfx_gen):
            self.miss_sfx_gen.reset()
            self.miss_sfx_gen.play()
        else:
            self.mixer.add(self.miss_sfx_gen)
            self.miss_sfx_gen.reset()
            self.miss_sfx_gen.play()

    def set_listener(self,listen_cb):
        self.audio.listen_func = listen_cb

    # needed to update audio
    def on_update(self):
        self.audio.on_update()


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
            if '\\' in word:
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
        

class LyricsPhrase(InstructionGroup):
    def __init__(self,pos,color,text,text_to_type,start_t,end_t,queue_cb):
        super(LyricsPhrase, self).__init__()
        self.text=text
        self.text_to_type=text_to_type
        self.end_of_lyric=False

        self.pos = np.array(pos, dtype=np.float)
        # text_size = (Window.width-pos[0],None)
        if platform == "win":
            self.label = CustomLabel(text,color=color, font_size=40,font_name="comic")
        elif platform == "macosx":
            self.label = CustomLabel(text,color=color, font_size=40,font_name="Microsoft Sans Serif")
        else:
            self.label = CustomLabel(text,color=color, font_size=40)
        self.current=self.text.find(text_to_type)
        self.next_avail = self.text[self.current]
        self.start_time = start_t
        self.end_time = end_t
        self.scroll_t = self.end_time - self.start_time
        # self.scroll_t = 25
        self.vel = -self.pos[1]/self.scroll_t
        self.time = 0
        self.queue_cb = queue_cb
        self.added_lyric = False
        self.on_screen = False
        # print "text to type: ",text_to_type
        # print "text: ",text
        self.label.set_colors((0,.87,1,1),text_to_type)
        # for i in range(len(self.label.text)):
        #     self.label.set_colors((0,0,0,0),"_")

        self.rect = Rectangle(size=self.label.texture.size,pos=pos,texture=self.label.texture)






    #Use self.label set_color() function to change color of text at an index 
    def on_hit(self,letter_idx):
        green=(0,1,0,1)
        self.label.set_color(letter_idx,green)
        self.label.set_bold(letter_idx+1)
        new_text = self.label.texture
        self.rect.texture = new_text
        # self.add(self.rect)
        self.current += 1
        try:
            self.next_avail=self.text[self.current]
            self.end_of_lyric=False
        except Exception as e:
            self.end_of_lyric=True
            print e
            print "END OF LYRIC"


    

    def on_miss(self,letter_idx):
        red=(1,0,0,1)
        self.label.set_color(letter_idx,red)
        # self.add(self.rect)

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
        if self.time > self.end_time:
            self.queue_cb()
        # if self.pos[1] < 0:
        #     self.queue_cb()

        return self.time < self.end_time
        # return self.pos[1] > 0




    # cpos = property(get_cpos, set_cpos)
    # size = property(get_csize, set_csize)


# Displays and controls all game elements: Nowbar, Buttons, BarLines, Gems.
class BeatMatchDisplay(InstructionGroup):
    def __init__(self, gem_data):
        super(BeatMatchDisplay, self).__init__()
        self.start_pos = (50,Window.height+50)
        self.gem_data = gem_data
        self.objects = AnimGroup()
        self.add(self.objects)
        self.game_paused = True
        self.game_started = False
        self.lyrics_deque = deque()

    def start(self):
        phrases = self.gem_data.get_phrases_in_order()
        # print phrases
        for data in phrases:
            phrase,phrase_to_type,start,end = data
            # print "phrase to type: ",phrase_to_type
            lyric = LyricsPhrase(self.start_pos,(1,1,1),phrase,phrase_to_type,start,end,self.pop_lyric)
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
            self.start()

    def toggle(self):
        self.game_paused = not self.game_paused
        
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

    def pop_lyric(self):
        self.lyrics_deque.popleft()
        if len(self.lyrics_deque) != 0:
            self.curr_lyric = self.lyrics_deque[0]

    # call every frame to make gems and barlines flow down the screen
    def on_update(self) :
        if not self.game_paused:
            self.objects.on_update()
        



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
        self.word_hits = 0
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

    def restart_game(self):
        self.display.restart()
        self.audio_ctrl.start()
        self.word_hits = 0
        self.longest_streak = 0


    # called by MainWidget
    def on_button_down(self, char):
        if not self.game_paused:
            curr_lyric = self.display.curr_lyric
            if curr_lyric.on_screen:
                print curr_lyric.next_avail
                if curr_lyric.next_avail == char:
                    self.display.on_button_down(char,True)
                    self.display.curr_lyric.on_hit(curr_lyric.current)
                    self.audio_ctrl.set_mute(False)
                    if curr_lyric.next_avail == " " or curr_lyric.end_of_lyric==True:
                        self.word_hits+=100
                        # print self.word_hits, "SCORE"

                else:
                   self.display.curr_lyric.on_miss(curr_lyric.current) 
                   print 'miss'
                   self.audio_ctrl.play_sfx()
                   self.audio_ctrl.set_mute(True)
                   


        #self.display.on_button_down(char,False)

    # called by MainWidget
    def on_button_up(self, char):
        if not self.game_paused:
            self.display.on_button_up(char)

    # needed to check if for pass gems (ie, went past the slop window)
    def on_update(self):
        self.audio_ctrl.on_update()
        self.display.on_update()

run(MainWidget)
