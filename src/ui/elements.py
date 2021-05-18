from pyglet.shapes import Circle
from pyglet.text import Label
from configuration import conf
from pyglet import image
from pyglet.sprite import Sprite
import numpy as np


class TargetIndicator(Circle):
    def __init__(self, *args, **kwargs):
        super().__init__(-1000, 0, 1, *args, **kwargs)
        self.opacity = conf.target_opacity
        self._original_color = kwargs['color']

    def set_on_target(self, target, progress):
        self.position = target.position
        self.radius = (target.scale * conf.ant_img_size / 2.) * (1. - progress)
        self.color = \
            (int(float(self._original_color[0]) + float(255 - self._original_color[0]) * (1. - progress)),
             int(float(self._original_color[1]) + float(255 - self._original_color[1]) * (1. - progress)),
             int(float(self._original_color[2]) + float(255 - self._original_color[2]) * (1. - progress)))


class Ant(Sprite):
    def __init__(self, player_idx, share, batch, group):
        self._player_idx = player_idx
        self.share = share
        img = self._get_center_circle(self.share)
        super().__init__(img=img, batch=batch, group=group)

    def update_ant(self, pos, rad, share=None):
        self.update(*tuple(pos), None, rad * 2. / conf.ant_img_size)
        if share is not None and self._share_changed(share):
            self._set_new_share(share)

    def _share_changed(self, current_share):
        if not (np.isnan(current_share) and np.isnan(self.share)):  # they are at least not both None
            if np.isnan(current_share) or np.isnan(self.share):  # only one is None -> Change in share
                return True
            elif int(current_share * 100) != int(self.share * 100):  # No one is none -> Check if values changed
                return True
        return False

    def _set_new_share(self, new_share):
        self.image = self._get_center_circle(new_share)
        self.share = new_share

    def _get_center_circle(self, share):
        if np.isnan(share):
            img = image.load('../res/img/circ.png')
        else:
            if self._player_idx == 0:
                img = image.load(f'../res/img/circ_{int(100 * share)}.png')
            else:
                img = image.load(f'../res/img/circ_{int(100 * (1 - share))}.png')
        img.anchor_x = img.width // 2
        img.anchor_y = img.height // 2
        return img


class PopUpLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(font_name=conf.font_name, font_size=conf.font_size, x=-1000, y=0, **kwargs)
        self._anchor_pos = (0, 0)

    def popup(self, player_cycle, score):
        self.text = f'+{score}'
        self._anchor_pos = (int(player_cycle.x), int(player_cycle.y))
        self.position = self._anchor_pos

    def update(self, progress):
        x, y = self._anchor_pos
        self.position = x, y + conf.popup_height * (1 - progress)
