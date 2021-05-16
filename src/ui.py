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

win = Window(resizable=True, vsync=False)
batch = Batch()

bg_group = OrderedGroup(0)
ant_group = OrderedGroup(1)
fg_group = OrderedGroup(2)
target_group = OrderedGroup(3)
opponent_group = OrderedGroup(4)
player_group = OrderedGroup(5)

background = Rectangle(0, 0, *win.get_size(), color=c.background_color, batch=batch, group=bg_group)
first_margin = Rectangle(0, 0, 1, 1, color=c.margin_color, batch=batch, group=fg_group)
second_margin = Rectangle(0, 0, 1, 1, color=c.margin_color, batch=batch, group=fg_group)

black_margins = [
    Rectangle(0, 0, 1, 1, color=c.margin_color, batch=batch, group=fg_group),
    Rectangle(0, 0, 1, 1, color=c.margin_color, batch=batch, group=fg_group)
]

player_mouse_circles = [Circle(0, 0, c.mouse_circle_radius, color=c.player_colors[0], batch=batch, group=player_group),
                        Circle(0, 0, c.mouse_circle_radius, color=c.player_colors[1], batch=batch, group=opponent_group)
                        ]

target_circles = [
    Circle(-1000, -1000, 1, color=c.player_colors[0], batch=batch, group=target_group),  # For clients player
    Circle(-1000, -1000, 1, color=c.player_colors[1], batch=batch, group=target_group)  # For opponent
]

target_circles[0].opacity = c.target_opacity
target_circles[1].opacity = c.target_opacity


def get_label(x, y, font_name=c.font_name, font_size=c.font_size, color=c.label_color, group=fg_group):
    return Label(
        font_name=font_name,
        font_size=font_size,
        color=color,
        x=x, y=y,
        batch=batch,
        group=group)


fps_label = get_label(0, win.get_size()[1] - c.font_size)
player_number_label = get_label(0, 2 * c.font_size)

ping_labels = [get_label(0, win.get_size()[1] - 2 * c.font_size),
               get_label(0, win.get_size()[1] - 3 * c.font_size)]
score_labels = [get_label(0, c.font_size),
                get_label(0, 0)]
score_animation_labels = [get_label(-1000, 0, color=(*c.player_colors[0], 255), group=player_group),
                          get_label(-1000, 0, color=(*c.player_colors[1], 255), group=opponent_group)]

scores = [0, 0]

scale_factor = None
client_field_size = win.get_size()
origin_coords = np.array([0, 0])
ant_shares_mirror = np.full(c.ant_amount, np.nan)

circles = []
player_number = -2
player_pings = [-1, -1]

for _ in range(c.ant_amount):
    img = image.load('../res/img/circ.png')
    img.anchor_x = img.width // 2
    img.anchor_y = img.height // 2
    sprite = Sprite(img, 0, 0, batch=batch, group=ant_group)
    sprite.update(0, 0, None, 1 / c.ant_img_size)
    circles.append(sprite)


@win.event
def on_resize(width, height):
    global scale_factor
    global client_field_size
    global origin_coords

    scale_factor = None
    client_field_size = [width, height]
    origin_coords = np.array([0, 0])

    aspect_ratio_client = client_field_size[0] / client_field_size[1]
    aspect_ratio_server = c.field_size[0] / c.field_size[1]

    if aspect_ratio_client > aspect_ratio_server:  # left, right margins  ##########
        # height is the limiting factor => width is what we adapt         # #    # #
        client_field_size[0] = height * aspect_ratio_server               # #    # #
        origin_coords[0] = (width - client_field_size[0]) // 2            # #    # #
        scale_factor = client_field_size[0] / c.field_size[0]             ##########

        black_margins[0].width = origin_coords[0]
        black_margins[0].height = client_field_size[1]
        black_margins[1].width = origin_coords[0]
        black_margins[1].height = client_field_size[1]

        black_margins[1].x = origin_coords[0] + client_field_size[0]
        black_margins[1].y = 0

    elif aspect_ratio_client < aspect_ratio_server:  # lower, upper margins
        # width is the limiting factor => height is what we adapt
        client_field_size[1] = width / aspect_ratio_server
        origin_coords[1] = (height - client_field_size[1]) // 2
        scale_factor = client_field_size[1] / c.field_size[1]

        black_margins[0].width = client_field_size[0]
        black_margins[0].height = origin_coords[1]
        black_margins[1].width = client_field_size[0]
        black_margins[1].height = origin_coords[1]

        black_margins[1].x = 0
        black_margins[1].y = origin_coords[1] + client_field_size[1]

    else:
        scale_factor = client_field_size[0] / c.field_size[0]  # TODO check whether this case works

    background.width = client_field_size[0]
    background.height = client_field_size[1]
    background.x, background.y = tuple(origin_coords)

    fps_label.x = origin_coords[0]
    fps_label.y = origin_coords[1] + client_field_size[1] - c.font_size
    for i, label in enumerate(ping_labels):
        label.x = origin_coords[0]
        label.y = origin_coords[1] + client_field_size[1] - (2 + i) * c.font_size
    player_number_label.x = origin_coords[0]
    player_number_label.y = origin_coords[1] + 2 * c.font_size
    for label in score_labels:
        label.x = origin_coords[0]
        label.y = origin_coords[1]
    score_labels[0].y += c.font_size


@win.event
def on_draw():
    win.clear()

    fps_label.text = f'FPS: {clock.get_fps()}'
    player_number_label.text = f'You are Player {player_number + 1}'
    for i in range(len(ping_labels)):
        ping_labels[i].text = f'Ping Player {i + 1}: {player_pings[i]}'
        score_labels[i].text = f'Score Player {i + 1}: {scores[i]}'

    batch.draw()


def schedule_interval(func, dt):
    pyglet.clock.schedule_interval(func, dt)


def get_center_circle(ant_shares):
    if np.isnan(ant_shares):
        img = image.load('../res/img/circ.png')
    else:
        if player_number == 0:
            img = image.load(f'../res/img/circ_{int(100 * ant_shares)}.png')
        else:
            img = image.load(f'../res/img/circ_{int(100 * (1 - ant_shares))}.png')
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


def set_score_states(score_states, target_states):
    if not np.isnan(sum(score_states)) \
            and int(target_states[0]) == int(target_states[1]) \
            and score_animation_labels[0].x == -1000:
        score_animation_labels[0].text = f'+{int(score_states[0])}'
        score_animation_labels[1].text = f'+{int(score_states[1])}'
        score_animation_labels[0].position = (int(player_mouse_circles[0].x - c.score_popup_offset),
                                              int(player_mouse_circles[0].y))
        score_animation_labels[1].position = (int(player_mouse_circles[0].x),
                                              int(player_mouse_circles[0].y))
        return
    for i, state in enumerate(score_states):
        if not np.isnan(state):
            if score_animation_labels[i].x == -1000:
                score_animation_labels[i].text = f'+{int(state)}'
                score_animation_labels[i].position = (int(player_mouse_circles[i].x - c.score_popup_offset),
                                                      int(player_mouse_circles[i].y))
        else:
            score_animation_labels[i].x = -1000


def run():
    pyglet.app.run()
