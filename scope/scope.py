#/usr/bin/python3
import time

import numpy as np
# https://download.tek.com/manual/070987600.pdf
import paho.mqtt.client as mqtt
import os
import random
import pyvisa as visa


def collect_data(duration):
    rm = visa.ResourceManager()
    addresses = rm.list_resources()
    addresse =addresses[0]
    print(addresse)
    #addresse ="ASLR/dev/bus/usb/003/023"
    osc = rm.open_resource(addresse)
    osc.read_termination = '\n'
    osc.write_termination = '\n'
    osc.baud_rate = 115200
    #osc.baud_rate = 9600

    print(osc.query('*IDN?'))  # Query the instrument identification string
    print(osc.query('*RST'))  # Query the operation complete status
    #print(osc.query('*OPC?'))  # Query the operation complete status
    print(osc.query('*opt?'))  # Query the average voltage
    # Configure the oscilloscope
    #osc.write('SELECT:CH1 ON')  # Select channel 1
    #osc.write('MEASUrement:IMMed:TYPE VOLTage')  # Set measurement to voltage
    #osc.write('TIMEBASE:SCALE 0.01')  # Set time base scale
    #osc.write('TRIGger:MODE EDGE;:TRIGger:EDGE:SOURce CH1')  # Configure trigger
    print(osc.query("status:measurement?"))
    # Assuming data collection starts automatically upon configuration
    print("Starting data collection...")
    time.sleep(duration)  # Wait for specified duration

    # Example: Retrieve the average voltage measurement
    # This command is hypothetical and depends on your oscilloscope's SCPI implementation
    data = osc.query('MEAS:VOLT? CH1', delay=3)  # Query the average voltage

    print(f"Data collection completed. Measurement: {data}")
    osc.close()
    return data


def start_collecting_scope():
    # Get env variables for mqtt
    mqtt_broket = str(os.getenv('MQTT_BROKER',"motleyslicer243.cloud.shiftr.io"))
    port_number = int(os.getenv('MQTT_PORT',1883))
    topic = str(os.getenv('MQTT_TOPIC',"energy_consumption"))
    token = str(os.getenv('MQTT_TOKEN',None))
    if token is None:
        raise Exception("You have to set an MQTT token of your MQTT broker")
    resistance = float(os.getenv('RESISTANCE',100))
    username = str(os.getenv('MQTT_USERNAME',None))
    if token is None:
        raise Exception("You have to set an MQTT username of your MQTT broker")
    # generate a random client id 
    client_id = f'python-mqtt-{random.randint(0, 1000)}:{token}'
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,client_id=client_id)
    client.username_pw_set(username, token)
    initialise_mqtt_client(client, mqtt_broket, 1883)
    rm = visa.ResourceManager("@py")
    addresses = rm.list_resources()
    visa_address = addresses[0]

    rm = visa.ResourceManager()
    scope = rm.open_resource(visa_address)
    scope.timeout = 10000  # ms
    scope.encoding = 'latin_1'
    scope.read_termination = '\n'
    scope.write_termination = None
    scope.write('*cls')  # clear ESR

    #print(scope.query('*idn?'))

    initialise(scope)

    scope.write('autoset EXECUTE')  # autoset
    t3 = time.perf_counter()
    r = scope.query('*opc?')  # sync
    t4 = time.perf_counter()
    print('autoset time: {} s'.format(t4 - t3))

    tscale = float(scope.query('wfmpre:xincr?'))
    tstart = float(scope.query('wfmpre:xzero?'))
    vscale = float(scope.query('wfmpre:ymult?'))  # volts / level
    voff = float(scope.query('wfmpre:yzero?'))  # reference voltage
    vpos = float(scope.query('wfmpre:yoff?'))
    i = 0
    # io config
    while(True):
        i += 1
        bin_wave, record = get_data(scope)
        scale_values_array, scale_time_array,total_time = transform_data(bin_wave, record, tscale=tscale, tstart =tstart, vpos =vpos,
                   vscale =vscale, voff =voff)
        mean_volt = scale_values_array.mean()
        intensity = mean_volt / resistance
        energy_consumed = mean_volt*intensity * total_time
        send_data_through_mqtt(client, energy_consumed,topic)

    # error checking
    scope.close()
    rm.close()


def get_data(scope):
    scope.write('header 0')
    scope.write('data:encdg RIBINARY')
    scope.write('data:source CH1')  # channel
    scope.write('data:start 1')  # first sample
    time_array = int(scope.query('wfmpre:nr_pt?'))
    scope.write('data:stop {}'.format(time_array))  # last sample
    scope.write('wfmpre:byt_nr 1')  # 1 byte per sample
    # acq config
    scope.write('acquire:state 0')  # stop # Met la capture en mode stop
    scope.write('acquire:stopafter SEQUENCE')  # single
    scope.write('acquire:state 1')  # run
    t5 = time.perf_counter()
    r = scope.query('*opc?')  # sync
    t6 = time.perf_counter()
    #print('acquire time: {} s'.format(t6 - t5))
    # data query
    t7 = time.perf_counter()
    values_array = scope.query_binary_values('curve?', datatype='b', container=np.array)
    t8 = time.perf_counter()
    #print('transfer time: {} s'.format(t8 - t7))
    return values_array, time_array


def initialise(scope):
    scope.write('*rst')  # reset
    t1 = time.perf_counter()
    r = scope.query('*opc?')  # sync
    t2 = time.perf_counter()
    #print('reset time: {} s'.format(t2 - t1))


def transform_data(values_array:np.ndarray, time_array: np.ndarray, tscale: float=None, tstart : float=None, vpos : float=None,
                   vscale : float =None, voff : float =None)->  np.ndarray:
    total_time = tscale * time_array
    tstop = tstart + total_time
    scale_time_array = np.linspace(tstart, tstop, num=time_array, endpoint=False)
    # vertical (voltage)
    unscaled_wave = np.array(values_array, dtype='double')  # data type conversion
    scale_values_array = (unscaled_wave - vpos) * vscale + voff
    return  scale_values_array, scale_time_array,total_time

def initialise_mqtt_client(client : mqtt.Client, broker_address:str, port:int):
    client.on_connect = None # We can define call when connect
    client.on_disconnect = None # We can define call when disconnect
    client.on_message = None # We can define call when message is received
    client.loop_start( )
    client.connect(broker_address, port)

def send_data_through_mqtt(client : mqtt.Client,data:np.ndarray, topic:str):
    client.publish(topic, data)

if __name__ == "__main__":
    start_collecting_scope()
