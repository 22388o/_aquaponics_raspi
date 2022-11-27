def ap_gpio_switch_swap(gpio_id: int, swap_to: int):
    import RPi.GPIO as GPIO
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(gpio_id, GPIO.OUT)  # chosen gpio pin is used to send signals out
    GPIO.output(gpio_id, swap_to)
    if swap_to:
        statestring = "ON"
    else:
        statestring = "OFF"
    message_01 = "GPIO Nr." + str(gpio_id) + " was turned " + statestring
    print(message_01)
    return message_01


def ap_gpio_switch_period(timespan: int, heartbeat: int, gpio_id: int, process_name: str):
    import time
    import RPi.GPIO as GPIO
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(gpio_id, GPIO.OUT)  # chosen gpio pin is used to send signals out
    
    localtime = 0
    
    GPIO.output(gpio_id, 1)  # switch gpio pin on
    while localtime < timespan:
        print("process: '{}' local time <localtime>: {:5.2f}".format(process_name, localtime))
        # further actions while cycling
        time.sleep(heartbeat)
        localtime += heartbeat

    GPIO.output(gpio_id, 0)
    message_ws01 = "process '{}' ended!".format(process_name)
    # GPIO.cleanup ()
    # print (message_WS01)
    return message_ws01


def ap_gpio_switch_test(timespan: int, heartbeat: int, gpio_in_id: int, gpio_out_id: int, process_name: str,
                        datestring: str = '2018-03-20',
                        timestring: str = '10:12'):
    import time
    import RPi.GPIO as GPIO
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    # GPIO.cleanup()
    GPIO.setup(gpio_out_id, GPIO.OUT)  # chosen gpio pin is used to send signals out
    GPIO.setup(gpio_in_id, GPIO.IN)  # chosen gpio pin is used to receive signals

    answer_message = "Process: " + process_name + ". " + str(datestring) + " " + timestring

    answer_message += "\n" + "Starting arguments:\n- timespan:  " + str(timespan) + "\n- heartbeat: " + str(heartbeat)

    answer_message += "\n" + "process:      '" + process_name + "' started."

    print(answer_message)

    # (WLT) water level test for grow bed (GB)

    msg_wltgb00 = "STATE:        '{}' says: GPIO pin Nr.{} was ordinarly turned:   ON".format(process_name, gpio_out_id)
    msg_wltgb01 = "STATE:        '{}' says: GPIO pin Nr.{} at Test begin:          OFF".format(process_name, gpio_in_id)
    msg_wltgb02 = "!!! ERROR !!! '{}' says: GPIO pin Nr.{} at Test begin:          ON".format(process_name, gpio_in_id)
    msg_wltgb021= "process:      '{}' says: Tier-1 started".format(process_name)
    msg_wltgb022= "process:      '{}' says: Tier-2 Started".format(process_name)
    
    msg_wltgb03 = "!!! ERROR !!! '{}' says: GPIO pin Nr.{} at End of Tier-1:       OFF\n" \
                  " - Tier-1 ended on timelimit.".format(process_name, gpio_in_id)
    msg_wltgb04 = "STATE:        '{}' says: GPIO pin Nr.{} at End of Tier-1:       ON\n" \
                  " - Tier-1 ended by signal".format(process_name, gpio_in_id)
    msg_wltgb041= "STATE:        '{}' says: GPIO pin Nr.{} at End of Tier-1:       ON\n" \
                  " - Tier-1 ended on timelimit. (switch stuck)".format(process_name, gpio_in_id)
    msg_wltgb05 = "STATE:        '{}' says: GPIO pin Nr.{} at End of 2st phase:    OFF".format(process_name, gpio_in_id)
    msg_wltgb06 = "!!! ERROR !!! '{}' says: GPIO pin Nr.{} at End of 2st phase:    ON".format(process_name, gpio_in_id)
    msg_wltgb07 = "WARNING:      '{}' says: GPIO pin Nr.{} during    Tier-1:       OFF\n" \
                  " - fell during process...".format(process_name, gpio_in_id)
    msg_wltgb08 = "process:      '{}' says: Tier-1 Ended".format(process_name)
    msg_wltgb10 = "STATE:        '{}' says: GPIO pin Nr.{} was ordinarly turned:   ON".format(process_name, gpio_out_id)
    msg_wltgb11 = "WARNING:      '{}' says: GPIO pin Nr.{} during    Tier-2:       ON\n" \
                  " - switched on during Tier-2 only...".format(process_name, gpio_in_id)
    msg_wltgb12 = "STATE:        '{}' says: GPIO pin Nr.{} at End of Tier-2:       OFF\n" \
                  " - Tier-2 ended by signal".format(process_name, gpio_in_id)
    msg_wltgb13 = "!!! ERROR !!! '{}' says: GPIO pin Nr.{} at End of Tier-2:       xx\n" \
                  " - Tier-2 ended on timelimit. (switch stuck)".format(process_name, gpio_in_id)
    msg_wltgb14 = "process:      '{}' says: Tier-2 Ended".format(process_name)
    msg_wltgb15 = "!!! ERROR !!! '{}' says: GPIO pin Nr.{} at Test end:            ON\n" \
                  " - compare with next test begin!".format(process_name, gpio_in_id)
    msg_wltgb16 = "STATE:        '{}' says: GPIO pin Nr.{} at Test end:            OFF".format(process_name, gpio_in_id)
    msg_wltgb17 = "process:      '{}' says: GPIO pin Nr.{}: OFF.\n" \
                  " Report done, returned and quit.".format(process_name, gpio_out_id)

    GPIO.output(gpio_out_id, 1)  # switch gpio pin on
    
    if GPIO.input(gpio_in_id) is True:
        answer_message += "\n" + msg_wltgb02
        ON_init = True
        was_on = True
        print(msg_wltgb02)
    else:
        answer_message += "\n" + msg_wltgb01
        ON_init = False
        was_on = False
        print(msg_wltgb01)

    ON_ph1 = None
    ON_ph2 = None
    ON_init = None

    phase1 = True
    localtime = 0

    answer_message += "\n" + msg_wltgb00
    answer_message += "\n" + msg_wltgb021
    print(msg_wltgb00 + "\n" + msg_wltgb021)
    print("process: Tier-1 <localtime>: {:>4.1}".format(localtime))

    while phase1:

        # further actions while cycling
        time.sleep (heartbeat)
        localtime += heartbeat
        if (GPIO.input(gpio_in_id) is True) and (not was_on):
            answer_message += "\n" + msg_wltgb04
            print(msg_wltgb04)
            was_on = True
            ON_ph1 = True
            phase1 = False
        elif (GPIO.input(gpio_in_id) is False) and was_on:
            answer_message += "\n" + msg_wltgb07
            print(msg_wltgb07)
            was_on = False
        elif localtime > timespan and was_on:
            answer_message += "\n" + msg_wltgb041
            print(msg_wltgb041)
            ON_ph1 = True
            phase1 = False
        elif localtime > timespan and not was_on:
            answer_message += "\n" + msg_wltgb03
            print(msg_wltgb03)
            ON_ph1 = False
            phase1 = False
        else:
            print("process: Tier-1 <localtime>: " + str(localtime))
            phase1 = True

    answer_message += "\n" + msg_wltgb08
    print(msg_wltgb08)

    if ON_ph1:
        was_off = False
    else:
        was_off = True

    phase2 = True
    localtime = 0
    answer_message += "\n" + msg_wltgb022
    print(msg_wltgb022)
    print("process: Tier-2 <localtime>: " + str(localtime))
    
    while phase2:
        time.sleep (heartbeat)
        localtime += heartbeat
        if (GPIO.input(gpio_in_id) is True) and was_off:
            answer_message += "\n" + msg_wltgb11
            print(msg_wltgb11)
            was_off = False
            phase2 = True
        elif (GPIO.input(gpio_in_id) is False) and not was_off:
            answer_message += "\n" + msg_wltgb12
            print(msg_wltgb12)
            ON_ph1 = False
            phase2 = False
        elif localtime > timespan:
            answer_message += "\n" + msg_wltgb13
            print(msg_wltgb13)
            ON_ph2 = True
            phase2 = False
        else:
            print("process: Tier-2 <localtime>: " + str(localtime))
            phase2 = True

    answer_message += "\n" + msg_wltgb14
    print(msg_wltgb14)

    if GPIO.input(gpio_in_id) is True:
        ON_ph2 = True
        answer_message += "\n" + msg_wltgb15
        print(msg_wltgb15)
    else:
        ON_ph2 = False
        answer_message += "\n" + msg_wltgb16
        print(msg_wltgb16)

    GPIO.output(gpio_out_id, 0)
    # GPIO.cleanup ()
    answer_message += "\n" + msg_wltgb17 + "\n----------------------------------------\n"
    print(msg_wltgb17)

    print("\n   ---------------------------")
    print("   - Summary at process end: -")
    print("   ---------------------------")

    print(answer_message)
    # GPIO.cleanup ()
    return answer_message


