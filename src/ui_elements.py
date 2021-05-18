from pyglet.shapes import Circle
from pyglet.text import Label
import conf


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

