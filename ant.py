import math
import numpy as np
from pyglet.shapes import Circle

class Ant:
    def __init__(self,win_size,pos=None,vel=None,size=1,base_speed=8):
        self.pos=pos
        self.vel=vel
        self.size=size
        self.win_size=win_size
        #if not pos:
        #    self.pos=np.array([win_size[0]//2,0],dtype='float64')
        #    angle=np.random.rand()*np.pi/4+np.pi*3/8
        #    self.vel=np.array([np.cos(angle),np.sin(angle)])*base_speed


    def update(self, acceleration=np.array([0,0])):
        self.vel*=.95 #air drag
        self.vel+=acceleration
        self.pos+=self.vel
        if not 0<=self.pos[0]<=self.win_size[0]:
            self.vel[0]*=-1
        if not 0<=self.pos[1]<=self.win_size[1]:
            self.vel[1]*=-1


    def absorb(self,ant):
        self.size+=ant.size
        self.pos+=ant.pos
        self.vel+=ant.vel
        self.pos/=2
        self.vel/=2


    def draw(self):
        Circle(*self.pos,8+self.size,color=(100,100,200)).draw()

    
    def coords(self):
        return tuple(self.pos)
