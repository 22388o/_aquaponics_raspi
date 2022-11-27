import run_clock
import run_display
import run_envread


class RoomManager:
    def __init__(self,
                 finite_looping: int,
                 time_shift: dict = False,
                 schedule: list = False):
        self.finite_looping = finite_looping  # 1- any int: actual int;
        if not time_shift:
            self.time_shift = {'delta_t_h': -1, 'delta_t_m': 0}
        else:
            self.time_shift = time_shift
        if not schedule:
            self.schedule = [
                {'function': run_clock.run,    'kwargs': {'duration': 30, 'heartbeat': 1}},
                {'function': run_display.run,  'kwargs': {'duration': 4, 'dyn': True, 'alias': 0, 'delay': 0.1}},
                {'function': run_envread.run,  'kwargs': {'code': 7, 'scroll_speed': 0.1}}
                    ]
        else:
            self.schedule = schedule

    def initiate(self):
        if not self.finite_looping:
            current_loop_count = 0
        else:
            current_loop_count = 1
        while current_loop_count <= self.finite_looping:
            for module in self.schedule:
                module['kwargs'].update(self.time_shift)
                module['function'](**module['kwargs'])
            if self.finite_looping: current_loop_count += 1


