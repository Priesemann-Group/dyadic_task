import numpy as np
import conf as c
from pyglet import clock
from pyglet import image
from pyglet.sprite import Sprite
from pyglet.window import Window
from pyglet.shapes import Circle, Rectangle
from pyglet.graphics import Batch, OrderedGroup
from pyglet.text import Label
import pyglet

#pyglet.options['vsync'] = False
win = Window(resizable=True, style=Window.WINDOW_STYLE_BORDERLESS, vsync=False)

batch = Batch()

bg_group = OrderedGroup(0)
ant_group = OrderedGroup(1)
fg_group = OrderedGroup(2)
target_group = OrderedGroup(3)
mouse_group = OrderedGroup(4)

background = Rectangle(0, 0, *win.get_size(), color=c.background_color, batch=batch, group=bg_group)
first_margin = Rectangle(0, 0, 1, 1, color=c.margin_color, batch=batch, group=fg_group)
second_margin = Rectangle(0, 0, 1, 1, color=c.margin_color, batch=batch, group=fg_group)

player_mouse_circle = Circle(0, 0, c.mouse_circle_radius, color=c.player_colors[0], batch=batch, group=mouse_group)
opponent_mouse_circle = Circle(0, 0, c.mouse_circle_radius, color=c.player_colors[1], batch=batch, group=mouse_group)
target_circles = [
    Circle(-1000, -1000, 1, color=c.player_colors[0], batch=batch, group=target_group),  # For clients player
    Circle(-1000, -1000, 1, color=c.player_colors[1], batch=batch, group=target_group)  # For opponent
]

target_circles[0].opacity = c.target_opacity
target_circles[1].opacity = c.target_opacity


def get_label(x, y):
    return Label(
        font_name=c.font_name,
        font_size=c.font_size,
        color=c.label_color,
        x=x, y=y,
        batch=batch,
        group=fg_group)


fps_label = get_label(0, win.get_size()[1] - c.font_size)
ping_label_1 = get_label(0, win.get_size()[1] - 1 * c.font_size)
ping_label_2 = get_label(0, win.get_size()[1] - 3 * c.font_size)
score_label_1 = get_label(0, 0)
score_label_2 = get_label(0, c.font_size)
player_number_label = get_label(0, 2 * c.font_size)

scores = [0, 0]

scale_factor = None
client_field_size = win.get_size()
origin_coords = np.array([0, 0])
ant_shares_mirror = np.full(c.ant_amount, np.nan)

circles = []
player_number = -2
player_pings = [-1, -1]

for _ in range(c.ant_amount):
    img = image.load('src/circ.png')
    img.anchor_x = img.width // 2
    img.anchor_y = img.height // 2
    sprite = Sprite(img, 0, 0, batch=batch, group=ant_group)
    sprite.update(0, 0, None, 1/c.ant_img_size)
    circles.append(sprite)


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

    fps_label.x = origin_coords[0]  # TODO write method if possible
    fps_label.y = origin_coords[1] + client_field_size[1] - c.font_size
    ping_label_1.x = origin_coords[0]
    ping_label_1.y = origin_coords[1] + client_field_size[1] - 2 * c.font_size
    ping_label_2.x = origin_coords[0]
    ping_label_2.y = origin_coords[1] + client_field_size[1] - 3 * c.font_size
    player_number_label.x = origin_coords[0]
    player_number_label.y = origin_coords[1] + 2 * c.font_size
    score_label_1.x = origin_coords[0]
    score_label_1.y = origin_coords[1] + c.font_size
    score_label_2.x = origin_coords[0]
    score_label_2.y = origin_coords[1]


@win.event
def on_draw():
    win.clear()

    fps_label.text = f'FPS: {clock.get_fps()}'
    ping_label_1.text = f'Ping Player 1: {player_pings[0]}'
    ping_label_2.text = f'Ping Player 2: {player_pings[1]}'
    score_label_1.text = f'Score Player 1: {scores[0]}'
    score_label_2.text = f'Score Player 2: {scores[1]}'
    player_number_label.text = f'You are Player {player_number + 1}'

    batch.draw()


def schedule_interval(func, dt):
    pyglet.clock.schedule_interval(func, dt)


def get_center_circle(ant_shares):
    if np.isnan(ant_shares):
        img = image.load('src/circ.png')
    else:
        if player_number == 0:
            img = image.load(f'src/circ_{int(100 * ant_shares)}.png')
        else:
            img = image.load(f'src/circ_{int(100 * (1-ant_shares))}.png')
    img.anchor_x = img.width // 2
    img.anchor_y = img.height // 2
    return img


def update_ant_sprites(i, ant_shares):
    if not (np.isnan(ant_shares) and np.isnan(ant_shares_mirror[i])):  # they are at least not both None
        if np.isnan(ant_shares) or np.isnan(ant_shares_mirror[i]):  # only one is None
            circles[i].image = get_center_circle(ant_shares)
            ant_shares_mirror[i] = ant_shares
        else:  # No one is none
            if int(ant_shares * 100) != int(ant_shares_mirror[i] * 100):
                circles[i].image = get_center_circle(ant_shares)
                ant_shares_mirror[i] = ant_shares


def set_ants(packet):
    packet[:, :2] += origin_coords  # pos to relative client pos
    for i, p in enumerate(packet):
        ant_pos, ant_rad, ant_shares = p[:2], p[2], p[3]
        circles[i].update(*tuple(ant_pos), None, ant_rad * 2. / c.ant_img_size)
        update_ant_sprites(i, ant_shares)
    for i in range(len(packet), c.ant_amount):
        circles[i].update(-1000, -1000, None, 0.)


def set_target_states(target_states):  # Called after set_ants()
    for i, t_s in enumerate(target_states):
        if t_s > -.5:
            idx = int(t_s)
            progress = t_s - idx
            target_circles[i].position = circles[idx].position
            target_circles[i].radius = (circles[idx].scale * c.ant_img_size / 2.) * (1. - progress)
            target_circles[i].color = \
                (int(float(c.player_colors[i][0]) + float(255 - c.player_colors[i][0]) * (1. - progress)),
                 int(float(c.player_colors[i][1]) + float(255 - c.player_colors[i][1]) * (1. - progress)),
                 int(float(c.player_colors[i][2]) + float(255 - c.player_colors[i][2]) * (1. - progress)))
        else:
            target_circles[i].position = (-1000, -1000)


def run():
    pyglet.app.run()
