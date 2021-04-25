import math
import numpy as np
from pyglet.shapes import Circle

import conf as c

class Ant:
    def __init__(self,win_size,pos=None,vel=None,batch=None,size=1):
        self.pos=pos
        self.vel=vel
        self.size=size
        self.radius=(c.ant_base_area*self.size)**(.5)
        self.win_size=win_size
        self.circ=Circle(*self.pos,self.radius,color=c.ant_color,batch=batch)


    def update(self, acceleration=np.array([0,0])):
        self.vel*=(1-c.exp_decay-self.size*c.size_dep_exp_vel_decay) #air drag
        self.vel+=acceleration
        self.pos+=self.vel
        if not 0<=self.pos[0]<=self.win_size[0]:
            self.vel[0]*=-1
        if not 0<=self.pos[1]<=self.win_size[1]:
            self.vel[1]*=-1
        self.circ.position=self.coords()


    def absorb(self,ant):
        s=self.size+ant.size
        self.pos=(self.size*self.pos+ant.size*ant.pos)/s
        self.vel=(self.size*self.vel+ant.size*ant.vel)/s
        self.size=s
        self.radius=(c.ant_base_area*self.size)**(.5)
        self.circ.position=tuple(self.pos)
        self.circ.radius=self.radius
        ant.circ.delete() #delete absorbed ant


    def coords(self):
        return tuple(self.pos)
