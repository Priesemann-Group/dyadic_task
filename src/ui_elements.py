from pyglet.shapes import Circle
import conf


class TargetIndicator(Circle):
    def __init__(self, opacity=64, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.opacity = opacity
        self.original_color = kwargs['color']

    def set_on_target(self, target, progress):
        self.position = target.position
        self.radius = (target.scale * conf.ant_img_size / 2.) * (1. - progress)
        self.color = \
            (int(float(self.original_color[0]) + float(255 - self.original_color[0]) * (1. - progress)),
             int(float(self.original_color[1]) + float(255 - self.original_color[1]) * (1. - progress)),
             int(float(self.original_color[2]) + float(255 - self.original_color[2]) * (1. - progress)))

