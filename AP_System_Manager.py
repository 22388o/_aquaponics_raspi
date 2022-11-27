def ap_system_manager(list_of_WaterStream_times=None,
                      list_of_WaterLevelTest_GB_times=None,
                      list_of_Feeding_times=None,
                      list_of_Reporting_times=None,
                      list_of_Light_1_periods=None):
    """
    Main module to controll water circulation of home made aquaponic system.
    Module is responsible for:
    - actual waterstream controll
    - reading in circulation times
    - operating and monitoring the systems related sensors
    - creating, archiving and sending relevant system status information to external media, e.g.: email, blockchain
    sending will probably leave current module, as outside communication will be migrated to a different module.
    :param list_of_pumpingtimes:
    :return:
    """

    import os
    import time
    import time_related as tr
    try:
        import RPi.GPIO as GPIO
    except ImportError:
        GPIO = False
    import gpio_operations as pin
    import environmental_readings as er
    import console_display as cd
    from sense_hat import SenseHat
    import list_operations as lo
    import clock as clock
    import email_setup as email_setup

    sense = SenseHat()
    
    GPIO.setwarnings (False)
    GPIO.cleanup ()
    GPIO.setmode(GPIO.BCM)

    if not list_of_WaterStream_times:
        list_of_WaterStream_times = []
    if not list_of_WaterLevelTest_GB_times:
        list_of_WaterLevelTest_GB_times = []
    if not list_of_Feeding_times:
        list_of_Feeding_times = []
    if not list_of_Reporting_times:
        list_of_Reporting_times = []
    if not list_of_Light_1_periods:
        list_of_Light_1_periods = []


    report_text_subject = ""
    report_text_body = ""

    function_dict = {'WaterStream':      {'gpio_id': 14, 'gpio_direction': GPIO.OUT},
                     'Feeding':          {'gpio_id': 15, 'gpio_direction': GPIO.OUT},
                     'Light_1':          {'gpio_id': 18, 'gpio_direction': GPIO.OUT},
                     'Light_2':          {'gpio_id': 7,  'gpio_direction': GPIO.OUT},
                     'Ventillation':     {'gpio_id': 1,  'gpio_direction': GPIO.OUT},
                     'Shading':          {'gpio_id': 12, 'gpio_direction': GPIO.OUT},
                     'WaterLevel_GB':    {'gpio_id': 21, 'gpio_direction': GPIO.IN} }

    current_system_state = {'WaterStream_recent': 'never',
                            'WaterLevelTest_GB_recent': 'never',
                            'Feeding_recent': 'never',
                            'Reporting_recent': 'never',
                            'Light_1_ON': False,
                            'Light_2_ON': False,
                            'Ventillation_ON': False,
                            'Shades_DOWN': False}
    
    act_env_readings = {'temperature': 0,
                            'humidity': 0,
                            'air_pressure': 0}

    hist_env_readings = {'temperature': [],
                            'humidity': [],
                            'air_pressure': []}

    moav_env_readings = {'temperature': 0,
                            'humidity': 0,
                            'air_pressure': 0}
    ''' Tasks are divided into 2 groups:
        - Events: these processes hapen in one System heartbeat. Start and finish in the same sequence.
                  WaterStream, WaterLevelTest, Feeding, Reporting, MovingShades.
        - States: prolonged changes in the System State. Changes last multiple heartbeats.
                  Turning Lights ON/OFF, Turning Vent. ON/OFF, Moving Shades (!!!-needs clarification)
                  When Lights and Ventillation are On, these processes constantly use current flowing through the Hub meaning the ON State constantly requires the Raspberry to have a GPIO pin ON!
                  The moving of the Shades is an Event setting the System state for multiple heartbeats. None of the states require current thou.
                  However the bidirectional moving requires 2 relais: one in each direction!'''

    
    task_table = {'WaterStream':            False,  # if task is due  
                  'WaterLevelTest_GB':      False,  # if task is due
                  'Feeding':                False,  # if task is due
                  'Reporting':              False,  # if task is due
                  'Turn_Light_1_ON':        False,  # if state change is due
                  'Turn_Light_1_OFF':       False,  # if state change is due
                  'Turn_Light_2_ON':        False,  # if state change is due
                  'Turn_Light_2_OFF':       False,  # if state change is due
                  'Turn_Ventillation_ON':   False,  # if state change is due
                  'Turn_Ventillation_OFF':  False,  # if state change is due
                  'Lower_Shades':           False,  # if state change is due
                  'Raise_Shades':           False}  # if state change is due
    
    '''
    for task in list(task_table.keys()):
        task_table[task]= False
    print (task_table)
    '''
    
    
    for task, desc in list(function_dict.items()):
        GPIO.setup(desc['gpio_id'], desc['gpio_direction']) # actual gpio pin is used to send signals in or out
        if desc['gpio_direction'] == GPIO.OUT:
            GPIO.output(desc['gpio_id'], 0)  # actual gpio is switched off

    GPIO.cleanup ()
    
    end = False
    delta_t_h = -2  # Time difference between Raspberry time and Actual time in hours > tR - tA
    delta_t_m = 0  # Time difference between Raspberry time and Actual time in minutes > tR - tA
    heartbeatlength = 10
    ma_increment = 12
    n_th = 0  # couter of current loop
     
    while not end:
        '''---------------------
        - time reading - START -
        ---------------------'''
        system_time = time.time() - 3600 * delta_t_h - 60 * delta_t_m
        detailed_system_time = time.gmtime(system_time)
        ai_year = int(time.strftime("%Y", detailed_system_time))  # Actual Integer year
        ai_month = int(time.strftime("%m", detailed_system_time))  # Actual Integer month
        ai_day = int(time.strftime("%d", detailed_system_time))  # Actual Integer month
        ai_hour = int(time.strftime("%H", detailed_system_time))  # Actual Integer hour
        ai_min = int(time.strftime("%M", detailed_system_time))  # Actual Integer min

        as_year = lo.data_leading_zero (integer=ai_year, digits=4)
        as_month = lo.data_leading_zero (integer=ai_month, digits=2)
        as_day = lo.data_leading_zero (integer=ai_day, digits=2)
        as_hour = lo.data_leading_zero (integer=ai_hour, digits=2)
        as_min = lo.data_leading_zero (integer=ai_min, digits=2)

        current_date_string = as_year + "-" + as_month + "-" + as_day
        current_time_string = as_hour + ":" + as_min
        # print("\nmeasured systemtime <system_time>: " + str(system_time))
        print("\n --------------------------------------------------------------")
        print(" - Starting upcomming Loop. -                Date: " + current_date_string + " -")
        print(" --------------------------------------------------------------\n")
        cd.console_display_6(string=current_time_string, char=chr(9608), charset=False)

        '''---------------------
        - time reading - ENDED -
        ---------------------'''

        '''-----------------------
        - sensor reading - START -
        -----------------------'''
        print("\n -------------------------------------------")
        print(" - Environmental data processing:          -")
        print(" -------------------------------------------")
        last_env_readings = dict(act_env_readings)
        act_env_readings.update(er.sense_hat_env_data(7)) 
        '''print("\n>> actual environmental readings:")
        for k in sorted(list(act_env_readings.keys())):
            print(" o " + k + ": " + str(act_env_readings[k]))'''
        hist_env_readings = lo.list_dict_fifo_extend_w_dist(listdict=hist_env_readings,
                                                         dict_in=act_env_readings,
                                                         max_length=ma_increment)

        moav_env_readings = list_dict_moav_calc(dict_in=hist_env_readings)
        print(">> Environmental readings. (Moving averages for the last " + str(round((heartbeatlength * len(list(hist_env_readings.values())[0])) / 60.0 ,1)) + " mins):")
        for k in sorted(list(moav_env_readings.keys())):
            print(" o " + k + ": " + str(moav_env_readings[k]))
        # print("\n -------------------------------------------")
        # print(" - Environmental data processing: FINISHED -")
        # print(" -------------------------------------------")

        '''-----------------------
        - sensor reading - ENDED -
        -----------------------'''

        print(" -------------------------------------------")
        print(" - Condition check for Events  :           -")
        print(" -------------------------------------------")        
        cond_waterstream_answer =       condition_check_event(task='WaterStream',
                                                              schedule=list_of_WaterStream_times,  # list of times when task is scheduled
                                                              current_system_state=current_system_state,  # feeding..., ..._in_act_minute
                                                              current_date_string=current_date_string,
                                                              current_time_string=current_time_string)
        init_waterstream =              cond_waterstream_answer['init_signal']
        current_system_state =          cond_waterstream_answer['current_system_state']

        cond_waterleveltest_gb_answer = condition_check_event(task='WaterLevelTest_GB',
                                                              schedule=list_of_WaterLevelTest_GB_times,  # list of times when task is scheduled
                                                              current_system_state=current_system_state,  # feeding..., ..._in_act_minute
                                                              current_date_string=current_date_string,
                                                              current_time_string=current_time_string)
        init_waterleveltest_gb =        cond_waterleveltest_gb_answer['init_signal']
        current_system_state =          cond_waterleveltest_gb_answer['current_system_state']
        
        cond_feeding_answer =           condition_check_event(task='Feeding',
                                                              schedule=list_of_Feeding_times,  # list of times when task is scheduled
                                                              current_system_state=current_system_state,  # feeding..., ..._in_act_minute
                                                              current_date_string=current_date_string,
                                                              current_time_string=current_time_string)
        init_feeding =                  cond_feeding_answer['init_signal']
        current_system_state =          cond_feeding_answer['current_system_state']
        
        cond_reporting_answer =         condition_check_event(task='Reporting',
                                                              schedule=list_of_Reporting_times,  # list of times when task is scheduled
                                                              current_system_state=current_system_state,  # feeding..., ..._in_act_minute
                                                              current_date_string=current_date_string,
                                                              current_time_string=current_time_string)
        init_reporting =                cond_reporting_answer['init_signal']
        current_system_state =          cond_reporting_answer['current_system_state']

        cond_light_1_swap_answer =      condition_check_state(task='Light_1',
                                                              schedule=list_of_Light_1_periods,  # list of periods when task is scheduled
                                                              current_system_state=current_system_state,  # feeding..., ..._in_act_minute
                                                              current_date_string=current_date_string,
                                                              current_time_string=current_time_string)
        turn_light_1_on =               cond_light_1_swap_answer['turn_Light_1_on']
        turn_light_1_off=               cond_light_1_swap_answer['turn_Light_1_off'] 
        current_system_state =          cond_light_1_swap_answer['current_system_state']

        cond_ventillation_swap_answer = {'turn_Ventillation_on': False, 'turn_Ventillation_off': False, 'current_system_state': current_system_state}
        turn_ventillation_on =          cond_ventillation_swap_answer['turn_Ventillation_on']
        turn_ventillation_off =         cond_ventillation_swap_answer['turn_Ventillation_off']
        current_system_state =          cond_ventillation_swap_answer['current_system_state']

        # print(" -------------------------------------------")
        # print(" - Condition check of processes:  FINISHED -")
        # print(" -------------------------------------------")

        print(" -------------------------------------------")
        print(" - Condition check for States  :           -")
        print(" -------------------------------------------") 

        '''--------------------------------------------------------------------
        - updating task table, if True signals were received - STARTED        -
        --------------------------------------------------------------------'''
        print(" -------------------------------------------")
        print(" - Task Table updated state:               -")
        print(" -------------------------------------------")

        if init_waterstream:
            task_table['WaterStream'] = True
        if init_waterleveltest_gb:
            task_table['WaterLevelTest_GB'] = True
        if init_feeding:
            task_table['Feeding'] = True
        if init_reporting:
            task_table['Reporting'] = True
        if turn_light_1_on:
            task_table['Turn_Light_1_ON'] = True
        if turn_light_1_off:
            task_table['Turn_Light_1_OFF'] = True
        if turn_ventillation_on:
            task_table['Turn_Ventillation_ON'] = True
        if turn_ventillation_off:
            task_table['Turn_Ventillation_OFF'] = True

        for k in sorted(list(task_table.keys())):
            print(" o " + k + ": " + str(task_table[k]))
        # print(" -------------------------------------------")
        # print(" - Task Table updating:           FINISHED -")
        # print(" -------------------------------------------")

        '''--------------------------------------------------------------------
        - updating task table, if True signals were received - FINISHED       -
        --------------------------------------------------------------------'''

        print(" -------------------------------------------")
        print(" - Executing tasks:                        -")
        print(" -------------------------------------------")

        # Lights
        
        if task_table['Turn_Light_1_ON'] or task_table['Turn_Light_1_OFF']:
            if task_table['Turn_Light_1_ON'] and not task_table['Turn_Light_1_OFF']:
                print(">>> Light_1: turned ON                       <<<")
                pin.ap_gpio_switch_swap(gpio_id=function_dict['Light_1']['gpio_id'], swap_to=True)
                current_system_state['Light_1_ON'] = True
                task_table['Turn_Light_1_ON'] = False
            elif task_table['Turn_Light_1_OFF'] and not task_table['Turn_Light_1_ON']:
                print(">>> Light_1: turned OFF                       <<<")
                pin.ap_gpio_switch_swap(gpio_id=function_dict['Light_1']['gpio_id'], swap_to=False)
                current_system_state['Light_1_ON'] = False
                task_table['Turn_Light_1_OFF'] = False
            else:
                print(">>> Light_1: contradiction, reseting tasks    <<<")
                task_table['Turn_Light_1_ON']  = False
                task_table['Turn_Light_1_OFF'] = False    
        else:
            print("...no change for Light_1!")

        # WaterStream

        if task_table['WaterStream']:
            print(">>> Water Stream: INITIATED                       <<<")
            pin.ap_gpio_switch_period (timespan=40, heartbeat = 2,
                                       gpio_id=function_dict['WaterStream']['gpio_id'],
                                       process_name="WaterStream")
            task_table['WaterStream'] = False
            print(">>> Water Stream: FINISHED                        <<<")         
        else:
            print("...no pumping!")

        # WaterLevelTest_GB

        if task_table['WaterLevelTest_GB']:
            print(">>> GrowBed WaterLevelTest: INITIATED             <<<")
            gpio_test_result = pin.ap_gpio_switch_test (timespan=20,
                                           heartbeat=0.5,
                                           gpio_in_id=function_dict['WaterLevel_GB']['gpio_id'],
                                           gpio_out_id=function_dict['WaterStream']['gpio_id'],
                                           process_name='WaterLevelTest_GB',
                                           datestring=current_date_string,
                                           timestring=current_time_string)
            print(gpio_test_result)
            report_text_body += gpio_test_result
            task_table['WaterLevelTest_GB'] = False
            print(">>> GrowBed WaterLevelTest: FINISHED              <<<")         
        else:
            print("...no water level testing!")

        # Feeding
        
        if task_table['Feeding']:
            print(">>> Feeding: INITIATED                            <<<")
            pin.ap_gpio_switch_period (timespan=20, heartbeat = 0.5,
                                       gpio_id=14, # temporarly changed!
                                       process_name="Feeding")
            task_table['Feeding'] = False
            print(">>> Feeding: FINISHED                             <<<")         
        else:
            print("...no feeding!")

        # Reporting

        if task_table['Reporting']:
            print(">>> Reporting: INITIATED                          <<<")
            report_text_body += " --- Current System State ---\n"
            for k in sorted(list(current_system_state.keys())):
                report_text_body += " o " + k + ": " + str(current_system_state[k]) + "\n"
            report_text_body += " --- Current Environmental data ---\n"
            for k in sorted(list(moav_env_readings.keys())):
                report_text_body += " o " + k + ": " + str(moav_env_readings[k]) + "\n"
            
            email_setup.email_send_aquaponia(To="szillerke@gmail.com",
                                             message_subject='Status_report_' + current_date_string + "_" + current_time_string,
                                             message_body=report_text_body)
            task_table['Reporting'] = False
            report_text_body = ""
            print(">>> Reporting: FINISHED                           <<<")         
        else:
            print("...no reporting!")
            
        print(" -------------------------------------------")
        print(" - Current system state:                   -")
        print(" -------------------------------------------")
       
            
        for k in sorted(list(current_system_state.keys())):
            print(" o " + k + ": " + str(current_system_state[k]))
        
        if n_th % 3 == 0:
            sense.show_message('T:'+str(moav_env_readings['temperature'])+"'C",
                               scroll_speed=0.05,
                               text_colour=[255, 0, 0])
            clock.update(time_string=current_time_string)
        elif n_th % 3 == 1:
             sense.show_message('rH:'+ str(moav_env_readings['humidity'])+"%",
                                scroll_speed=0.05,
                                text_colour=[0,0,255])
             clock.update(time_string=current_time_string)
        elif n_th % 3 == 2:
            sense.show_message('p:'+ str(moav_env_readings['air_pressure']) +'bar',
                               scroll_speed=0.05,
                               text_colour=[255,255,0])
            clock.update(time_string=current_time_string)
        else:
            clock.update(time_string=current_time_string)
        n_th += 1
        time.sleep(heartbeatlength)
        
    
