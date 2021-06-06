from sched import scheduler as SchedulerBase
from backend import engine, data_depositor
import time
from configuration import conf


class GameScheduler(SchedulerBase):
    def __init__(self, action, send_msg, engine):
        super().__init__(time.time, time.sleep),
        self._action = action
        self._send_msg = send_msg
        self._engine = engine
        self._scheduled_events = []
        self._next_round = False
        self._sleep = True

    def start(self):
        while True:
            data_depositor.new_file()
            self._engine.spawn_ants()
            start_time = conf.time_before_round + time.time()
            self._send_msg(start_time)
            for i in range(conf.update_amount):
                event = self.enterabs(start_time + i / conf.pos_updates_ps, 1, self._tick)
                self._scheduled_events.append(event)
            self.run()

    def next_round(self):
        self._next_round = True

    def sleep(self):
        self._sleep = True

    def wakeup(self):
        self._sleep = False

    def _tick(self):
        if self._sleep:
            while self._sleep:
                time.sleep(1)
            self._reset()
        elif self._next_round:
            self._reset()
        else:
            self._action()

    def _reset(self):
        self._next_round = False
        data_depositor.close()  # delete invalid game record
        while not self.empty():
            self.cancel(self._scheduled_events.pop())
        self._scheduled_events = []
