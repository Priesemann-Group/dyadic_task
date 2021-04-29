import numpy as np
import conf as c
from pyglet import clock
from pyglet.window import Window
from pyglet.shapes import Circle, Rectangle
from pyglet.graphics import Batch
from pyglet.text import Label
import pyglet

pyglet.options['vsync'] = False
win = Window(resizable=True)

circle_batch = Batch()
label_batch = Batch()
margin_batch = Batch()
player_batch = Batch()

background = Rectangle(0, 0, *win.get_size(), color=c.background_color)
first_margin = Rectangle(0, 0, 1, 1, color=c.margin_color, batch=margin_batch)
second_margin = Rectangle(0, 0, 1, 1, color=c.margin_color, batch=margin_batch)

mouse_circle = Circle(0, 0, c.mouse_circle_radius, color=c.mouse_circle_color, batch=player_batch)
opponent_circle = Circle(0, 0, c.mouse_circle_radius, color=c.opponent_circle_color, batch=player_batch)

fps_label = Label(
    font_name=c.font_name,
    font_size=c.font_size,
    color=c.label_color,
    x=0, y=win.get_size()[1] - c.font_size,
    batch=label_batch)
score_label_1 = Label(
    font_name=c.font_name,
    font_size=c.font_size,
    color=c.label_color,
    x=0, y=0,
    batch=label_batch)
score_label_2 = Label(
    font_name=c.font_name,
    font_size=c.font_size,
    color=c.label_color,
    x=0, y=c.font_size,
    batch=label_batch)

scores = [0, 0]

circles = []
scale_factor = None
client_field_size = win.get_size()
origin_coords = np.array([0, 0])

for i in range(c.ant_amount):
    circles.append(Circle(0,
                          0,
                          float(1),
                          color=c.ant_color,
                          batch=circle_batch))


@win.event
def on_resize(width, height):
    global scale_factor
    global client_field_size
    global origin_coords

    client_field_size = [width, height]
    scale_factor = None
    origin_coords = np.array([0, 0])

    aspect_ratio_client = client_field_size[0] / client_field_size[1]
    aspect_ratio_server = c.field_size[0] / c.field_size[1]

    if aspect_ratio_client > aspect_ratio_server:  # left, right margins  ##########
        # height is the limiting factor => width is what we adapt         # #    # #
        client_field_size[0] = height * aspect_ratio_server               # #    # #
        origin_coords[0] = (width - client_field_size[0]) // 2            # #    # #
        scale_factor = client_field_size[0] / c.field_size[0]             ##########

        first_margin.width = origin_coords[0]
        first_margin.height = client_field_size[1]
        second_margin.width = origin_coords[0]
        second_margin.height = client_field_size[1]
        second_margin.x = origin_coords[0] + client_field_size[0]
        second_margin.y = 0

    elif aspect_ratio_client < aspect_ratio_server:  # lower, upper margins
        # width is the limiting factor => height is what we adapt
        client_field_size[1] = width / aspect_ratio_server
        origin_coords[1] = (height - client_field_size[1]) // 2
        scale_factor = client_field_size[0] / c.field_size[0]

        first_margin.width = client_field_size[0]
        first_margin.height = origin_coords[1]
        second_margin.width = client_field_size[0]
        second_margin.height = origin_coords[1]
        second_margin.x = 0
        second_margin.y = origin_coords[1] + client_field_size[1]

    else:
        scale_factor = client_field_size[0] / c.field_size[0]  # TODO check whether this case works

    background.width = client_field_size[0]
    background.height = client_field_size[1]
    background.x, background.y = tuple(origin_coords)

    fps_label.x = origin_coords[0]
    fps_label.y = origin_coords[1] + client_field_size[1] - c.font_size
    score_label_1.x = origin_coords[0]
    score_label_1.y = origin_coords[1] + c.font_size
    score_label_2.x = origin_coords[0]
    score_label_2.y = origin_coords[1]


@win.event
def on_draw():
    win.clear()

    fps_label.text = f'FPS: {clock.get_fps()}'
    score_label_1.text = f'Score Player 1: {scores[0]}'
    score_label_2.text = f'Score Player 2: {scores[1]}'

    background.draw()
    circle_batch.draw()
    player_batch.draw()
    label_batch.draw()
    margin_batch.draw()


def schedule_interval(func, dt):
    pyglet.clock.schedule_interval(func, dt)


def set_target_states(target_states):
    for t_s in target_states:
        if t_s > 0.:
            idx = int(t_s)
            progress = t_s - idx
            circles[idx].color = (100 + 155 * (1 - progress),
                                  100 + 155 * (1 - progress),
                                  200 + 55 * (1 - progress))


def set_ants(packet):
    packet[:, :2] += origin_coords
    for i, p in enumerate(packet):
        ant_pos, ant_rad = p[:2], p[2]
        circles[i].position = tuple(ant_pos)
        circles[i].radius = float(ant_rad)
        circles[i].color = c.ant_color
    for i in range(len(packet), c.ant_amount):
        circles[i].position = (-1000, -1000)
        circles[i].radius = 0.


def run():
    pyglet.app.run()
