#####################################################################
#
# customlabel.py
#
# written by: Eghosa Eke
#
#####################################################################
from kivy.graphics.instructions import InstructionGroup
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.core.text.markup import MarkupLabel
from kivy.utils import get_hex_from_color as to_hex
from kivy.core.window import Window
import re
import numpy as np
from copy import deepcopy
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
        self.color = color
        self.invert_text = invert_text
        self.text_dict = {i:text[i] for i in range(len(text))}
        self.og_text = text
        self._font_size = font_size
        self.kwargs = kwargs
        self.label_text = self.parse_text(text,invert_text)
        self.label = MarkupLabel(text=self.label_text,font_size=font_size,color=color,**kwargs)
        self.markup_regex = re.compile("(\[.+\])")
        self.def_regex = re.compile("(\[/*(color(=#\w+)*|b|i)\])")
        
        self.label.refresh()

    def copy(self):
        new_label = CustomLabel(self.og_text,self._font_size,self.color,invert_text=self.invert_text,**self.kwargs)
        new_label.text_dict = self.text_dict
        new_label.text = self.join_text()
        return new_label

    # Get the current text of the label
    def get_text(self):
        return self.label_text


    # setter method for text of the label. Allows for dynamic changes to the label
    def set_text(self,txt):
        self.text_dict = {i:txt[i] for i in range(len(txt))}
        fin_txt = self.parse_text(txt,self.invert_text)
        self.label_text = fin_txt
        self.label.text = self.label_text
        self.label.refresh()

    # Parse text into vertically inverted or non-inverted format for interfacing
    def parse_text(self,text,invert):
        fin_txt = ""
        if invert:
            split_txt = text.split("\n")
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
            hexcolor = to_hex(color)
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
#            print e
            pass


    def set_colors(self,color,substr="",start=None,end=None):
        """
        Function to set the color of multiple characters matching a specific substring
        or from a start to end index

        Parameters:
        -----------
        color: tuple(r,g,b,a)
            tuple containing rgba values mapped on scale from 0 to 1
        substr: string
            String representing substring of text to color
            Default: ""
        start: int
            Number representing start index to set color for
            Default: None
        end: int
            Number representing end index for setting             Default: None
        """
        if substr:
            og_text = self.og_text.replace("\n", " ")
            start = og_text.find(substr)
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
            elif end:
                print "here!"
                for idx in range(end):
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
#            print e
            pass


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
#            print e
            pass

    def set_size(self,idx,fsize,start=True,end=True):
        """
        Function to change the color of an individual character in the label

        Parameters
        ----------
        idx: int
            Number representing index in string of the char to manipulate
        fsize: int
            Number representing font size of character
        """
        try:
            old_text = self.text_dict[idx]
            if start:
                size_regex = re.compile("(\[size=\d+\])")
            else:
                size_regex = re.compile("(\[/size\])")
            match = size_regex.search(old_text)
            if match:
                if start:
                    new_text = re.sub('=\d+',"="+str(fsize),old_text)
            else:
                markups = self.markup_regex.split(old_text)
                if start and end:
                    new_text = ["[size=%d]" % fsize] + markups + ["[/size]"]
                elif start:
                    new_text = ["[size=%d]" % fsize] + markups
                elif end:
                    new_text = markups + ["[/size]"]
                new_text = "".join(new_text)
            self.text_dict[idx] = new_text
            render_text = self.join_text()
            self.label.text = render_text
            self.label.refresh()
        except Exception as e:
#            print e
            pass
    def set_font(self,idx,font):
        """
        Function to change the color of an individual character in the label

        Parameters
        ----------
        idx: int
            Number representing index in string of the char to manipulate
        font: string
            String representing font name to set the character to
                **Will not work if font isn't available for your operating system**
        """
        try:
            old_text = self.text_dict[idx]
            font_regex = re.compile("(\[font=\d\])")
            match = font_regex.search(old_text)
            if match:
                new_text = re.sub('\d',font,old_text)
            else:
                markups = self.markup_regex.split(old_text)
                new_text = ["[font=%s]" % font] + markups+ ["[/font]"]
                new_text = "".join(new_text)
            self.text_dict[idx] = new_text
            render_text = self.join_text()
            self.label.text = render_text
            self.label.refresh()
        except Exception as e:
#            print e
            pass

    def get_fontsize(self):
        return self._font_size

    def set_fontsize(self,f):
        low,high = min(self.text_dict),max(self.text_dict)
        self.set_size(low,f,start=True,end=False)
        self.set_size(high,f,start=False,end=True)
        self._font_size = f
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

    text = property(get_text,set_text)
    font_size = property(get_fontsize,set_fontsize)

    @property
    def texture(self):
        return self.label.texture

class BasicLabel(InstructionGroup):
    """
    Class to provide simple Label functionalilty

    Parameters
    ----------
    text: str
        String representing text you want the texture for
    tpos: tuple(float,float)
        Tuple representing x,y coordinates of the topleft corner of label in pixel-space
    **kwargs: args
        Additional arguments need for more fine control of label placement
        See CustomLabel for additional details
        See https://kivy.org/docs/api-kivy.core.text.html
    """
    def __init__(self,text,tpos,**kwargs):
        super(BasicLabel, self).__init__()
        self.og_pos = tpos
        self.label = CustomLabel(text,**kwargs)
        self.rect = Rectangle(size=self.label.texture.size,pos=self.og_pos,texture=self.label.texture)
        self.max_size = self.label.texture.size
        self.tpos = tpos
        self.label_text = text
        self.add(self.rect)

    # Get the text associated with this label
    def get_text(self):
        return self.label_text

    # setter method for text of the label. Allows for dynamic changes to the label
    def set_text(self,txt):
        self.label.text = txt
        self.rect.size = self.label.texture.size
        self.rect.texture = self.label.texture
        self.tpos = self.og_pos
        self.rect.pos = self.pos
        self.label_text = txt

    # Get the current topleft corner pos of label
    def get_tpos(self):
        return (self.pos[0], self.pos[1] + self.size[1])

    # setter method for tpos of label. Allows for dynamic changes to the label
    def set_tpos(self, p):
        if isinstance(p,np.ndarray):
            p = tuple(p.tolist())
        self.pos = (p[0], p[1] - self.size[1])
        if p != self.pos:
            self.rect.pos = self.pos
            self.og_pos = p

    def get_fsize(self):
        return self.label.font_size

    def set_fsize(self,f):
        self.label.font_size = f
        self.rect.size = self.label.texture.size
        self.rect.texture = self.label.texture
        self.tpos = self.og_pos

    @property
    def size(self):
        return max(self.label.texture.size,self.max_size)

    text = property(get_text,set_text)
    tpos = property(get_tpos, set_tpos)
    font_size = property(get_fsize,set_fsize)