def list_dict_moav_calc(dict_in:dict):
    answer={}
    for k, l in list(dict_in.items()):
        answer[k] = round(sum(l) / float(len(l)), 1)
    return answer


def condition_check_event (task:str,
                           schedule:list=[],  # list of times when task is scheduled
                           task_specific_conditions=True,
                           current_environmental_data:dict={}, # temperature, humidity, pressure...  
                           current_system_readings:dict={},  # water level, wheel position
                           current_system_state:dict={},  # feeding..., ..._in_act_minute
                           current_date_string:str='2018-03-15',
                           current_time_string:str='00:00'):
    init_signal = False
    str_len = len(task)
    placeholder = (24-str_len) * " "
    task_specific_conditions = True # to be able to extend conditions with task specific statements!!!
    if (current_time_string in schedule) and task_specific_conditions: 
        print(" - current time for " + task + placeholder + " IS  scheduled...")
        if current_time_string != current_system_state[task + '_recent']:
            task_iam = False
        else:
            task_iam = True
        if task_iam:
            print("   ...but process has already run.")
            init_signal = False
        if not task_iam:
            init_signal = True
            current_system_state[task + '_recent'] = current_time_string
            print("   ... < " + task + "_recent > set to: " + current_system_state[task +'_recent'])
    else:
        init_signal = False
        placeholder = (24-str_len) * " "
        print(" - current time for " + task + ":" +  placeholder + "NOT scheduled!")
    return {'init_signal': init_signal, 'current_system_state': current_system_state}


