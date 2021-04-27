import math
import numpy as np

import conf as c

class Ant:
    def __init__(self,win_size,pos=None,vel=None,batch=None,size=1):
        self.pos=pos
        self.vel=vel
        self.size=size
        self.radius=(c.ant_base_area*self.size)**(.5)
        self.win_size=win_size
        self.circ=None
        if batch:
            from pyglet.shapes import Circle
            self.circ=Circle(*self.pos,self.radius,color=c.ant_color,batch=batch)


    def update(self, acceleration=np.array([0,0]), air_drag=False):
        if air_drag:
            air_drag=(1-c.exp_decay-self.size*c.size_dep_exp_vel_decay)
            if air_drag<10**-5: #To prevent overflows
                air_drag=0
            self.vel*=air_drag
        self.vel+=acceleration
        self.pos+=self.vel
        if self.pos[0]<0+self.radius:
            self.pos[0]=1+self.radius
            self.vel[0]*=-1
        elif self.pos[0]>c.field_size[0]-self.radius:
            self.pos[0]=c.field_size[0]-1-self.radius
            self.vel[0]*=-1
        if self.pos[1]<0+self.radius:
            self.pos[1]=1+self.radius
            self.vel[1]*=-1
        elif self.pos[1]>c.field_size[1]-self.radius:
            self.pos[1]=c.field_size[1]-1-self.radius
            self.vel[1]*=-1

        #if not 0<=self.pos[0]<=self.win_size[0]:
        #    self.vel[0]*=-1
        #if not 0<=self.pos[1]<=self.win_size[1]:
        #    self.vel[1]*=-1
        if self.circ:
            self.circ.position=self.coords()

    def collide(self,ant):
        joint_vel=(self.vel*self.size+ant.vel*ant.size)/(self.size+ant.size)
        self.vel=2*joint_vel-self.vel
        ant.vel=2*joint_vel-ant.vel
        #dist=np.linalg.norm(self.pos-ant.pos)
        #if dist<self.radius+ant.radius

    def absorb(self,ant):
        s=self.size+ant.size
        self.pos=(self.size*self.pos+ant.size*ant.pos)/s
        self.vel=(self.size*self.vel+ant.size*ant.vel)/s
        self.size=s
        self.radius=(c.ant_base_area*self.size)**(.5)
        if self.circ:
            self.circ.position=tuple(self.pos)
            self.circ.radius=self.radius
            ant.circ.delete() #delete absorbed ant


    def coords(self):
        return tuple(self.pos)
