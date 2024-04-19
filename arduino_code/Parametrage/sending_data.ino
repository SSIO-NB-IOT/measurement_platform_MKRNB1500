// Copied and modified from https://github.com/256dpi/arduino-mqtt/blob/master/examples/ArduinoMKRNB1500/ArduinoMKRNB1500.ino
#include "sending_data.h"*



extern const char pin[];
extern const char token_mqtt[];
extern const char user_name[];
extern const char device_name[];
extern const char client_id[];
extern const char countMessageReceivedTopic[];
extern const char ackMessageReceivedTopic[];
extern const char broker[];
extern int broker_port;
extern int packetSize;
extern int packetPerSeconds;
extern int everyMillis;
extern unsigned int  baud_rate;
extern int MonitoringCampagnDuration;
static int currentMonitoringIndex = 0;
unsigned long lastMillis = 0;

NBClient net;
NB nbAccess;
MQTTClient client(packetSize);

void connectToCellular(){

  bool connected = false;

  Serial.print("connecting to cellular network ...");

  while (!connected) {
    if ((nbAccess.begin(pin) == NB_READY)) {
      connected = true;
      Serial.println("connected! to cellular network");
    } else {
      Serial.print(".");
      delay(1000);
    }
  }
  Serial.println("connected!");
}

void connectMQTTBroker(){
  Serial.print("\nconnecting to MQTT broker ...");
  Serial.println(broker);
  while (!client.connect(device_name, user_name, token_mqtt)) {
    Serial.print(".");
    delay(1000);
  }

  Serial.println("\nconnected!");

}

void connect() {
  connectToCellular();
  connectMQTTBroker();
}

void connect_mqtt() {
  Serial.begin(baud_rate);
  client.begin(broker, broker_port,net);
  //client.onMessage(messageReceived);
  connect();
  client.subscribe(ackMessageReceivedTopic);
}

bool sendingDataLoop() {
  Serial.print("Send data ");
  Serial.println(currentMonitoringIndex);
  if (currentMonitoringIndex >= MonitoringCampagnDuration){
    Serial.println("Monitoring campagn is over");
    return true;
  }
  client.loop();

  if (!client.connected()) {
    connect();
  }

  if (millis() - lastMillis > everyMillis) {
    lastMillis = millis();
    for (int i = 0; i < packetPerSeconds; i++){
        char packet[packetSize + 1];
        generateRandomString(packet,packetSize);
        client.publish(countMessageReceivedTopic, packet);
    }
  }  
  currentMonitoringIndex += 1;
  return false;
}


void messageReceived(String &topic, String &payload) {
  Serial.println("incoming: " + topic + " - " + payload);
  // TODO : compute the delay between the sending and the reception of the message
  // is this useless ? 
}

const char charset[] = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"; // Define the character set

void generateRandomString(char *output, int length) {
  for (int i = 0; i < length; ++i) {
    int randomIndex = random(0, sizeof(charset) - 1); // Generate a random index within the character set
    output[i] = charset[randomIndex]; // Assign the randomly selected character to the output array
  }
  output[length] = '\0'; // Null-terminate the string
}
