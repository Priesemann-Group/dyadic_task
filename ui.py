from threading import Thread

import numpy as np
import pickle
import time

import pyglet
pyglet.options['vsync'] = False
#from pyglet.app import run
from pyglet import clock
from pyglet.window import Window
from pyglet.shapes import Circle, Rectangle
from pyglet.graphics import Batch
from pyglet.text import Label

from ant import Ant
import conf as c
from queue import Queue
from numba import njit

win = Window(resizable=True)

circle_batch = Batch()
label_batch = Batch()
margin_batch = Batch()

background = Rectangle(0,0,*win.get_size(),color=c.background_color)
first_screen_margin = Rectangle(0,0,1,1,color=c.margin_color,batch=margin_batch)
second_screen_margin = Rectangle(0,0,1,1,color=c.margin_color,batch=margin_batch)

mouse_circle = Circle(0,0,c.mouse_circle_radius,color=c.mouse_circle_color)

fps_label = Label(
        font_name=c.font_name,
        font_size=c.font_size,
        color=c.label_color,
        x=0, y=win.get_size()[1]-c.font_size,
        batch=label_batch)

circle_count = c.ant_amount+10#TODO del +10

circles=[]


scale_factor = None 
client_field_size = win.get_size()
coords_origin = np.array([0,0])


for i in range(circle_count):
    circles.append(Circle(0,
                          0,
                          float(1),
                          color=c.ant_color,
                          batch=circle_batch))


@win.event
def on_resize(width,height):

    #print(f'on_resize called{width} {height}')
    #client.width, client.height = win.get_size()
    global scale_factor
    global client_field_size
    global coords_origin

    client_field_size = [width,height]
    scale_factor = None 
    coords_origin = np.array([0,0])

    aspect_ratio_client = client_field_size[0]/client_field_size[1]
    aspect_ratio_server = c.field_size[0]/c.field_size[1]
    
    if aspect_ratio_client > aspect_ratio_server: #left, right margins  ##########
        #height is the limiting factor => width is what we adapt        # #    # #
        client_field_size[0]=height*aspect_ratio_server                 # #    # #
        coords_origin[0]=(width-client_field_size[0])//2                # #    # #
        scale_factor=client_field_size[0]/c.field_size[0]               ##########

        first_screen_margin.width = coords_origin[0]
        first_screen_margin.height = client_field_size[1]
        second_screen_margin.width = coords_origin[0]
        second_screen_margin.height = client_field_size[1]
        second_screen_margin.x = coords_origin[0]+client_field_size[0]
        second_screen_margin.y = 0

    elif aspect_ratio_client < aspect_ratio_server: #lower, upper margins
        #width is the limiting factor => height is what we adapt
        client_field_size[1]=width/aspect_ratio_server
        coords_origin[1]=(height-client_field_size[1])//2
        scale_factor=client_field_size[0]/c.field_size[0]
        
        first_screen_margin.width = client_field_size[0]
        first_screen_margin.height = coords_origin[1]
        second_screen_margin.width = client_field_size[0]
        second_screen_margin.height = coords_origin[1]
        second_screen_margin.x = 0
        second_screen_margin.y = coords_origin[1]+client_field_size[1]

    else:
        scale_factor=client_field_size[0]/c.field_size[0] #TODO check wether this case works

    background.width = client_field_size[0]
    background.height = client_field_size[1]
    background.x, background.y = tuple(coords_origin)

    fps_label.x=coords_origin[0]
    fps_label.y=coords_origin[1]+client_field_size[1]-c.font_size


@win.event
def on_draw():

    #print(1)
    
    global catch_count 
    global current_atr

    win.clear()

    #catched_label.text=f'Ants catched: {catch_count}'
    fps_label.text=f'FPS: {clock.get_fps()}'

    background.draw()
    circle_batch.draw()
    mouse_circle.draw()
    label_batch.draw()
    margin_batch.draw()


@win.event
def on_mouse_press(x, y, scroll_x, scroll_y):
    mouse_circle.position=(x,y)
    #i = shot(np.array((x,y)),ant_posistions(),ant_radians())
    #global catch_count
    #if i is not None:
    #    catch_count+=targets[i].size
    #    del targets[i]

def schedule_interval(func, dt):
    pyglet.clock.schedule_interval(func, dt)

def run():
    pyglet.app.run()
