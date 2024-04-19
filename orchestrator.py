import os
import subprocess
import time
import uuid
from pathlib import Path

import hydra
from hydra.core.config_store import ConfigStore
from omegaconf import DictConfig

from arduino_file_generator import ArduinoFileGenerator
from config import ArduinoConfig, InfluxDBConfig, SQLEndpointConfig, ArduinoConverter
from sql.models import Mission, Campaign


class Orchestrator():

    def __init__(self,arduino, influxDBEndpoint, SQLEndpoint):
        self.arduino_config = arduino()

        self.influxDBEndpoint = influxDBEndpoint()
        self.SQLEndpoint = SQLEndpoint()
        self.mission_parameters = { "packet_size": self.arduino_config["packetSize"],
                                    "packet_send_frequency": self.arduino_config["packetPerSeconds"],
                                    "energy_consume": None,
                                    "packet_delivery_ratio": None,
                                    "mission_time": self.arduino_config["MonitoringCampagnDuration"],
                                    "e_drx_value": self.arduino_config["EDRX"],
                                    "network_coordination_mode": ArduinoConverter.psm_bits_signification(self.arduino_config["PSM_VERSION"]),
                                    "radio_access_technologies_mode": self.arduino_config["RAT"],
                                    "throughput": None}
        self.measurement_campagn_duration = self.arduino_config["MonitoringCampagnDuration"]
        out_put_file_path = Path("arduino_code/Parametrage/parameter.ino")
        template_file_path = Path("arduino_code/template/c_template.jinja")
        self.arduino_file_generator = ArduinoFileGenerator(out_put_file_path=out_put_file_path,
                                                           template_file_path=template_file_path,
                                                           makefile_path=Path("./Makefile"),
                                                              context=self.arduino_config)
        self.campaign = Campaign(name="First campaign", description= "Test campaign")
        self.csv_path = Path(f"measurements_{uuid.uuid4()}.csv")

    def compile_and_deploy_arduino_code(self):
        self.arduino_file_generator.generate()
        self.arduino_file_generator.compile_and_deploy()

    def start_scope(self):
        # Path to your Python script
        python_script_path = Path('scope/scope.py')

        # Command to execute the Python script
        command = ["python", python_script_path ,">"  , "/dev/null"  ]

        # Environment variables
        environment = os.environ.copy()
        environment["MQTT_BROKER"] = self.arduino_config["broker"]
        environment["MQTT_PORT"] = str(self.arduino_config["broker_port"])
        environment["MQTT_TOPIC"] = "energy_consumption"
        environment["MQTT_TOKEN"] = self.arduino_config["token_mqtt"]
        environment["MQTT_USERNAME"] = self.arduino_config["user_name"]

        try:
            # Run the Python script with environment variables
            self.scope_process = subprocess.Popen(command, env=environment)
            print("Python script executed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"Error executing Python script: {e}")

    def fill_mission_parameters(self):
        dataFrame = self.influxDBEndpoint.request_mission_values() # Values already sum
        max_packet_sended = self.arduino_config.packetPerSeconds * self.measurement_campagn_duration
        self.mission_parameters["energy_consume"] = dataFrame["energy_consumption"] / self.measurement_campagn_duration
        self.mission_parameters["packet_delivery_ratio"] = dataFrame["packetReceived"] / (max_packet_sended)
        self.mission_parameters["throughput"] = (dataFrame["packetReceived"] * self.arduino_config.packetSize) / self.measurement_campagn_duration

    def measurement_campaign_finish(self):
        assert len(l := [ (k,v) for k,v in self.mission_parameters.items() if v is None]), f"Missing values for {l}"
        self.scope_process.terminate()
        mission = Mission(**self.mission_parameters)
        self.SQLEndpoint.add_mission(mission, self.campaign)
        self.SQLEndpoint.to_csv(self.csv_path)


    def init_influx_db(self):
        self.influxDBEndpoint.clean_influxDB()

    def init_sql_db(self):
        self.SQLEndpoint.init_data_base()


    def start_measurement_campaign(self):
        self.compile_and_deploy_arduino_code()
        print("Ardiuno code deployed")
        try:
            self.init_influx_db()
        except :
            print("Error while cleaning the influxDB")
        print("InfluxDB cleaned")
        self.init_sql_db()
        print("SQL Database initialized")
        input("Press Enter to start the measurement campaign")
        self.start_scope()
        print("Scope started")
        print("go to sleep")
        time.sleep(int(self.measurement_campagn_duration))
        print("wake up, measurement campaign finished")
        self.measurement_campaign_finish()

cs = ConfigStore.instance()
cs.store( name="arduino", node=ArduinoConfig)
cs.store( name="influxDBEndpoint", node=InfluxDBConfig)
cs.store( name="SQLEndpoint", node=SQLEndpointConfig)

@hydra.main(config_path="config", config_name="nb-iot_config.yaml",version_base="1.3")
def start_measurement_campaign(cfg: DictConfig):
    cfg_instanciated = hydra.utils.instantiate(cfg)
    orchestrator = Orchestrator(**cfg_instanciated)
    orchestrator.start_measurement_campaign()


if __name__ == "__main__":
    start_measurement_campaign()
