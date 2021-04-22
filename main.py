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
from pyglet.graphics import Batch
from pyglet.text import Label

from ant import Ant

win = pyglet.window.Window()

label_batch = Batch()
ant_batch = Batch()
catched_label = Label(text='Ants catched: ',
        font_name='Arial',
        font_size=20,
        color=(0, 0, 0, 255),
        x=0, y=0,
        batch=label_batch)
fps_label = Label(text='FPS: ',
        font_name='Arial',
        font_size=20,
        color=(0, 0, 0, 255),
        x=0, y=win.get_size()[1]-20,
        batch=label_batch)

#Event Logger
#event_logger = pyglet.window.event.WindowEventLogger()
#win.push_handlers(event_logger)

mouse_circle = Circle(0,0,5,color=(100,100,100))

catch_count = 0
targets = []
current_atr = 0
attractors = [np.array([0,0],
    dtype='float64')]*2
angle_pendulum=0

@njit
def gaussian(x,mu=0.,sig=float(win.get_size()[0]/2)):
    return 1./(np.sqrt(2.*np.pi)*sig)*np.exp(-np.power((x-mu)/sig,2.)/2)

def add_ant(x,y,angle):
    pos=np.array([x,y],dtype='float64')
    vel=np.array([np.cos(angle),np.sin(angle)])*10
    ant=Ant(win.get_size(),pos,vel,batch=ant_batch)
    targets.append(ant)


def add_ants(dt):
    global angle_pendulum
    width, height = win.get_size()

    angle=np.pi/2*np.sin(np.pi*angle_pendulum/20)-np.pi/4
    add_ant(0,height/2,angle)
    add_ant(width/2,0,angle+np.pi/2)
    add_ant(width,height/2,angle+np.pi)
    add_ant(width/2,height,angle+np.pi*3/2)

    angle_pendulum+=1
    angle_pendulum%=20

@njit
def absorb_calc(ants,radians):
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
                    #if dist < 20:
                    if dist < radians[absorber_idx]+radians[i+1+absorber_idx]:
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

@njit
def shot(pos,ants,radians):
    for i,ant in enumerate(ants):
        dist=np.linalg.norm(ant-pos)
        if dist < radians[i]:
            return i


#to run njit compiler
absorb_calc(np.array([(42.,42.),(1.,1.)]),np.array([[42.],[42.]]))
gaussian(0.)
accelerations_calc(np.array([(42.,42.),(1.,1.)]), attractors)
shot(np.array((0,0)),np.array([(42.,42.),(1.,1.)]),np.array(([42.],[42.])))

def ant_posistions():
    out=np.array([targets[0].pos])
    for i in range(1,len(targets)):
        out=np.vstack((out,np.array([targets[i].pos])))
    return out

def ant_radians():
    out=np.array([targets[0].radius])
    for i in range(1,len(targets)):
        out=np.vstack((out,np.array([targets[i].radius])))
    return out

def update(dt):
    if len(targets)==0:
        return
   
    eater,food = absorb_calc(ant_posistions(),ant_radians())

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
clock.schedule_interval(update, 1/60)
clock.schedule_interval(switch_attractors, 1)


@win.event
def on_draw():
    win.clear()
    background = Rectangle(0,0,*win.get_size(),color=(255,255,255))
    background.draw()

    ant_batch.draw()
    mouse_circle.draw()
    global catch_count 

    catched_label.text=f'Ants catched: {catch_count}'
    fps_label.text=f'FPS: {clock.get_fps()}'
    fps_label.y=win.get_size()[1]-20
    label_batch.draw()


@win.event
def on_mouse_press(x, y, scroll_x, scroll_y):
    mouse_circle.position=(x,y)
    i = shot(np.array((x,y)),ant_posistions(),ant_radians())
    global catch_count
    if i is not None:
        catch_count+=targets[i].size
        del targets[i]


pyglet.app.run()
