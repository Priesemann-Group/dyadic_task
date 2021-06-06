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
        self._countdown_label = Label(x=0, y=0,
                                      font_name=conf.font_name,
                                      font_size=conf.countdown_font_size,
                                      color=conf.font_color,
                                      group=fg_group,
                                      batch=batch)
        self._countdown_label.anchor_x = 'center'
        self._countdown_label.anchor_y = 'center'
        self._scale_factor = None
        self._client_field_size = None
        self._origin = [0, 0]
        self._background = Rectangle(0, 0, 0, 0, color=conf.background_color, batch=batch, group=bg_group)
        self._score_chart = self.ScoreChart(batch=batch, fg_group=fg_group, bg_group=bg_group)
        self._black_margins = [Rectangle(0, 0, 1, 1, color=conf.margin_color, batch=batch, group=fg_group),
                               Rectangle(0, 0, 1, 1, color=conf.margin_color, batch=batch, group=fg_group)]
        self.event(self.on_resize)
        self.event(self.on_key_release)

    def close(self):
        self._window.close()

    def get_scale_factor(self):
        return self._scale_factor

    def set_player_idx(self, player_idx):
        if self._debug_overlay:
            self._debug_labels._player_number = player_idx

    def on_key_release(self, symbol, modifiers):
        if symbol == 102:  # 102 == symbol for 'f'
            self._window.set_fullscreen(fullscreen=not self._window.fullscreen)

    def event(self, func):
        return self._window.event(func)

    def to_win_coordinates(self, x, reverse=False):
        x = numpy.array(x)
        if not reverse:
            return x * self._scale_factor + numpy.array(self._origin)
        else:
            return (x - self._origin) / self._scale_factor

    def set_scores_and_pings(self, scores, pings, score_states):
        if self._debug_overlay:
            self._debug_labels._scores = scores
            self._debug_labels._player_pings = pings
        self._score_chart.set_score(scores, score_states)

    def on_draw(self):
        self._window.clear()
        if self._debug_overlay:
            self._debug_labels.draw()
        self._countdown_label.draw()

    def set_countdown(self, num):
        if num == 0:
            self._countdown_label.color = (0, 0, 0, 0)
        else:
            self._countdown_label.color = conf.font_color
            self._countdown_label.text = f'{num}'

    def on_resize(self, width, height):
        self._scale_factor = -1
        self._origin = [0, 0]

        aspect_ratio_client = width / height
        aspect_ratio_game = (conf.field_size[0] + conf.score_chart_width) / conf.field_size[1]
        score_chart_share = conf.score_chart_width / (conf.field_size[0] + conf.score_chart_width)

        if aspect_ratio_client > aspect_ratio_game:  # left, right margins
            # height is the limiting factor => width is what we adapt
            self._background.height = height
            game_width = height * aspect_ratio_game
            self._background.width = game_width * (1 - score_chart_share)

            self._scale_factor = self._background.width / conf.field_size[0]

            self._black_margins[0].width = (width - game_width) // 2
            self._black_margins[1].width = (width - game_width) // 2
            self._black_margins[0].height = height
            self._black_margins[1].height = height

            self._score_chart.resize(x=self._black_margins[0].width,
                                     y=0,
                                     width=game_width * score_chart_share,
                                     height=height)

            self._origin[0] += self._black_margins[0].width
            self._origin[0] += self._score_chart.width

            self._black_margins[1].x = self._origin[0] + game_width
            self._black_margins[1].y = 0
        elif aspect_ratio_client < aspect_ratio_game:  # lower, upper margins
            # width is the limiting factor => height is what we adapt
            self._background.width = width * (1 - score_chart_share)
            game_height = width / aspect_ratio_game
            self._background.height = game_height

            self._scale_factor = self._background.height / conf.field_size[1]

            self._black_margins[0].height = (height - game_height) // 2
            self._black_margins[1].height = (height - game_height) // 2
            self._black_margins[0].width = width
            self._black_margins[1].width = width

            self._score_chart.resize(x=0,
                                     y=self._black_margins[0].height,
                                     width=width * score_chart_share,
                                     height=game_height)

            self._origin[0] += self._score_chart.width
            self._origin[1] += self._black_margins[0].height

            self._black_margins[1].x = 0
            self._black_margins[1].y = self._origin[1] + game_height
        else:
            self._background.width = width
            self._background.height = height

            self._scale_factor = 1.

            for margin in self._black_margins:
                margin.width = 0
                margin.height = 0

            self._score_chart.resize(x=0,
                                     y=0,
                                     width=width * score_chart_share,
                                     height=height)
            self._origin[0] += self._score_chart.width

        self._background.position = tuple(self._origin)

        if self._debug_overlay:
            self._debug_labels.replace_labels(origin=self._origin,
                                              field_height=self._background.height)
        self._countdown_label.x = self._origin[0] + self._background.width // 2
        self._countdown_label.y = self._origin[1] + self._background.height // 2

    class ScoreChart(Rectangle):
        def __init__(self, batch, fg_group, bg_group):
            super().__init__(0, 0, 1, 1, color=conf.score_chart_bg_color, batch=batch, group=bg_group)
            self._scores = [0, 0]
            self._bars = [Rectangle(0, 0, 1, 1, color=conf.player_colors[0], batch=batch, group=fg_group),
                          Rectangle(0, 0, 1, 1, color=conf.player_colors[1], batch=batch, group=fg_group)]

        def resize(self, x, y, width, height):
            self.width = width
            self.height = height
            self.x = x
            self.y = y
            for i in [0, 1]:
                self._bars[i].x = x + i * width // 2
                self._bars[i].y = y
                self._bars[i].width = width // 2
            self._update_bars()

        def set_score(self, scores, score_states):
            self._scores = scores
            self._update_bars(score_states)

        def _update_bars(self, score_states=None):
            for i, bar in enumerate(self._bars):
                if score_states is None or numpy.isnan(score_states[i]):
                    bar.height = self.height * self._scores[i] / conf.score_chart_max_score
                else:
                    progress = score_states[i] - int(score_states[i])
                    fraction_to_show = int(score_states[i]) * (1. - progress)
                    score_to_show = self._scores[i] - int(score_states[i]) + fraction_to_show
                    bar.height = self.height * score_to_show / conf.score_chart_max_score

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

        def replace_labels(self, origin, field_height):
            self._fps_label.x = origin[0]
            self._fps_label.y = origin[1] + field_height - conf.font_size
            for i, label in enumerate(self._ping_labels):
                label.x = origin[0]
                label.y = origin[1] + field_height - (2 + i) * conf.font_size
            self._player_number_label.x = origin[0]
            self._player_number_label.y = origin[1] + 2 * conf.font_size
            for label in self._score_labels:
                label.x = origin[0]
                label.y = origin[1]
            self._score_labels[0].y += conf.font_size

        def draw(self):
            self._fps_label.text = f'FPS: {int(clock.get_fps())}'
            self._player_number_label.text = f'You are Player {self._player_number + 1}'
            for i in range(len(self._ping_labels)):
                self._ping_labels[i].text = f'Ping Player {i + 1}: {self._player_pings[i]}'
                self._score_labels[i].text = f'Score Player {i + 1}: {self._scores[i]}'
