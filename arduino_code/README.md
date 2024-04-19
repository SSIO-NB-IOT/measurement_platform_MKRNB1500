# Arduino MKRNB1500 Configuration

This folder contains the Arduino code for the project. The code is written in C++ and is intended to be run on an Arduino MKRNB1500. 
The code is responsible for sending fake to an MQTT broker. 


## Acknowledgement

This code is derived from a student project in 2nd year of master Degree [SSIO](https://igm.univ-gustave-eiffel.fr/formations/master-2-systemes-et-services-pour-linternet-des-objets-ssio) at University Gustave Eiffel, Near from Paris Champs-Sur-Marne.
The base code is the following written by Abir Hammache https://github.com/HammacheAbir :
- https://github.com/SSIO-NB-IOT/NB-MKR-Configuration-Measurement


## How to run 

```bash
make install # Install the dependencies
make deploy # Compile and deploy the code to the arduino
make # <=> make deploy
```

## Chip Configuration  

You can change configuration in Parameter.ino file.

For chip configuration it's a bit complicated you have to read the following manuals:
- AT command manual for RAT,PTW,EDRX, PSM_VERSION
https://content.u-blox.com/sites/default/files/documents/LEXI-R4-SARA-R4_ATCommands_UBX-17003787.pdf
- DRX configuration manual 
https://www.etsi.org/deliver/etsi_ts/124000_124099/124008/13.07.00_60/ts_124008v130700p.pdf

To help you to configure the chip there are some explanation :

### RAT

The Radio Access Technology (RAT) is the technology used to connect to the network. 

The AT commands is `AT+URAT=<1stAcT>[,<2ndAcT>[,<3rdAcT>]]`, in the code it's used like this :
```ino
MODEM.sendf("AT+URAT=%s", RAT); 
```

The possible RAT values are:
- 0 : GSM/GPRS/eGPRS
- 2 : UMTS
- 3 : LTE
- 7 : LTE Cat M1 "LTE-M"
- 8 : NB-IoT
- 9 : GPRS eGPRS

### DRX 

The Discontinuous Reception (DRX) is a feature that allows the device to sleep for a certain amount of time and wake up to check if there is any data to receive.
Be carefull some values corresponds to same drx cycle length in seconds
https://www.etsi.org/deliver/etsi_ts/124000_124099/124008/13.07.00_60/ts_124008v130700p.pdf



The AT command is `AT+CEDRXS=<mode>,<AcT>,<Requested_eDRX_value>,<Requested_PTW_value>`, in the code it's used like this :
```ino
MODEM.sendf("AT+CEDRXS=1,5,%s,%s",eDRX_AT_command, PTW_AT_command ); // Activate DRX
MODEM.sendf("AT+CEDRXS=1,5,%s,%s",eDRX_AT_command,PTW_AT_command); // Deactiviate DRX
```

The isDRXactivated parameters will activate or deactivate the DRX feature.

The possible values for eDRX_AT_command are:
- "0000" : 20.48 seconds in NB-IoT
- "0001" : 20.48 seconds in NB-IoT
- ... : read below for more values
I already write it in the code, it's dead code but it's usefull `Parametrage.ino` file.: 
```ino
EDRXLength eDRXLengths[16] = { // Check 3GPP standart for more information in seconds
  {0, "0000"}, // 20.48 seconds in NB-IoT
  {1, "0001"}, // 20.48 seconds in NB-IoT
  {2, "0010"}, // 20.48 in NB-IoT
  {3, "0011"}, // 40.96 in NB-IoT
  {4, "0100"}, // 20.48 in NB-IoT
  {5, "0101"}, // 81.92
  {6, "0110"}, // 20.48 in NB-IoT
  {7, "0111"}, // 20.48 in NB-IoT
  {8, "1000"}, // 20.48 in NB-IoT
  {9, "1001"}, // 163.84
  {10, "1010"}, //327.68
  {11, "1011"}, // 655.36
  {12, "1100"}, //1310.72
  {13, "1101"}, // 2621.44
  {14, "1110"}, // 5242.88
  {15, "1111"} // 10485.76
};
```

### PSM_VERSION

the PSM_VERSION is the version of the Power Saving Mode (PSM) that the device will use.

The AT command is `AT+CPSMS=<psm_version>[otherArgument]`, in the code it's used like this :
```ino
MODEM.sendf("AT+UPSMVER=%i",PSM_VERSION);
```

The possible values for PSM_VERSION are:
- from 0 to 15 : the version of the PSM
  - bit 0: PSM without network coordination
  - bit 1: PSM according to release 12 without context retention
  - bit 2: PSM according to release 12 with context retention
  - bit 3: deep-sleep mode in between eDRX cycles


## Application Configuration

You can change configuration in Parameter.ino file.
- packetSize : the size of the packet that will be sent to the broker
- packetPerSeconds : the number of packet that will be sent to the broker per second
- everyMillis : the time between each packet sent to the broker /!\ don't modified it.
- MonitoringCampagnDuration : the duration of the monitoring campagn in seconds



## Dependencies

The code depends on the following arduino libraries:
- MKRNB
- MQTT


## MQTT Channels

There is two MQTT channels :
- `const char countMessageReceivedTopic[] = "countMessageReceived";`, the channel where the arduino will send fake data.
- `const char ackMessageReceivedTopic[] = "AckCountMessageReceived";`, the channel where the arduino will receive the acknoledgement of the data sent.
  - For now it's not used anymore, but it can be used to check if the data was received by the broker.

## Debugging 

The code is configured to print debug messages to the serial port.

## Code generation

If you're use the Orchestrator class there is a `c_template.jinja` file that will generate configuration code in the file `Parameter.ino`.
We use jinja2 to write template file.
