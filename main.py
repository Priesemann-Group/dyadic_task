import random as r
import numpy as np
from numba import njit

from pyglet import clock
from pyglet.app import run
from pyglet.window import Window
from pyglet.shapes import Circle, Rectangle
from pyglet.graphics import Batch
from pyglet.text import Label

from ant import Ant
import conf as c

win = Window()
label_batch = Batch()
ant_batch = Batch()
catched_label = Label(
        font_name=c.font_name,
        font_size=c.font_size,
        color=c.label_color,
        x=0, y=0,
        batch=label_batch)
fps_label = Label(
        font_name=c.font_name,
        font_size=c.font_size,
        color=c.label_color,
        x=0, y=win.get_size()[1]-c.font_size,
        batch=label_batch)
background = Rectangle(0,0,*win.get_size(),color=c.background_color)
mouse_circle = Circle(0,0,c.mouse_circle_radius,color=c.mouse_circle_color)

targets = []
catch_count= 0
current_atr= -1
angle_pendulum= 0
attractors = [np.array([0,0],dtype='float64')]*2


@njit
def gaussian(x,mu=0.,sig=float(win.get_size()[0]/2)):
    return 1./(np.sqrt(2.*np.pi)*sig)*np.exp(-np.power((x-mu)/sig,2.)/2)


@njit
def absorb_calc(ants,radians):
    absorber_idx = 0
    meal_count=0
    eater=np.array([-1]*len(ants))
    food=np.array([-1]*len(ants))

    while(absorber_idx<len(ants)):
        absorber=ants[absorber_idx]
        if absorber[0]!=-42:
            for i,ant in enumerate(ants[absorber_idx+1:]):
                if ant[0]!=-42:
                    dist=np.linalg.norm(ant-absorber)
                    if dist < radians[absorber_idx]+radians[i+1+absorber_idx]:
                        eater[meal_count]=absorber_idx
                        food[meal_count]=i+1+absorber_idx
                        meal_count+=1
                        ants[i+1+absorber_idx] = (-42,-42)
        absorber_idx+=1
    return eater, food


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


def add_ant(x,y,angle):
    pos=np.array([x,y],dtype='float64')
    vel=np.array([np.cos(angle),np.sin(angle)])*c.start_velocity
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


def update(dt):
    if len(targets)==0:
        return
   
    eater,food = absorb_calc(ant_posistions(),ant_radians())
    for e,f in zip(eater,food):
        if e==-1:
            break
        targets[e].absorb(targets[f])
    for f in sorted(food, reverse=True):
        if f==-1:
            break
        del targets[f]

    accelerations = accelerations_calc(ant_posistions(), np.array(attractors))
    for i,ant in enumerate(targets):
        ant.update(accelerations[i])


def switch_attractors(dt=None):
    global current_atr
    width, height = win.get_size()

    current_atr=(current_atr+1)%len(attractors)
    attractors[current_atr]=np.array([r.randrange(width),r.randrange(height)],
            dtype='float64')


@win.event
def on_draw():
    global catch_count 
    global current_atr

    win.clear()

    if current_atr==-1: #Randomize initial attractors
        switch_attractors()
        switch_attractors()
        current_atr+=1

    catched_label.text=f'Ants catched: {catch_count}'
    fps_label.text=f'FPS: {clock.get_fps()}'
    fps_label.y=win.get_size()[1]-c.font_size
    background.width, background.height = win.get_size()

    background.draw()
    ant_batch.draw()
    mouse_circle.draw()
    label_batch.draw()


@win.event
def on_mouse_press(x, y, scroll_x, scroll_y):
    mouse_circle.position=(x,y)
    i = shot(np.array((x,y)),ant_posistions(),ant_radians())
    global catch_count
    if i is not None:
        catch_count+=targets[i].size
        del targets[i]


#to run njit compiler - this causes the initial loading time
absorb_calc(np.array([(42.,42.),(1.,1.)]),np.array([[42.],[42.]]))
gaussian(0.)
accelerations_calc(np.array([(42.,42.),(1.,1.)]), np.array(attractors))
shot(np.array((0,0)),np.array([(42.,42.),(1.,1.)]),np.array(([42.],[42.])))

clock.schedule_interval(add_ants, 1/c.spawns_ps)
clock.schedule_interval(update, 1/c.pos_updates_ps)
clock.schedule_interval(switch_attractors, 1/c.attractor_tele_ps)

run()
