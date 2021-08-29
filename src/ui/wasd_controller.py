from pyglet.window import key
from pyglet import clock
from configuration import conf


class KeyController:
    def __init__(self, event_decorator, on_space_pressed):
        self._on_space_pressed = on_space_pressed
        event_decorator(self.on_key_press)

    def on_key_press(self, symbol, modifiers):
        if symbol == key.SPACE:
            self._on_space_pressed()


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


