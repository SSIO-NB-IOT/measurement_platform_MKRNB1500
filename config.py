from dataclasses import dataclass
from typing import List

from influx_db import InfluxDBEndPoint
from sql.models import Base
from sql.sql_endpoint import SQLEndpoint


@dataclass
class ArduinoConfig:
    pin: str = ""
    token_mqtt: str = ""
    user_name: str = ""
    device_name: str = ""
    client_id: str = ""
    countMessageReceivedTopic: str = ""
    ackMessageReceivedTopic: str = ""
    broker: str = ""
    broker_port: int = 1883
    packetSize: int = 128
    packetPerSeconds: int = 10
    everyMillis: int = 1000
    baud_rate: int = 115200
    MonitoringCampagnDuration: int = 60000
    RAT: str = "7"
    PTW: str = "0000"
    EDRX: str = "0000"
    PSM_VERSION: int = 15


@dataclass
class InfluxDBConfig:
    bucket_list: List[str]
    organisation: str = ""
    INFLUXDB_TOKEN: str = ""
    port_number: int = 8086
    ip_address: str = "localhost"
    __target__ = "config.InfluxDBEndpointConverter"


@dataclass
class SQLEndpointConfig:
    MYSQL_USER: str = ""
    MYSQL_PASSWORD: str = ""
    MYSQL_DATABASE: str = ""
    SQL_PORT: int = 3306
    IP_ADDRESS: str = ""
    __target__ = "config.SQLEndpointConverter"




class SQLEndpointConverter():

    def __init__(self, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE, SQL_PORT,IP_ADDRESS):
        self.endpoint = SQLEndpoint(url=f"mysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{IP_ADDRESS}:{SQL_PORT}/{MYSQL_DATABASE}", base_class=Base)

    def __call__(self):
        return self.endpoint

class InfluxDBEndpointConverter():

    def __init__(self, bucket_list, organisation, INFLUXDB_TOKEN, port_number, ip_address):
        self.endpoint = InfluxDBEndPoint(url=f"http://{ip_address}:{port_number}",
                                         organisation=organisation,
                                         token=INFLUXDB_TOKEN,
                                         bucket_list=bucket_list)

    def __call__(self):
        return self.endpoint

class ArduinoConverter():

    @staticmethod
    def psm_version() -> dict:
        return { i : ArduinoConverter.psm_bits_signification(i)  for i in range(16) }
    @staticmethod
    def psm_bits_signification( value: float) -> str:
        # Convert to an array of 4 bits
        bits = list(bin(int(value))[2:].zfill(4))
        string = ""
        if bits[0] == 1:
            string += "PSM_W/_Netcordination "
        if bits[1] == 1:
            string += "PSM_W/_context_retention "
        if bits[2] == 1:
            string += "PSM_W_context_retention "
        if bits[3] == 1:
            string += "PSM_w_DRX"
        return string


    def __init__(self, **kwargs):
        # For now it's useless but
        # if you want to put 20.24 seconds for DRX here you will convert it into str
        # readable by the ublox LTE chip

        self.configurations = kwargs
        for key, value in kwargs.items():
            if isinstance(value, bool):
                self.configurations[key] = str(value).lower()
            else:
                self.configurations[key] = str(value)

    def __call__(self):
        return self.configurations