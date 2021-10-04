import numpy

from pyglet.window import key
from pyglet import clock
from configuration import conf
from backend.engine import euclid_dist


class KeyController:
    def __init__(self, event_decorator, on_space_pressed):
        self._on_space_pressed = on_space_pressed
        event_decorator(self.on_key_press)

    def on_key_press(self, symbol, modifiers):
        if symbol == key.SPACE:
            self._on_space_pressed()


class CapedMouseControl:
    def __init__(self, event_decorator, on_motion):
        self._mouse_pos = numpy.array(conf.field_size)/2
        self._pos = numpy.array(conf.field_size)/2
        print(f'position: {self._pos}')
        self._vel = numpy.array([0, 0])
        self._on_motion = on_motion
        event_decorator(self.on_mouse_motion)
        clock.schedule_interval(self._tick, conf.wasd_update_rate)

    def on_mouse_motion(self, x, y, dx, dy):
        self._mouse_pos[0] = x
        self._mouse_pos[1] = y

    def _tick(self, dx):
        vec_to_mouse = self._mouse_pos - self._pos
        dist_to_mouse = euclid_dist(vec_to_mouse)
        if dist_to_mouse > conf.wasd_speed:
            self._vel = vec_to_mouse/dist_to_mouse*conf.wasd_speed
        else:
            self._vel = vec_to_mouse
        self._pos += self._vel
        self._on_motion(tuple(self._pos))


class WasdController(KeyController):
    def __init__(self, event_decorator, on_motion, on_space_pressed):
        super().__init__(event_decorator, on_space_pressed)
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

    def _movement(self):
        diag = False
        if self._w_pressed and self._d_pressed:
            self._y += conf.wasd_diag_speed
            self._x += conf.wasd_diag_speed
            diag = True
        if self._w_pressed and self._a_pressed:
            self._y += conf.wasd_diag_speed
            self._x -= conf.wasd_diag_speed
            diag = True
        if self._s_pressed and self._d_pressed:
            self._y -= conf.wasd_diag_speed
            self._x += conf.wasd_diag_speed
            diag = True
        if self._s_pressed and self._a_pressed:
            self._y -= conf.wasd_diag_speed
            self._x -= conf.wasd_diag_speed
            diag = True
        if not diag:
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
        super().on_key_press(symbol, modifiers)
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


