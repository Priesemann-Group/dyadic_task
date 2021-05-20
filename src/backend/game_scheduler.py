from sched import scheduler as SchedulerBase
from backend import engine, data_depositor
import time
from configuration import conf


class GameScheduler(SchedulerBase):
    def __init__(self, action):
        super().__init__(time.time, time.sleep),
        self._action = action
        self._scheduled_events = []
        self._next_round = False
        self._sleep = True

    def start(self):
        while True:
            data_depositor.new_file()
            engine.respawn_ants()
            engine.score = [0, 0]
            start_time = 1 + time.time()
            for i in range(conf.update_amount):
                event = self.enterabs(start_time + i / conf.pos_updates_ps, 1, self._tick)  # TODO new round stuff
                self._scheduled_events.append(event)
            self.run()
        #self.round()  # start next round

    def next_round(self):
        self._next_round = True

    def sleep(self):
        self._sleep = True

    def wakeup(self):
        self._sleep = False

    def _tick(self):  # TODO rewrite?
        if self._sleep:
            data_depositor.close()  # delete invalid game record
            while self._sleep:
                print('sleeping...')
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
