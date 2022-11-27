import os
import time
from sense_hat import SenseHat

def sense_hat_env_data(code):
    
    sense = SenseHat()
    sense_hat_measurements = {}
    if code in [1, 3, 5, 7]:
        temp = round(sense.get_temperature_from_pressure(), 1)
        cpu_temp = round(float(measure_cpu_temp()), 1)
        factor = 1.8
        sense_hat_measurements['temperature'] = round(temp - ((cpu_temp - temp)/factor), 1) 
        # print (sense_hat_measurements['actual_temperature'])
    if code in [2, 3, 6, 7]:
        sense_hat_measurements['humidity'] =     round(sense.get_humidity(), 1)
        # print (sense_hat_measurements['actual_humidity'])
    if code in [4, 5, 6, 7]:
        sense_hat_measurements['air_pressure'] = round(sense.get_pressure(), 1)
        # print (sense_hat_measurements['actual_air_pressure'])
    return sense_hat_measurements


def measure_cpu_temp():
    temp = os.popen("vcgencmd measure_temp").readline()
    return (temp.replace("temp=","").replace("'C", ""))


if __name__ == "__main__":
    while True:
        speed = 0.1
        sense = SenseHat()
        actual_data = sense_hat_env_data(7)
        print(actual_data)
        sense.show_message('rH:' + str(actual_data['humidity']) + "%",
                           scroll_speed=speed,
                           text_colour=[0, 0, 255])
        sense.show_message('T:' + str(actual_data['temperature']) + "'C",
                           scroll_speed=speed,
                           text_colour=[255, 0, 0])
        sense.show_message('p:' + str(actual_data['air_pressure']) + 'bar',
                           scroll_speed=speed,
                           text_colour=[255, 255, 0])
        time.sleep(0.5)