def pintest(gpio_in_id):
    import time
    import RPi.GPIO as GPIO
    GPIO.setwarnings (False)
    GPIO.setmode(GPIO.BCM)
    GPIO.cleanup()
    GPIO.setup(gpio_in_id, GPIO.IN) # chosen gpio pin is used to receive signals

    while True:
        if GPIO.input(gpio_in_id) is True:
            print("yepp")
        else:
            print("nope")


GPIO_db = [
    {'nr': 0,   'on': None, 'use': '3.3'},  {'nr': 0,   'on': None, 'use': '5'},    # 01 - 02   -   -
    {'nr': 2,   'on': None, 'use': 'act'},  {'nr': 0,   'on': None, 'use': '5'},    # 03 - 04   -   l
    {'nr': 3,   'on': None, 'use': 'act'},  {'nr': 0,   'on': None, 'use': 'gnd'},  # 05 - 06   -   g
    {'nr': 4,   'on': None, 'use': 'act'},  {'nr': 14,  'on': True, 'use': 'act'},  # 07 - 08   -   p
    {'nr': 0,   'on': None, 'use': 'gnd'},  {'nr': 15,  'on': True, 'use': 'act'},  # 09 - 10   -   p
    {'nr': 17,  'on': None, 'use': 'act'},  {'nr': 18,  'on': True, 'use': 'act'},  # 11 - 12   -   p
    {'nr': 27,  'on': None, 'use': 'act'},  {'nr': 0,   'on': None, 'use': 'gnd'},  # 13 - 14   -   -
    {'nr': 22,  'on': None, 'use': 'act'},  {'nr': 23,  'on': None, 'use': 'act'},  # 15 - 16   -   -
    {'nr': 0,   'on': None, 'use': '3.3'},  {'nr': 24,  'on': None, 'use': 'act'},  # 17 - 18   -   -
    {'nr': 10,  'on': None, 'use': 'act'},  {'nr': 0,   'on': None, 'use': 'gnd'},  # 19 - 20   -   -
    {'nr': 9,   'on': None, 'use': 'act'},  {'nr': 25,  'on': None, 'use': 'act'},  # 21 - 22   -   -
    {'nr': 11,  'on': None, 'use': 'act'},  {'nr': 8,   'on': None, 'use': 'act'},  # 23 - 24   -   -
    {'nr': 0,   'on': None, 'use': 'gnd'},  {'nr': 7,   'on': True, 'use': 'act'},  # 25 - 26   -   p
    {'nr': 0,   'on': None, 'use': 'sd'},   {'nr': 0,   'on': None, 'use': 'sc'},   # 27 - 28   -   -
    {'nr': 5,   'on': None, 'use': 'act'},  {'nr': 0,   'on': None, 'use': 'gnd'},  # 29 - 30   -   -
    {'nr': 6,   'on': None, 'use': 'act'},  {'nr': 12,  'on': None, 'use': 'act'},  # 31 - 32   -   p
    {'nr': 13,  'on': None, 'use': 'act'},  {'nr': 0,   'on': None, 'use': 'gnd'},  # 33 - 34   -   -
    {'nr': 19,  'on': None, 'use': 'act'},  {'nr': 16,  'on': None, 'use': 'act'},  # 35 - 36   -   p
    {'nr': 26,  'on': None, 'use': 'act'},  {'nr': 20,  'on': None, 'use': 'act'},  # 37 - 38   -   p
    {'nr': 0,   'on': None, 'use': 'gnd'},  {'nr': 21,  'on': None, 'use': 'act'},  # 39 - 40   -   p
    ]

if __name__ == "__main__":
    import time
    times = int(input(      "how many loops: (integer) "))
    timespan = int(input(   "how long ON:    (integer) "))
    timesleep = float(input("how long OFF:   (float)   "))
    for _ in range(times):
        for pin_sqc in range(1, 40, 2):
            data = GPIO_db[pin_sqc]
            if data['nr'] and data['on']:
                print("sequence nr: {:>2}, gpio_id: {:>2}".format(pin_sqc + 1, data['nr']))
                ap_gpio_switch_period(timespan=timespan, heartbeat=1, gpio_id=data['nr'], process_name="WaterStream")
                time.sleep(timesleep)

    '''    
    ap_gpio_switch_swap(gpio_id=18, swap_to=False)
    #ap_gpio_switch_test(timespan=30, heartbeat = 1, gpio_in_id= 21, gpio_out_id=14, process_name="WaterLevelTest_GB", datestring="2018-03-22", timestring="15:02")
    #pintest(21)
    '''
