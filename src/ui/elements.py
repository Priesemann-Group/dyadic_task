from pyglet.shapes import Circle

from pyglet.text import Label
from configuration import conf
from configuration import paths
from pyglet import image
from pyglet.sprite import Sprite
import numpy as np
from backend import ant_kind


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
        if target_ant.is_competitive():
            self.opacity = 255 * (1 - progress)
        else:
            self.opacity = 100 * (1 - progress)

    def move(self, position):
        self.position = position
        self._target_sprite.position = position

    def hide(self):
        self.x = -1000
        self._target_sprite.x = -1000

    def _get_sprite(self, player_idx):  # player_idx = 2 is for predictor
        img = image.load(f'{paths.target_indicator_prefix}{player_idx}.png')
        img.anchor_x = img.width // 2
        img.anchor_y = img.height // 2
        return img


class Pointer(Circle):
    def __init__(self, player_color, player_group, player_pointer_group, *args, **kwargs):
        super().__init__(-1000, 0, conf.player_radius,
                         color=conf.border_black,
                         group=player_group,
                         *args, **kwargs)
        self._inner = Circle(-1000, 0, conf.player_radius - 2,
                             color=player_color,
                             group=player_pointer_group,
                             *args, **kwargs)

    def place(self, pos, scale_factor):
        self.position = pos
        self._inner.position = pos
        self.radius = conf.player_radius * scale_factor
        self._inner.radius = (conf.player_radius - 2) * scale_factor

    def hide(self):
        self.x = -1000
        self._inner.x = -1000


class Ant(Sprite):
    def __init__(self, kind, batch, group):
        self._player_idx = -1
        self._kind = kind
        super().__init__(img=image.load(f'{paths.circ_prefix}0.png'), batch=batch, group=group)
        self.hide()

    def update_ant(self, pos, rad, share=None):
        self.update(*tuple(pos), None, rad * 2. / conf.ant_img_size)
        if share is not None and self._share_changed(share):
            self._set_share(share)

    def hide(self):
        self.x = -1000

    def _share_changed(self, current_share):
        if not (np.isnan(current_share) and np.isnan(self._kind)):  # they are at least not both None
            if np.isnan(current_share) or np.isnan(self._kind):  # only one is None -> Change in share
                return True
            elif int(current_share * 100) != int(self._kind * 100):  # No one is none -> Check if values changed
                return True
        return False

    def get_share(self):
        return self._kind

    def is_competitive(self):
        return not ant_kind.is_shared(self._kind)

    def _set_share(self, new_share):
        self._kind = new_share
        self.image = self._get_center_circle()

    def _get_center_circle(self):
        img = image.load(f'{paths.circ_prefix}{int(self._kind)}.png')
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


class Curtain(Sprite):
    def __init__(self, batch, group):
        super().__init__(img=image.load(paths.curtain_path), batch=batch, group=group)

    def hide(self):
        #self.x = -10000
        self.visible = False