def condition_check_state (task:str,
                           schedule:list=[],  # list of times when task is scheduled
                           current_environmental_data:dict={}, # temperature, humidity, pressure...  
                           current_system_readings:dict={},  # water level, wheel position
                           current_system_state:dict={},  # feeding..., ..._in_act_minute
                           current_date_string:str='2018-03-15',
                           current_time_string:str='00:00'):
    import time_related as tr     
    init_signal = False
    str_len=len(task)
    placeholder = (24-str_len) * " "
    nth_of_period = 0
    tot_of_period = len(schedule)
    should_be_ON = False
    while nth_of_period < tot_of_period and not should_be_ON:
        should_be_ON = should_be_ON or tr.check_if_time_in_period(time_str=current_time_string,
                                                                  start_str=schedule[nth_of_period]['ON'],
                                                                  finish_str=schedule[nth_of_period]['OFF'])
        nth_of_period += 1
    # print(str(task) + " <should_be_ON>: " + str(should_be_ON))
    is_ON = current_system_state[task + '_ON']
    #print(str(task) + " <is_ON> :       " + str(is_ON))
    answer_turn_on = False
    answer_turn_off = False
    if should_be_ON and not is_ON:
        answer_turn_on = True
    if not should_be_ON and is_ON:
        answer_turn_off = True    
    return {'turn_' + task + '_on': answer_turn_on, 'turn_' + task + '_off': answer_turn_off, 'current_system_state': current_system_state}


