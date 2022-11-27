from BaseClasses import BaseClasses as BC
import run_clock
import run_display
import run_envread


def app_room_manager(**data_passed):
    app = BC.RoomManager(**data_passed)
    app.initiate()


if __name__ == "__main__":
    _schedule = [
        {'function': run_clock.run,     'kwargs': {'duration': 45, 'heartbeat': 1}},
        {'function': run_display.run,   'kwargs': {'duration': 5, 'dyn': True, 'alias': 0, 'delay': 0.1}},
        {'function': run_envread.run,   'kwargs': {'code': 3, 'scroll_speed': 0.075}}]
    _time_shift =\
        {'delta_t_h': -1, 'delta_t_m': 0}
    app_room_manager(finite_looping=0, schedule=_schedule, time_shift=_time_shift)

