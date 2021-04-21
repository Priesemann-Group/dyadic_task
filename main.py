import random as r
import numpy as np
from threading import Lock
import time
import copy

from numba import njit

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

@njit
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

update_time = 0.
draw_time = 0.

@njit
def absorb_calc(ants):
    absorber_idx = 0
    #out = [] 
    absorbers=[]#TODO fix length for jit?
    absorbed=[]
    
    while(absorber_idx<len(ants)):
        absorber=ants[absorber_idx]
        if absorber[0]!=-42:
            for i,ant in enumerate(ants[absorber_idx+1:]):
                if ant[0]!=-42:
                    dist=np.linalg.norm(ant-absorber)
                    if dist < 20:
                        #out.append((absorber_idx,i+1+absorber_idx))
                        absorbers.append(absorber_idx)
                        absorbed.append(i+1+absorber_idx)
                        ants[i+1+absorber_idx] = (-42,-42)
        absorber_idx+=1
    return absorbers, absorbed

@njit
def accelerations_calc(ants, attractors):
    accs=np.zeros_like(ants)
    for i,ant in enumerate(ants):
        acc = np.array([0,0],dtype='float64')
        for atr in attractors:
            vec=atr-ant
            dist=np.linalg.norm(vec)
            acc+=vec*gaussian(dist)/dist/gaussian(0.)
        accs[i]=acc
    return accs


#to run njit compiler
absorb_calc(np.array([(42.,42.),(1.,1.)]))
gaussian(0.)
accelerations_calc(np.array([(42.,42.),(1.,1.)]), attractors)

def ant_posistions():
    out=targets[0].pos
    for i in range(1,len(targets)):
        out=np.vstack((out,targets[i].pos))
    return out

def update(dt):
    if len(targets)==0:
        return
    
    eater,food = absorb_calc(ant_posistions())

    for e,f in zip(eater,food):
        targets[e].absorb(targets[f])
    for f in sorted(food, reverse=True):
        del targets[f]
    #for _,food in reversed(absorbings):
    #    del targets[food] #TODO list assignment out of range

    accelerations = accelerations_calc(ant_posistions(), attractors)
    
    for i,ant in enumerate(targets):
        ant.update(accelerations[i])

def switch_attractors(dt):
    global current_atr
    width, height = win.get_size()

    #w_m=width//8
    #h_m=height//8

    current_atr=(current_atr+1)%len(attractors)
    #attractors[current_atr]=np.array([r.randrange(w_m,width-w_m),r.randrange(h_m,height-h_m)],
    attractors[current_atr]=np.array([r.randrange(width),r.randrange(height)],
            dtype='float64')


clock.schedule_interval(add_ants, .2)
clock.schedule_interval(update, 1/33)
clock.schedule_interval(switch_attractors, 1)


@win.event
def on_draw():
    begin = time.time()
    global draw_time

    win.clear()
    background = Rectangle(0,0,*win.get_size(),color=(255,255,255))
    background.draw()
    mouse_circle.draw()
    for ant in targets:
        ant.draw()
    lasso.draw()

    t=time.time()-begin
    if t>draw_time:
        draw_time=t
        print(f'draw_time:{draw_time}')


drag_dist=0

@win.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
    global drag_dist
    drag_dist+=(dx**2+dy**2)**(.5)
    if drag_dist>10: #Fixes lag for high res mouse input
        mouse_circle.anchor_position=(x,y)
        lasso.consume((x,y))
        drag_dist=0


@win.event
def on_mouse_release(x, y, button, modifiers):
    lasso.collapse()
    #p = []
    #for a in targets:
    #    p.append(tuple(a.pos.astype('float64')))
    #print(p)


pyglet.app.run()
