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

for i in range(100):
    draw.ellipse((0, 0, conf.ant_img_size, conf.ant_img_size),
                 fill=conf.player_colors[1])
    draw.pieslice((0, 0, conf.ant_img_size, conf.ant_img_size),
                  start=frac_to_deg(0),
                  end=frac_to_deg(i/100.),
                  fill=conf.player_colors[0])
    im.save(output_folder_path + f'/circ_{i}.png', quality=100)

draw.ellipse((0, 0, conf.ant_img_size, conf.ant_img_size), fill=conf.player_colors[0])
im.save(output_folder_path + f'/circ_{100}.png', quality=100)

draw.ellipse((0, 0, conf.ant_img_size, conf.ant_img_size), fill=conf.ant_color)
im.save(output_folder_path + f'/circ.png', quality=100)

margin = conf.ant_img_size * .05

for i in [0, 1]:
    draw.ellipse((0, 0, conf.ant_img_size, conf.ant_img_size), fill=conf.player_colors[i])
    draw.ellipse((margin, margin, conf.ant_img_size - margin, conf.ant_img_size - margin), fill=0)
    im.save(output_folder_path + f'/target_indicator_{i}.png', quality=100)