if __name__ == "__main__":
    import list_operations as lo
    list_of_WaterStream_times = ['00:00', '00:10', '00:20', '00:30', '00:40', '00:50',
                                 '01:00', '01:10', '01:20', '01:30', '01:40', '01:50',
                                 '02:00', '02:10', '02:20', '02:30', '02:40', '02:50',
                                 '03:00', '03:10', '03:20', '03:30', '03:40', '03:50',
                                 '04:00', '04:10', '04:20', '04:30', '04:40', '04:50',
                                 '05:00', '05:10', '05:20', '05:30', '05:40', '05:50',
                                 '06:00', '06:10', '06:20', '06:30', '06:40', '06:50',
                                 '07:00', '07:10', '07:20', '07:30', '07:40', '07:50',
                                 '08:00', '08:10', '08:20', '08:30', '08:40', '08:50',
                                 '09:00', '09:10', '09:20', '09:30', '09:40', '09:50',
                                 '10:00', '10:10', '10:20', '10:30', '10:40', '10:50',
                                 '11:00', '11:10', '11:20', '11:30', '11:40', '11:50',
                                 '12:00', '12:10', '12:20', '12:30', '12:40', '12:50',
                                 '13:00', '13:10', '13:20', '13:30', '13:40', '13:50',
                                 '14:00', '14:10', '14:20', '14:30', '14:40', '14:50',
                                 '15:00', '15:10', '15:20', '15:30', '15:40', '15:50',
                                 '16:00', '16:10', '16:20', '16:30', '16:40', '16:50',
                                 '17:00', '17:10', '17:20', '17:30', '17:40', '17:50',
                                 '18:06', '18:10', '18:20', '18:30', '18:40', '18:50',
                                 '19:00', '19:10', '19:20', '19:30', '19:40', '19:50',
                                 '20:00', '20:10', '20:20', '20:30', '20:40', '20:50',
                                 '21:00', '21:10', '21:20', '21:30', '21:40', '21:50',
                                 '22:00', '22:10', '22:20', '22:30', '22:40', '22:50',
                                 '23:00', '23:10', '23:20', '23:30', '23:40', '23:50']
    list_of_Feeding_times = ['20:15']
    list_of_WaterLevelTest_GB_times = ['02:15', '08:15', '14:15', '20:15']
    list_of_Reporting_times = ['20:18', '08:18']
    list_of_Light_1_periods = [{'ON': '23:00', 'OFF': '05:00'},
                               {'ON': '20:01', 'OFF': '22:30'}]

    print("\nWater pump will turn on at following times: <list_WaterStream_times>")
    lo.list_display_dundle(list_in=list_of_WaterStream_times,
                           sequence_length=6)

    print("\nFeeding wheel will be activated at following times: <list_of_Feeding_times>")
    lo.list_display_dundle(list_in=list_of_Feeding_times,
                           sequence_length=6)

    print("\nWater level sensor will be tested at following times: <list_of_WaterLevelTest_GB_times>")
    lo.list_display_dundle(list_in=list_of_WaterLevelTest_GB_times,
                           sequence_length=6)
    
    print("\nReport will be created at following times: <list_of_Reporting_times>")
    lo.list_display_dundle(list_in=list_of_Reporting_times,
                           sequence_length=6)

    ap_system_manager(list_of_WaterStream_times=list_of_WaterStream_times,
                      list_of_WaterLevelTest_GB_times=list_of_WaterLevelTest_GB_times,
                      list_of_Feeding_times=list_of_Feeding_times,
                      list_of_Reporting_times=list_of_Reporting_times,
                      list_of_Light_1_periods=list_of_Light_1_periods)

"""
so letcc C
"""