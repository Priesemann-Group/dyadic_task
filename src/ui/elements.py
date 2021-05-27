from pyglet.shapes import Circle
from pyglet.text import Label
from configuration import conf
from pyglet import image
from pyglet.sprite import Sprite
import numpy as np


class TargetIndicator(Circle):
    def __init__(self, marker_group, *args, **kwargs):
        super().__init__(-1000, 0, 1, *args, **kwargs)
        self._target_sprite = Sprite(img=self._get_sprite(0), batch=kwargs['batch'], group=marker_group)
        self._target_sprite.x = -1000
        self.opacity = conf.target_opacity
        self.color = conf.background_color

    def set_on_target(self, target_ant, progress, player_idx):
        self.position = target_ant.position
        self._target_sprite.image = self._get_sprite(player_idx)
        self._target_sprite.update(x=target_ant.x, y=target_ant.y, rotation=None, scale=target_ant.scale)
        self.radius = (target_ant.scale * conf.ant_img_size / 2.) * (1. - progress)
        if np.isnan(target_ant.get_share()):
            self.opacity = 200 * (1 - progress)
        else:
            self.opacity = 100 * (1 - progress)

    def move(self, position):
        self.position = position
        self._target_sprite.position = position

    def _get_sprite(self, player_idx):
        img = image.load(f'../res/img/target_indicator_{player_idx}.png')
        img.anchor_x = img.width // 2
        img.anchor_y = img.height // 2
        return img


class Ant(Sprite):
    def __init__(self, share, batch, group):
        self._player_idx = -1
        self._share = share
        super().__init__(img=self._get_center_circle(), batch=batch, group=group)

    def update_ant(self, pos, rad, share=None):
        self.update(*tuple(pos), None, rad * 2. / conf.ant_img_size)
        if share is not None and self._share_changed(share):
            self._set_share(share)

    def hide(self):
        self.x = -1000

    def _share_changed(self, current_share):
        if not (np.isnan(current_share) and np.isnan(self._share)):  # they are at least not both None
            if np.isnan(current_share) or np.isnan(self._share):  # only one is None -> Change in share
                return True
            elif int(current_share * 100) != int(self._share * 100):  # No one is none -> Check if values changed
                return True
        return False

    def get_share(self):
        return self._share

    def _set_share(self, new_share):
        self._share = new_share
        self.image = self._get_center_circle()

    def set_player_idx(self, player_idx):
        self._player_idx = player_idx

    def _get_center_circle(self):
        if np.isnan(self._share):
            img = image.load('../res/img/circ.png')
        else:
            if self._player_idx == 0:
                img = image.load(f'../res/img/circ_{int(100 * self._share)}.png')
            else:
                img = image.load(f'../res/img/circ_{int(100 * (1 - self._share))}.png')
        img.anchor_x = img.width // 2
        img.anchor_y = img.height // 2
        return img


class PopUpLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(font_name=conf.font_name, font_size=conf.popup_font_size, x=-1000, y=0, **kwargs)
        self._anchor_pos = (0, 0)
        self._scale_factor = 1.

    def popup(self, player_cycle, score):
        self.text = f'+{score}'
        self._anchor_pos = (int(player_cycle.x), int(player_cycle.y))
        self.position = self._anchor_pos

    def update(self, progress):
        x, y = self._anchor_pos
        self.position = x, y + conf.popup_height * self._scale_factor * (1 - progress)

    def adapt_size(self, scale_factor):
        self.font_size = conf.popup_font_size * scale_factor
        self._scale_factor = scale_factor

    def hide(self):
        self.x = -1000

