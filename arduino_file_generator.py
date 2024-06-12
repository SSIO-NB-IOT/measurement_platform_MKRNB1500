import subprocess
from pathlib import Path
from jinja2 import  Environment, FileSystemLoader

class ArduinoFileGenerator():

    def __init__(self, out_put_file_path : Path, template_file_path : Path,makefile_path: Path, context : dict ):
        self.out_put_file_path = out_put_file_path
        self.template_file_path = template_file_path
        self.makefiel_path = makefile_path
        self.context = context
        self.env = Environment(
        loader=FileSystemLoader(self.template_file_path.parent)
        )

    def generate(self)-> None:
        template = self.env.get_template(self.template_file_path.name)
        renderd_c_code = template.render(self.context)
        self.write_c_code(renderd_c_code)

    def write_c_code(self, renderd_c_code : str) -> None:
        with open(self.out_put_file_path, "w") as f:
            f.write(renderd_c_code)

    def compile_and_deploy(self):

        command = [ "make", "-f", str(self.makefiel_path)]
        try:
            # Run the make command
            subprocess.run(command,cwd="arduino_code", check=True)
            print("Makefile executed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"Error executing Makefile: {e}")
            raise e



if __name__ == "__main__":
    out_put_file_path = Path("arduino_code/Parametrage/parameter.ino")
    template_file_path = Path("arduino_code/template/c_template.jinja")
    context = {
    "pin": "",
    "token_mqtt": "YourToken",
    "user_name": "motleyslicer243",
    "device_name": "nb-iot_device",
    "client_id": "CafeKrem",
    "countMessageReceivedTopic": "/countMessageReceived",
    "ackMessageReceivedTopic": "/ackMessageReceived",
    "broker": "motleyslicer243.cloud.shiftr.io",
    "broker_port": 1883,
    "packetSize": 128,
    "packetPerSeconds": 10,
    "everyMillis": 1000,
    "baud_rate": 115200,
    "MonitoringCampagnDuration": 60000,
    "RAT": "7",
    "PTW": "0000",
    "EDRX": "0000",
    "NETWORK_COORDINATION": 15
    }

    arduino_file_generator = ArduinoFileGenerator(out_put_file_path, template_file_path, context)
    arduino_file_generator.generate()
