from PIL import Image, ImageDraw
import os

import conf

real_path = os.path.realpath(__file__)
dir_path = os.path.dirname(real_path)
output_folder_path = dir_path + '/../../res/img'

im = Image.new('RGBA', (conf.ant_img_size, conf.ant_img_size), (0, 0, 0, 0))
draw = ImageDraw.Draw(im)

PI = 3.141593
to_deg = lambda x: 180/PI*(x+PI*3/2)  # {+PI*3/2} to adapt to PIL
frac_to_deg = lambda x: to_deg(x*2*PI)


if not os.path.exists(output_folder_path):
    os.makedirs(output_folder_path)

name_index = 0

margin = conf.ant_img_size * .05


def draw_shared_circ(fraction, col_0=conf.player_colors[0], col_1=conf.player_colors[1]):
    start = frac_to_deg(0)
    end = frac_to_deg(fraction)
    global name_index
    draw.ellipse((0, 0, conf.ant_img_size, conf.ant_img_size),
                 fill=conf.border_black),
    draw.ellipse((margin, margin, conf.ant_img_size - margin, conf.ant_img_size - margin),
                 fill=col_1),
    draw.pieslice((margin, margin, conf.ant_img_size - margin, conf.ant_img_size - margin),
                  start=start,
                  end=end,
                  fill=col_0)
    im.save(output_folder_path + f'/circ_{name_index}.png', quality=100)
    name_index += 1


for i in range(1, 4):
    draw_shared_circ(i/16.)
for i in range(13, 16):
    draw_shared_circ(i/16.)
for i in range(5, 8):
    draw_shared_circ(i/16., col_0=conf.competitive_reward_color, col_1=conf.ant_base_color)
#for i in range(5, 8):
#    draw_shared_circ(i/16., second_col=conf.ant_base_color, reverse=True)

#for i in range(17):
#    draw.ellipse((0, 0, conf.ant_img_size, conf.ant_img_size),
#                 fill=conf.player_colors[1])
#    draw.pieslice((0, 0, conf.ant_img_size, conf.ant_img_size),
#                  start=frac_to_deg(0),
#                  end=frac_to_deg(i/16.),
#                  fill=conf.player_colors[0])
#    im.save(output_folder_path + f'/circ_{i}.png', quality=100)

#draw.ellipse((0, 0, conf.ant_img_size, conf.ant_img_size), fill=conf.player_colors[0])
#im.save(output_folder_path + f'/circ_{100}.png', quality=100)

#draw.ellipse((0, 0, conf.ant_img_size, conf.ant_img_size), fill=conf.ant_base_color)
#im.save(output_folder_path + f'/circ.png', quality=100)


for i in [0, 1]:
    draw.ellipse((0, 0, conf.ant_img_size, conf.ant_img_size),
                 fill=conf.player_colors[i])
    draw.ellipse((margin/2, margin/2, conf.ant_img_size - margin/2, conf.ant_img_size - margin/2),
                 fill=conf.border_black)
    draw.ellipse((margin, margin, conf.ant_img_size - margin, conf.ant_img_size - margin),
                 fill=0)
    im.save(output_folder_path + f'/target_indicator_{i}.png', quality=100)
