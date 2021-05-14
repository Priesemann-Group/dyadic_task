from PIL import Image, ImageDraw
import os

from src import conf

real_path = os.path.realpath(__file__)
dir_path = os.path.dirname(real_path)

im = Image.new('RGBA', (conf.ant_img_size, conf.ant_img_size), (0, 0, 0, 0))
draw = ImageDraw.Draw(im)

PI = 3.141593
to_deg = lambda x: 180/PI*(x+PI*3/2)  # {+PI*3/2} to adapt to PIL
frac_to_deg = lambda x: to_deg(x*2*PI)

if not os.path.exists(f'{dir_path}/src'):
    os.makedirs(f'{dir_path}/src')

for i in range(100):
    draw.ellipse((0, 0, conf.ant_img_size, conf.ant_img_size), fill=conf.player_colors[1])
    draw.pieslice((0, 0, conf.ant_img_size, conf.ant_img_size),
                  start=frac_to_deg(0),
                  end=frac_to_deg(i/100.),
                  fill=conf.player_colors[0])
    im.save(f'{dir_path}/src/circ_{i}.png', quality=100)

draw.ellipse((0, 0, conf.ant_img_size, conf.ant_img_size), fill=conf.player_colors[0])
im.save(f'{dir_path}/src/circ_{100}.png', quality=100)

draw.ellipse((0, 0, conf.ant_img_size, conf.ant_img_size), fill=conf.ant_color)
im.save(f'{dir_path}/src/circ.png', quality=100)

