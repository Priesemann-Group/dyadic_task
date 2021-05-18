from pyglet.window import Window
from pyglet.shapes import Rectangle
from pyglet.text import Label
from pyglet import clock
from configuration import conf
import numpy


class ScaleFieldWindow:
    def __init__(self, batch, bg_group, fg_group, debug_overlay=False, *args, **kwargs):
        self._window = Window(*args, **kwargs)  # Wrapper because window is abstract
        self._debug_overlay = debug_overlay
        if self._debug_overlay:
            self._debug_labels = self.DebugLabels(batch, fg_group)
        self._scale_factor = None
        self._client_field_size = None
        self._origin = (0, 0)
        self._background = Rectangle(0, 0, 0, 0, color=conf.background_color, batch=batch, group=bg_group)
        self._black_margins = [Rectangle(0, 0, 1, 1, color=conf.margin_color, batch=batch, group=fg_group),
                               Rectangle(0, 0, 1, 1, color=conf.margin_color, batch=batch, group=fg_group)]
        self.event(self.on_resize)

    def get_scale_factor(self):
        return self._scale_factor

    def set_player_idx(self, player_idx):
        if self._debug_overlay:
            self._debug_labels.player_number = player_idx

    def event(self, func):
        return self._window.event(func)

    def to_win_coordinates(self, x, reverse=False):
        x = numpy.array(x)
        if not reverse:
            return x * self._scale_factor + numpy.array(self._origin)
        else:
            return (x - self._origin) / self._scale_factor

    def set_scores_and_pings(self, scores, pings):
        if self._debug_overlay:
            self._debug_labels._scores = scores
            self._debug_labels._player_pings = pings

    def on_draw(self):
        self._window.clear()
        if self._debug_overlay:
            self._debug_labels.draw()

    def on_resize(self, width, height):
        self._scale_factor = None
        self._client_field_size = [width, height]
        self._origin = [0, 0]

        aspect_ratio_client = self._client_field_size[0] / self._client_field_size[1]
        aspect_ratio_server = conf.field_size[0] / conf.field_size[1]

        if aspect_ratio_client > aspect_ratio_server:  # left, right margins
            # height is the limiting factor => width is what we adapt
            self._client_field_size[0] = height * aspect_ratio_server
            self._origin[0] = (width - self._client_field_size[0]) // 2
            self._scale_factor = self._client_field_size[0] / conf.field_size[0]

            self._black_margins[0].width = self._origin[0]
            self._black_margins[0].height = self._client_field_size[1]
            self._black_margins[1].width = self._origin[0]
            self._black_margins[1].height = self._client_field_size[1]

            self._black_margins[1].x = self._origin[0] + self._client_field_size[0]
            self._black_margins[1].y = 0

        elif aspect_ratio_client < aspect_ratio_server:  # lower, upper margins
            # width is the limiting factor => height is what we adapt
            self._client_field_size[1] = width / aspect_ratio_server
            self._origin[1] = (height - self._client_field_size[1]) // 2
            self._scale_factor = self._client_field_size[1] / conf.field_size[1]

            self._black_margins[0].width = self._client_field_size[0]
            self._black_margins[0].height = self._origin[1]
            self._black_margins[1].width = self._client_field_size[0]
            self._black_margins[1].height = self._origin[1]

            self._black_margins[1].x = 0
            self._black_margins[1].y = self._origin[1] + self._client_field_size[1]

        else:
            self._scale_factor = self._client_field_size[0] / conf.field_size[0]  # TODO check whether this case works

        self._background.width = self._client_field_size[0]
        self._background.height = self._client_field_size[1]
        self._background.x, self._background.y = self._origin[0], self._origin[1]

        if self._debug_overlay:
            self._debug_labels.replace_labels(self._origin, self._client_field_size)

    class DebugLabels:
        def __init__(self, batch, fg_group):
            self._player_pings = [-1, -1]
            self._scores = [0, 0]

            label_kwargs = {'x': 0, 'y': 0,
                            'font_name': conf.font_name,
                            'font_size': conf.font_size,
                            'color': conf.font_color,
                            'batch': batch,
                            'group': fg_group}

            self._fps_label = Label(**label_kwargs)
            self._player_number_label = Label(**label_kwargs)
            self._ping_labels = [Label(**label_kwargs),
                                 Label(**label_kwargs)]
            self._score_labels = [Label(**label_kwargs),
                                  Label(**label_kwargs)]
            self._player_number = -1

        def replace_labels(self, origin, field_size):
            self._fps_label.x = origin[0]
            self._fps_label.y = origin[1] + field_size[1] - conf.font_size
            for i, label in enumerate(self._ping_labels):
                label.x = origin[0]
                label.y = origin[1] + field_size[1] - (2 + i) * conf.font_size
            self._player_number_label.x = origin[0]
            self._player_number_label.y = origin[1] + 2 * conf.font_size
            for label in self._score_labels:
                label.x = origin[0]
                label.y = origin[1]
            self._score_labels[0].y += conf.font_size

        def draw(self):
            self._fps_label.text = f'FPS: {clock.get_fps()}'
            self._player_number_label.text = f'You are Player {self._player_number + 1}'
            for i in range(len(self._ping_labels)):
                self._ping_labels[i].text = f'Ping Player {i + 1}: {self._player_pings[i]}'
                self._score_labels[i].text = f'Score Player {i + 1}: {self._scores[i]}'
