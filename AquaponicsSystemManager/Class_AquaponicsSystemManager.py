import time
try:
    import RPi.GPIO as GPIO
except ImportError:
    GPIO = None

from SenseHatLedClock import Class_SenseHatLedClock as SeLC
from SenseHatSensors import Class_SenseHatSensors as SeSe

import display_8x8 as d8


class GpioPin:
    def __init__(self, _id_):
        self._id_ = _id_
        self.used:          bool    = False
        self.state_is:      bool    = None
        self.state_ought:   bool    = None
        self.io:            bool    = False     # (I)n: True,   (O)ut: False
        self.taskname:      str     = ""


class APSystemManager:
    def __init__(self, heartbeat: int = 20, delta_t_h: int = 0, delta_t_m: int = 0):
        self.delta_t_h = delta_t_h  # difference btw system time and real time: whole hours
        self.delta_t_m = delta_t_m  # difference btw system time and real time: additional minutes

        self.curr_date_str:             str = ''            # format:   2020-05-17
        self.curr_time_str:             str = ''            # format:   09:41
        self.curr_datetime_str:         str = ''            # format:   2018-02-11_03:21
        self.set_current_timedata(mode=2)
        self.timedate_at_init:          str = self.curr_datetime_str
        self.timedate_at_start_manager: str = ''            # format:   2016-03-03_05:43
        self.time_at_start_loop:        str = ''            # format:   03:21
        self.time_at_prevs_loop:        str = ''            # format:   03:21

        self.looptime_changed: bool         = False

        self.mngr_start_minute_zero = time.time()
        self.act_loop_start_time = 0
        self.act_loop_end_time = 0
        self.loop_counter: int = 0
        self.conditions = True

        self.manual_override = False

        # An 'event' is a set of actions takes in one go. An 'event' delays any other actions in a given loop, so
        # by definition an 'event' always starts and finishes in the same loop.
        # Events therefore are only timed once.

        # A 'process' is a set of actions that is independent form loops. A 'process' usually starts and ends in
        # different loops.
        # Processes are therefore timed both for start and for finish.

        # verification necessary:
        # no overlap inside each action
        self.dict_of_events: dict       =   {   "waterstream":
                                                    ['00:05', '01:05', '02:05', '03:05', '04:05', '05:05', '06:05',

                                                     '07:05', '07:35', '08:05', '08:35', '09:05', '09:35',
                                                     '10:05', '10:35', '11:05', '11:35', '12:05', '12:35',
                                                     '13:05', '13:35', '14:05', '14:35', '15:05', '15:35',
                                                     '16:05', '16:35', '17:05', '17:35', '18:05', '18:35',
                                                     '19:05', '19:35', '20:05', '20:35', '21:05', '21:35',
                                                     '22:05', '22:35', '23:05', '23:35'
                                                                     ],
                                                "feeding":          ['20:20', '21:20', '22:20', '23:20'],
                                                "shading_raise":    [],
                                                "shading_lower":    []}
        self.dict_of_events_command: dict   = {"waterstream": ['14:10']}
        self.event_details: dict        =   {   "waterstream":      {"duration": 5},
                                                "feeding":          {"duration": 20}}
        # verification necessary:
        # no overlap inside each action over any period. not even start end overlap btw. any two.
        self.dict_of_processes: dict    =   {   "light-1":          [{'start': '20:17', 'end': '20:17'},
                                                                     {'start': '21:00', 'end': '21:10'},
                                                                     {'start': '23:55', 'end': '23:55'},
                                                                     {'start': '23:59', 'end': '00:06'},
                                                                     {'start': '03:05', 'end': '03:10'},
                                                                     {'start': '08:05', 'end': '08:10'}],
                                                "light-2":          [{'start': '20:17', 'end': '20:18'},
                                                                     {'start': '22:22', 'end': '22:22'},
                                                                     {'start': '08:05', 'end': '08:10'}
                                                                     ],
                                                "aircirculation":   [{'start': '13:00', 'end': '12:58'}
                                                                     ],
                                                "ventillation":     []}

        self.pins: dict                 =   {   "waterstream":      7,
                                                "feeding":          15,
                                                "light-1":          14,
                                                "light-2":          12,
                                                "aircirculation":   18,
                                                "ventillation":     16,
                                                "shading_raise":    21,
                                                "shading_lower":    20}

        self.pin_info: dict             =   {7:  {'state': None, 'ought': None, 'dir': 'out', 'used': None},
                                             12: {'state': None, 'ought': None, 'dir': 'out', 'used': None},
                                             14: {'state': None, 'ought': None, 'dir': 'out', 'used': None},
                                             15: {'state': None, 'ought': None, 'dir': 'out', 'used': None},
                                             16: {'state': None, 'ought': None, 'dir': 'out', 'used': None},
                                             18: {'state': None, 'ought': None, 'dir': 'out', 'used': None},
                                             20: {'state': None, 'ought': None, 'dir': 'out', 'used': None},
                                             21: {'state': None, 'ought': None, 'dir': 'out', 'used': None}}

        self.gpio_states = {}
        # --- Input validation ------------------------------------------------------------------   START   -
        self.validate_times()
        self.validate_ops()
        # --- Input validation ------------------------------------------------------------------   ENDED   -
        self.actual_commands = {}
        self.heartbeat: int = heartbeat     # seconds

    def update_pin_info(self):
        for event, timelist in self.dict_of_events.items():
            if timelist:
                self.pin_info[self.pins[event]]["used"] = True

        for process, periodlist in self.dict_of_processes.items():
            if periodlist:
                self.pin_info[self.pins[process]]["used"] = True

    def update_commands(self):
        self.actual_commands = {}
        for pin, pininfo in self.pin_info.items():
            if pininfo["used"] and pininfo["state"] != pininfo["ought"] and pininfo["ought"] is not None:
                self.actual_commands[pin] = pininfo["ought"]

    def setup_pins(self):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        for pin_id, pin_data in self.pin_info.items():
            if pin_data['task']:
                GPIO.setup(pin_id, {'out': GPIO.OUT, 'in': GPIO.IN}[pin_data['dir']])

    def set_current_timedata(self, mode: int):
        cst = time.time() - 3600 * self.delta_t_h - 60 * self.delta_t_m  # Current System Time
        working_answer = self.create_timeformat(float_time=cst, mode=mode)

        if mode in [0, 2]:
            self.curr_time_str = working_answer[0]
        if mode in [1, 2]:
            self.curr_date_str = working_answer[1]
        if mode == 2:  # to update complete time and date readings
            self.curr_datetime_str = "{}_{}".format(self.curr_date_str, self.curr_time_str)

    @ staticmethod
    def create_timeformat(float_time: float, mode: int) -> dict:
        dst = time.gmtime(float_time)  # Detailed System Time
        answer = {}
        if mode in [0, 2]:
            answer[0] = time.strftime("%H:%M", dst)
        if mode in [1, 2]:
            answer[1] = time.strftime("%Y-%m-%d", dst)
        return answer

    def validate_times(self):
        pass

    def validate_ops(self):
        pass

    def update_conditions(self):
        self.conditions = True

    def msg_actual_task(self, task_name, state):
        print("actual task {:<10}: {:>20}".format(state, task_name))

    def measuring_phase(self):
        self.msg_actual_task(task_name="Measuring", state="started")
        time.sleep(0)
        self.msg_actual_task(task_name="Measuring", state="ended")

    def looptime_change_tracker(self):
        if self.time_at_prevs_loop == self.time_at_start_loop:
            self.looptime_changed = False
        else:
            self.looptime_changed = True

    def start_manager(self):
        self.update_pin_info()
        self.set_current_timedata(mode=2)
        self.timedate_at_start_manager: str = self.curr_datetime_str

        self.mainloop()

    def update_ought_status(self):
        for eventname in self.dict_of_events.keys():
            pin = self.pins[eventname]
            if self.pin_info[pin]["used"]:  # later: pin_object_dict
                ought = self.track_event(eventname=eventname)
                self.pin_info[pin]["ought"] = ought

        for processname in self.dict_of_processes.keys():
            pin = self.pins[processname]
            if self.pin_info[pin]["used"]:  # later: pin_object_dict
                ought = self.track_process(processname=processname)
                self.pin_info[pin]["ought"] = ought

    def track_event(self, eventname):
        """=== Method name: track_event ================================================================================
        Method returns a True answer if current timestamp (at actual loop begin) can be found in the time-list defined
        by the user for actual 'eventname'.
        :param eventname: string - name of the event to be tracked
        :return bool
        ========================================================================================== by Sziller ==="""
        event_time_list = self.dict_of_events[eventname]

        ought_status = False
        if self.time_at_start_loop in event_time_list:
            ought_status = True
        return ought_status

    def track_event_ui(self, eventname):
        """=== Method name: track_event ================================================================================
        Method returns a True answer if current timestamp (at actual loop begin) can be found in the time-list defined
        by the user for actual 'eventname'.
        :param eventname: string - name of the event to be tracked
        :return bool
        ========================================================================================== by Sziller ==="""
        event_time_list = self.dict_of_events[eventname]

        ought_status = False
        if self.time_at_start_loop in event_time_list:
            ought_status = True
        return ought_status

    def track_process(self, processname: str):
        """=== Method name: track_process ==============================================================================
        Method returns a True answer if current timestamp (at actual loop begin) falls into any of the periods defined
        by the user for actual 'processname'.
        :param processname: string - name of the process to be tracked
        :return bool
        ========================================================================================== by Sziller ==="""
        process_period_list = self.dict_of_processes[processname]
        ought_status = None
        for period in process_period_list:
            start   = int("".join(period['start'].split(sep=":")))
            end     = int("".join(period['end'].split(sep=":")))
            now     = int("".join(self.time_at_start_loop.split(sep=":")))
            ought_status = self.track_period(start, end, now)
            if ought_status:
                break
        return ought_status

    @staticmethod
    def track_period(start: int, end: int, now: int):
        """=== Method name: track_period ===============================================================================
        Method checks if integer is inside segment defined by two values.
        Period might be circular, if starting value exceeds end value: These are the cases where 'now' is considered to
        be inside 'period': o = now

        normal period:
        | start        end      |
        |   >---o-------<       |
        |   o-----------<       |
        |   >---------- o       |
        |   o                   |

        circular case:
        |  end        start     |
        |-o-<           >-------|
        |---o           >-------|
        |---<           >---o---|
        |---<           o-------|
        ========================================================================================== by Sziller ==="""
        if start <= now <= end:
            included = True
        elif now <= end < start:
            included = True
        elif end < start <= now:
            included = True
        else:
            included = False
        return included

    def issue_commands(self):

        for pin, command in self.actual_commands.items():
            taskname = [key for key, value in self.pins.items() if value == pin][0]

            # processes:
            if taskname in self.dict_of_processes.keys():
                if command is True:
                    self.gpio_switch_on(pin_id=pin, process_name=taskname)
                elif command is False:
                    self.gpio_switch_off(pin_id=pin, process_name=taskname)
                else:
                    print("BIG FUCKING HOW...???")
            # events:
            if taskname in self.dict_of_events.keys():
                if command is True:
                    self.gpio_switch_period(timespan=self.event_details[taskname]['duration'],
                                            heartbeat=self.event_details[taskname]['duration'] * 0.1,
                                            pin_id=pin, event_name=taskname)
                elif command is False:
                    self.gpio_switch_off(pin_id=pin, process_name=taskname)

    def mainloop(self):
        while self.conditions:
            print("---------------------------------------------------------------------------------------------------")
            # time management   phase                                                           START   -
            # timing scheme: loop_start -   action_end -    loop_end
            self.set_current_timedata(mode=0)
            self.time_at_start_loop = self.curr_time_str
            self.looptime_change_tracker()
            self.act_loop_start_time = time.time()
            d8.display_8x8(string=self.curr_time_str, char="X")     # chr(9608)
            clock = SeLC.LedClock()
            clock.delta_t_h = self.delta_t_h
            clock.clock_style = 1
            clock.update(timestring=self.curr_time_str)
            # print("loop - current action phase started:{:8.2f}".format(self.act_loop_start_time - self.mngr_start_minute_zero))
            # time management   phase                                                           ENDED   -

            # measurement       phase                                                           START   -
            self.measuring_phase()
            # measurements = SeSe.EnvironmentalReadings()
            # measurements.show_actual_data(code=7, scroll_speed=0.04, delta_t_h=self.delta_t_h)
            # measurement       phase                                                           ENDED   -

            print("\nIncomming:")
            for pin, state in self.pin_info.items():
                if state['used']: print("{:>3} - {}".format(pin, state))

            if self.looptime_changed or False:
                # ought status      phase                                                           START   -
                self.update_ought_status()
                # ought status      phase                                                           ENDED   -

                print("\nOnUpdate:")
                for pin, state in self.pin_info.items():
                    if state['used']: print("{:>3} - {}".format(pin, state))

                # command setup     phase                                                           START   -
                self.update_commands()
                # command setup     phase                                                           ENDED   -

                # command issue     phase                                                           START   -
                if self.actual_commands: self.issue_commands()
                # command issue     phase                                                           ENDED   -

            print("\nAfterCommands:")
            for pin, state in self.pin_info.items():
                if state['used']: print("{:>3} - {}".format(pin, state))

            action_end = time.time()
            action_end_time_soll = (self.loop_counter + 1) * self.heartbeat
            wait_till_loopend = action_end_time_soll - (action_end - self.mngr_start_minute_zero)

            if wait_till_loopend > 0:
                time.sleep(wait_till_loopend)
                # print("---\n{}\n---".format(wait_till_loopend))
            self.act_loop_end_time = time.time()
            self.loop_counter += 1

            self.update_conditions()

            # print("loop - current action phase   ended:{:8.2f}".
            #       format(self.act_loop_end_time - self.mngr_start_minute_zero))

            self.time_at_prevs_loop = self.time_at_start_loop

    def gpio_switch_period(self, timespan: int, heartbeat: int, pin_id: int, event_name: str):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin_id, GPIO.OUT)  # chosen GPIO pin is used to send signals out
        localtime = 0

        GPIO.output(pin_id, 1)  # switch gpio pin on
        self.pin_info[pin_id]['state'] = True
        while localtime < timespan:
            print("event  : '{:>15}' on pin {:>3}  - <localtime>: {:5.2f}".format(event_name, pin_id, localtime))
            # further actions while cycling
            time.sleep(heartbeat)
            localtime += heartbeat

        GPIO.output(pin_id, 0)
        self.pin_info[pin_id]['state'] = False
        msg_ev01 = "event   '{}' ended!".format(event_name)
        print(msg_ev01)
        # GPIO.cleanup ()
        # print (message_WS01)
        return msg_ev01

    def gpio_switch_on(self, pin_id: int, process_name: str):
        if GPIO:
            GPIO.setwarnings(False)
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(pin_id, GPIO.OUT)  # chosen gpio pin is used to send signals out
            GPIO.output(pin_id, 1)  # switch gpio pin on
        else: print("ISSUED: pin: {:>2}     --> {:>3}".format(pin_id, "ON"))
        self.pin_info[pin_id]['state'] = True
        msg_pr01 = ("process: '{:>15}' on pin {:>3}  -              {:>3}".format(process_name, pin_id, "ON"))
        print(msg_pr01)
        return msg_pr01

    def gpio_switch_off(self, pin_id: int, process_name: str):
        if GPIO:
            GPIO.setwarnings(False)
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(pin_id, GPIO.OUT)  # chosen gpio pin is used to send signals out
            GPIO.output(pin_id, 0)  # switch gpio pin on
        else: print("ISSUED: pin: {:>2}     --> {:>3}".format(pin_id, "OFF"))
        self.pin_info[pin_id]['state'] = False
        msg_pr02 = ("process: '{:>15}' on pin {:>3}  -              {:>3}".format(process_name, pin_id, "OFF"))
        print(msg_pr02)
        return msg_pr02


if __name__ == "__main__":
    a = GpioPin(_id_ = 7)
    for k, v in vars(a).items():
        print("{:>12}: {}".format(k, v))