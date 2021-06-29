from pyglet.window import key
from pyglet import clock
from configuration import conf


class WasdController:
    def __init__(self, event_decorator, on_motion):
        self._w_pressed = False
        self._a_pressed = False
        self._s_pressed = False
        self._d_pressed = False
        self._x = conf.field_size[0] // 2
        self._y = conf.field_size[1] // 2
        self._on_motion = on_motion
        event_decorator(self.on_key_press)
        event_decorator(self.on_key_release)
        clock.schedule_interval(self._tick, conf.wasd_update_rate)

    def _tick(self, dx):
        self._movement()
        self._correct_to_boundaries()
        self._on_motion((self._x, self._y))

    def _movement(self):  # TODO make speed euclidian
        if self._w_pressed:
            self._y += conf.wasd_speed
        if self._a_pressed:
            self._x -= conf.wasd_speed
        if self._s_pressed:
            self._y -= conf.wasd_speed
        if self._d_pressed:
            self._x += conf.wasd_speed

    def _correct_to_boundaries(self):
        if self._x < 0:
            self._x = 0
        elif self._x > conf.field_size[0]:
            self._x = conf.field_size[0]
        if self._y < 0:
            self._y = 0
        elif self._y > conf.field_size[1]:
            self._y = conf.field_size[1]

    def on_key_press(self, symbol, modifiers):
        if symbol == key.W:
            self._w_pressed = True
        elif symbol == key.A:
            self._a_pressed = True
        elif symbol == key.S:
            self._s_pressed = True
        elif symbol == key.D:
            self._d_pressed = True

    def on_key_release(self, symbol, modifiers):
        if symbol == key.W:
            self._w_pressed = False
        elif symbol == key.A:
            self._a_pressed = False
        elif symbol == key.S:
            self._s_pressed = False
        elif symbol == key.D:
            self._d_pressed = False


