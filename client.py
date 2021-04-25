from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor

from threading import Thread

import numpy as np
import pickle
import time

import pyglet
#from pyglet.app import run
from pyglet import clock
from pyglet.window import Window
from pyglet.shapes import Circle, Rectangle
from pyglet.graphics import Batch
from pyglet.text import Label

from ant import Ant
import conf as c
from queue import Queue

win = Window()

circle_batch = Batch()
label_batch = Batch()

background = Rectangle(0,0,*win.get_size(),color=c.background_color)
mouse_circle = Circle(0,0,c.mouse_circle_radius,color=c.mouse_circle_color)

fps_label = Label(
        font_name=c.font_name,
        font_size=c.font_size,
        color=c.label_color,
        x=0, y=win.get_size()[1]-c.font_size,
        batch=label_batch)

circle_count = 300


circles=[]
rec_packets = Queue()

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
    
    if aspect_ratio_client > aspect_ratio_server: #left, right margins 
        #print(1)
        #height is the limiting factor => width is what we adapt
        client_field_size[0]=height*aspect_ratio_server
        coords_origin[0]=(width-client_field_size[0])//2
        scale_factor=client_field_size[0]/c.field_size[0] 
    elif aspect_ratio_client < aspect_ratio_server: #lower, upper margins
        #width is the limiting factor => height is what we adapt
        #print(2)
        client_field_size[1]=width/aspect_ratio_server
        coords_origin[1]=(height-client_field_size[1])//2
        scale_factor=client_field_size[0]/c.field_size[0]
    else:
        scale_factor=client_field_size[0]/c.field_size[0] #TODO check wether this case works

    background.width = client_field_size[0]
    background.height = client_field_size[1]
    background.x, background.y = tuple(coords_origin)



@win.event
def on_draw():
    global catch_count 
    global current_atr

    win.clear()

    #catched_label.text=f'Ants catched: {catch_count}'
    fps_label.text=f'FPS: {clock.get_fps()}'
    fps_label.y=coords_origin[1]+win.get_size()[1]-c.font_size

    background.draw()
    circle_batch.draw()
    mouse_circle.draw()
    label_batch.draw()


@win.event
def on_mouse_press(x, y, scroll_x, scroll_y):
    mouse_circle.position=(x,y)
    #i = shot(np.array((x,y)),ant_posistions(),ant_radians())
    #global catch_count
    #if i is not None:
    #    catch_count+=targets[i].size
    #    del targets[i]
        
class MulticastClient(DatagramProtocol):
    def startProtocol(self):
        """
        Called after protocol has started listening.
        """
        # Set the TTL>1 so multicast will cross router hops:
        self.transport.setTTL(5)
        # Join a specific multicast group:
        self.transport.joinGroup("228.0.0.5")


    def datagramReceived(self, datagram, address):
        global circles
        global scale_factor
        global coords_origin

        #print('received datagram')
        packet=pickle.loads(datagram)
        #ant_pos,ant_rad = packet[:,:2],packet[:,2]

        #ant_pos*=scale_factor #TODO the same for rad
        packet*=scale_factor #scale positions as well as radians 
        packet[:,:2]+=coords_origin
        rec_packets.put(packet)

consume_time = -1000000

def consume_packet(dx):
    global consume_time
    t0 = time.time() 

    if rec_packets.qsize()>1:
        print(f'Client skipped {rec_packets.qsize()-1} packet(s).')
        for _ in range(rec_packets.qsize()-1):
            rec_packets.get()
    if not rec_packets.empty():
        packet=rec_packets.get()
        #ant_pos,ant_rad = packet[:,:2],packet[:,2]
        for i,p in enumerate(packet):
            ant_pos,ant_rad = p[:2],p[2]
            circles[i].position=tuple(ant_pos)
            circles[i].radius=float(ant_rad)
        for i in range(len(packet),circle_count):
            circles[i].position=(-1000,-1000)
            circles[i].radius=0.

    t=time.time()-t0
    if t>consume_time:
        consume_time=t
        print(consume_time)




pyglet.clock.schedule_interval(consume_packet, 2**-20)
Thread(target=pyglet.app.run).start()
print('app closed')

# We use listenMultiple=True so that we can run MulticastServer.py and
# MulticastClient.py on same machine:
reactor.listenMulticast(9999, MulticastClient(), listenMultiple=True)
reactor.run()
