#####################################################################
#
# mixer.py
#
# Copyright (c) 2015, Eran Egozy
#
# Released under the MIT License (http://opensource.org/licenses/MIT)
#
#####################################################################

import numpy as np


class Mixer(object):
    def __init__(self):
        super(Mixer, self).__init__()
        self.generators = []
        self.gain = 0.5;

    def add(self, gen) :
        if gen not in self.generators:
            self.generators.append(gen)

    def remove(self, gen) :
        self.generators.remove(gen)

    def set_gain(self, gain) :
        self.gain = np.clip(gain, 0, 1)

    def get_gain(self) :
        return self.gain

    def get_num_generators(self) :
        return len(self.generators)

    def contains(self,gen):

        for g in self.generators:
            if g== gen:
                return True
        return False


    def generate(self, num_frames, num_channels) :
        output = np.zeros(num_frames * num_channels)

        # this calls generate() for each generator. generator must return:
        # (signal, keep_going). If keep_going is True, it means the generator
        # has more to generate. False means generator is done and will be
        # removed from the list. signal must be a numpay array of length
        # num_frames * num_channels (or less)
        kill_list = []
        for g in self.generators:
            (signal, keep_going) = g.generate(num_frames, num_channels)
            output += signal
            if not keep_going:
                kill_list.append(g)

        # remove generators that are done
        for g in kill_list:
            self.generators.remove(g)

        output *= self.gain
        return (output, True)


class Sequencer(object):
    """
    Creates a Sequencer that generates notes sequentially
    Stops generating frames once the final note has been played
    
    """
    def __init__(self):
        super(Sequencer,self).__init__()
        
        self.generators = []
        self.curr_note = 0
        self.gain = 1.0
        self.finish = False
        
    def add(self, gen) :
        self.generators.append(gen)

    def remove(self, gen) :
        self.generators.remove(gen)

    def set_gain(self, gain) :
        self.gain = np.clip(gain, 0, 1)

    def get_gain(self) :
        return self.gain

    def generate(self, num_frames, num_channels) :
        output = np.zeros(num_frames * num_channels)
        output,continue_flag = self.generators[self.curr_note%len(self.generators)].generate(num_frames, num_channels)
        output *= self.gain
        if not continue_flag:
            self.curr_note += 1
        self.finish = self.curr_note > len(self.generators)
        return (output, not self.finish)