# Arduino mkrNB1500 mearsurement platform for NB-IoT and LTE-M

This goal of this repository is to create a measurement infrastructure. Where we want to measure the performance of the NB-IoT and LTE-M networks.
More specifically, we want to measure the performance of the network in terms of throughput, and PDR Packet Delivery Ratio.

## Acknowledgement

This code is derived from a student project in 2nd year of master Degree [SSIO](https://igm.univ-gustave-eiffel.fr/formations/master-2-systemes-et-services-pour-linternet-des-objets-ssio) at University Gustave Eiffel, Near from Paris Champs-Sur-Marne.
Thanks to the members of this project :
- Abdessalam Benayyad, https://github.com/benayyad12
- Abir Hammache, https://github.com/HammacheAbir
- Clément Dutriez, https://github.com/CafeKrem

During the student project :
Abir Hammache [GitHub account](https://github.com/benayyad12) was the project leader, and she was responsible for the code of the arduino and the chip configuration.
Abdessalam Benayyad, [GitHub account](https://github.com/benayyad12), he was responsible for the deployment of the monitoring campagn.
Clément Dutriez was the product owner and teacher.

For now Clément Dutriez is the main contributor and maintainer of this project.

## Contents 

This project is composed of :
- The arduino repository
  - The code is written in C++ and is intended to be run on an Arduino MKRNB1500.
  - The code is responsible for sending fake to an MQTT broker and configure the chip.
  - The code is located in the folder [arduino_code](arduino_code)
- The deployment repository
  - In this repository we deploy, using docker and docker-compose, the monitoring campaign composed of:
    - mysql database
    - InfluxDB database
    - Grafana dashboard
    - NodeRED flow
    - An MQTT broker
  - The code is located in the folder [deployment](deployment)
- The scope repository
  - In this repository we have the code to analyse the data collected during the monitoring campaign using pyvisa libs.
  - The code is located in the folder [scope](scope)
- The sql repository
  - In this repository we define models and SQLEndpoint responsible for talking with the database.
  - We use the ORM framework SQLAlchemy. 
  - The code is located in the folder [sql](sql)
- The `config` repository
  - In this repository we define the configuration of the project.
  - We use the hydra library to instanciate the configuration.
  - The code is located in the folder [config](config)
- `arduino_file_generator.py` file
  - This file is responsible for generating arduino code using jinja2.
- `config.py` file
  - This file contains the configuration of the project.
  - We use hydra library to instanciate the configuration.
- `influx_db.py` file
  - This file contains the code to interact with the influxDB database.
- `orchrestator.py` file
  - This file is responsible for orchestrating the deployment of the monitoring campagn.

## How to install 

First make sur you have poetry installed on your machine.


```bash 
poetry install
```

## How to run 

```bash
poetry run python orchestrator.py
```