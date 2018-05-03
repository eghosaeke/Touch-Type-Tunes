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
        
        self.label_text = self.parse_text(text,invert_text)
        self.label = MarkupLabel(text=self.label_text,font_size=font_size,color=color,**kwargs)
        self.markup_regex = re.compile("(\[.+\])")
        self.def_regex = re.compile("(\[/*(color(=#\w+)*|b|i)\])")
        
        self.label.refresh()

    def get_text(self):
        return self.label_text

    def set_text(self,txt):
        print "SETTING NEW TEXT"
        self.text_dict = {i:txt[i] for i in range(len(txt))}
        
        fin_txt = ""
        if self.invert_text:
            split_txt = txt.strip().split("\n")
            split_txt = split_txt[::-1]
            stitched = "\n".join(split_txt)
            fin_txt = stitched
        else:
            fin_txt = txt
        self.label_text = fin_txt
        self.label.text = self.label_text
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
        try:
            hexcolor = colors.to_hex(color,keep_alpha=True)
            old_text = self.text_dict[idx]
            color_regex = re.compile("(\[color=#\w+\])")
            match = color_regex.search(old_text)
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
        except Exception as e:
            print e

    def set_colors(self,color,substr="",start=None,end=None):

        if substr:
            start = self.text.find(substr)
            if start != -1:
                end = start + len(substr)
                for idx in range(start,end):
                    self.set_color(idx,color)
        else:
            if start and end:
                for idx in range(start,end):
                    self.set_color(idx,color)
            elif start:
                for idx in range(start,len(self.text)):
                    self.set_color(idx,color)


    def set_bold(self,idx):
        """
        Function to bold an individual character in the label

        Parameters
        ----------
        idx: int
            Number representing index in string of the char to manipulate
        """
        try:
            old_text = self.text_dict[idx]
            bold_regex = re.compile("\[/*b\]")
            match = bold_regex.search(old_text)
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
        except Exception as e:
            print e


    def set_italic(self,idx):
        """
        Function to italicize an individual character in the label

        Parameters
        ----------
        idx: int
            Number representing index in string of the char to manipulate
        """
        try:
            old_text = self.text_dict[idx]
            italic_regex = re.compile("\[/*i\]")
            match = italic_regex.search(old_text)
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
        except Exception as e:
            print e

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

    text = property(get_text,set_text)

    @property
    def texture(self):
        return self.label.texture

class BasicLabel(InstructionGroup):
    def __init__(self,text,**kwargs):
        super(BasicLabel, self).__init__()
        self.label = CustomLabel(text,**kwargs)
        if kwargs.has_key('tpos'):
            self.tpos = kwargs['tpos']
        elif kwargs.has_key('pos'):
            self.pos = kwargs['pos']
            self.pos = np.array(self.pos, dtype=np.float)
        self.label_text = text
        self.rect = Rectangle(size=self.label.texture.size,pos=self.pos,texture=self.label.texture)
        self.add(self.rect)

    def get_text(self):
        return self.label_text

    def set_text(self,txt):
        self.label.text = txt
        self.rect.size = self.label.texture.size
        self.rect.texture = self.label.texture
        self.label_text = txt

    def get_tpos(self):
        return (self.pos[0], self.pos[1] + self.size[1])

    def set_tpos(self, p):
        self.pos = (p[0], p[1] - self.size[1])

    @property
    def size(self):
        return self.label.texture.size
    text = property(get_text,set_text)
    tpos = property(get_tpos, set_tpos)

