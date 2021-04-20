import random as r
import numpy as np
from threading import Lock

import pyglet
from pyglet import clock
from pyglet.shapes import Circle
from pyglet.shapes import Rectangle

import shapely
from shapely.geometry import LineString
from shapely.geometry import Polygon
from shapely.geometry import Point

from lasso import Lasso
from ant import Ant

win = pyglet.window.Window()

#Event Logger
#event_logger = pyglet.window.event.WindowEventLogger()
#win.push_handlers(event_logger)

mouse_circle = Circle(0,0,5,color=(100,100,100))

targets = []
current_atr = 0
attractors = [np.array([0,0],
    dtype='float64')]*2

lasso = Lasso(targets)


def gaussian(x,mu=0.,sig=float(win.get_size()[0]/2)):
    return 1./(np.sqrt(2.*np.pi)*sig)*np.exp(-np.power((x-mu)/sig,2.)/2)

def add_ants(dt):

    start_vel=8.
    width, height = win.get_size()
    
    angle=np.random.rand()*np.pi/4+np.pi*5/8

    left_pos=np.array([0,height/2],dtype='float64')
    left_vel=np.array([-np.cos(angle),np.sin(angle)])*start_vel
    left_ant=Ant(win.get_size(),left_pos,left_vel)
    targets.append(left_ant)

    right_pos=np.array([width,height/2],dtype='float64')
    right_vel=np.array([np.cos(angle),np.sin(angle)])*start_vel
    right_ant=Ant(win.get_size(),right_pos,right_vel)
    targets.append(right_ant)
    
    angle=np.random.rand()*np.pi/4+np.pi*3/8

    lower_pos=np.array([width/2,0],dtype='float64')
    lower_vel=np.array([-np.cos(angle),np.sin(angle)])*start_vel
    lower_ant=Ant(win.get_size(),lower_pos,lower_vel)
    targets.append(lower_ant)
    
    upper_pos=np.array([width/2,height],dtype='float64')
    upper_vel=np.array([-np.cos(angle),-np.sin(angle)])*start_vel
    upper_ant=Ant(win.get_size(),upper_pos,upper_vel)
    targets.append(upper_ant)

def update(dt):
    
    absorber_idx = 0

    while(absorber_idx<len(targets)): #TODO This goes better!
        absorber=targets[absorber_idx]
        idx_to_del = []
        for i,ant in enumerate(targets[absorber_idx+1:]):
            dist=np.linalg.norm(ant.pos-absorber.pos)
            if dist < 20:
                absorber.absorb(ant)
                idx_to_del.append(i+absorber_idx+1)
        for idx in sorted(idx_to_del, reverse=True):
            del targets[idx]
        absorber_idx+=1
            

    for ant in targets:
        acc = np.array([0,0],dtype='float64')
        for atr in attractors:
            vec=atr-ant.pos
            dist=np.linalg.norm(vec)
            acc+=vec*gaussian(dist)/dist/gaussian(0.)
        ant.update(acc)

def switch_attractors(dt):
    global current_atr
    width, height = win.get_size()

    #w_m=width//8
    #h_m=height//8

    current_atr=(current_atr+1)%len(attractors)
    #attractors[current_atr]=np.array([r.randrange(w_m,width-w_m),r.randrange(h_m,height-h_m)],
    attractors[current_atr]=np.array([r.randrange(width),r.randrange(height)],
            dtype='float64')


clock.schedule_interval(add_ants, .15)
clock.schedule_interval(update, 1/33)
clock.schedule_interval(switch_attractors, 1)


@win.event
def on_draw():
    win.clear()
    
    background = Rectangle(0,0,*win.get_size(),color=(255,255,255))
    background.draw()
    mouse_circle.draw()
    for ant in targets:
        ant.draw()
    lasso.draw()


@win.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
    mouse_circle.anchor_position=(x,y)
    lasso.consume((x,y))


@win.event
def on_mouse_release(x, y, button, modifiers):
    lasso.collapse()


pyglet.app.run()
