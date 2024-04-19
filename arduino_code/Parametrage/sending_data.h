#include <MKRNB.h>
#include <MQTT.h>

/*
This file is responsible for sending data to the MQTT broker. 
At compilaton time, the user can set the following parameters:
- pin: the pin of the SIM card
- apn: the APN of the cellular network
- login: the login of the cellular network
- password: the password of the cellular network
- countMessageReceivedTopic: the topic where the number of messages received will be published
- ackMessageReceivedTopic: the topic where the acknoledgement of the message received will be published
- broker: the address of the MQTT broker
- packetSize: the size of the packet to send
- packetPerSeconds: the number of packets to send per second
- everyMillis: the time between two packets
- baud_rate: the baud rate of the serial communication
- MonitoringCampagnDuration: the duration of the monitoring campaign

The private variables are:
- net: the NBClient object
- nbAccess: the NB object
- client: the MQTTClient object
- currentMonitoringIndex: the index of the current monitoring
*/

void messageReceived(String &topic, String &payload);

// connect arduino to cellular network. 
void connectToCellular();

// connect arduino to mqtt broker
void connect_mqtt();

// start the sending data procedure
bool sendingDataLoop();