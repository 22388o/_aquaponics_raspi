"""
timechecking functions
"""

def system_time_to_string():
    return True

def stringtime_to_minutes(time_string:str):
    '''
    '''
    time_as_list = time_string.split(":")
    hour =      int (time_as_list[0])
    minutes =      int (time_as_list[1])
    # print(hour*60.0 + minutes)
    return hour*60.0 + minutes    
    

def check_if_time_in_period(time_str:str, start_str:str, finish_str:str):
    time_min = stringtime_to_minutes(time_str)
    start_min = stringtime_to_minutes(start_str)
    finish_min = stringtime_to_minutes(finish_str)
    # print("time: "+ str(time_min))
    # print("start: "+ str(start_min))
    # print("finish: "+ str(finish_min))
    if start_min <= time_min <= finish_min:
        return True
    elif (start_min > finish_min) and ( time_min > start_min or time_min < finish_min ):
        return True
    else:
        return False

        
if __name__ == "__main__":
    print(check_if_time_in_period(time_str = '06:16',
                            start_str = '23:00',
                            finish_str = '06:15'))
