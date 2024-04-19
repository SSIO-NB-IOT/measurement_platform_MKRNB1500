#include "sending_data.h"

/*
ubloc AT documentation 
https://content.u-blox.com/sites/default/files/documents/LEXI-R4-SARA-R4_ATCommands_UBX-17003787.pdf

DRX configuration manual 
https://www.etsi.org/deliver/etsi_ts/124000_124099/124008/13.07.00_60/ts_124008v130700p.pdf
*/
struct PagingTimeWindowLength {
  int PTW; // Paging Time Window
  String PTW_AT_command;
}; 
struct eDRXCycleLenth {
  int eDRX; // eDRX cycle length
  String eDRX_AT_command; 
};


typedef struct eDRXCycleLenth EDRXLength; 
typedef struct PagingTimeWindowLength PTWLength;
extern const char truc[];
// Create an array of eDRXLength
EDRXLength eDRXLengths[16] = { // Check 3GPP standart for more information in seconds
  {0, "0000"}, // 20.48 in NB-IoT
  {1, "0001"}, // 20.48 in NB-IoT
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
// Create an array of PTWLength
PTWLength PTWLengths[16] = { // Check 3GPP standart for more information
  {0, "0000"}, // 1.28 seconds
  {1, "0001"}, // 2.56
  {2, "0010"}, // 3.84
  {3, "0011"}, 
  {4, "0100"},
  {5, "0101"},
  {6, "0110"},
  {7, "0111"},
  {8, "1000"},
  {9, "1001"},
  {10, "1010"},
  {11, "1011"},
  {12, "1100"},
  {13, "1101"},
  {14, "1110"},
  {15, "1111"}
};

int eDRXChoices[4] = {
  0, // 20.48 seconds
  3, // 40.96 seconds
  5, // 81.92 seconds
  9 // 163.84 seconds
  };

extern const char RAT[];
extern const char PTW[];
extern const char EDRX[];
extern int PSM_VERSION;
extern bool isDRXactivated;

bool is_finish = false;

void setup() {
  
  Serial.begin(115200);
  while (!Serial);

  MODEM.begin();
  while (!MODEM.noop());
  configure_arduino_device(RAT, EDRX, PSM_VERSION,PTW,isDRXactivated);
  apply_AT_commands();
  connectToCellular();
  connect_mqtt();
  sendingDataLoop();
}



bool configure_arduino_device(const  char  RAT[], const char  eDRX_AT_command[],int PSM_VERSION,const char  PTW_AT_command[],bool isDRXactivated ) {
  String response;
  //String PTW_AT_command = PTWLengths[0].PTW_AT_command;
  //String eDRX_AT_command = eDRXLengths[eDRXChoices[edrx]].eDRX_AT_command;
  Serial.print("Disconnecting from network: ");
  MODEM.sendf("AT+COPS=2");
  MODEM.waitForResponse(2000);
  Serial.println("done.");

  Serial.print("Setting Radio Access Technology: ");
  MODEM.sendf("AT+URAT=%s", RAT); 
  // 7 : LTE-M and 8 : NB-IoTs
  MODEM.waitForResponse(2000, &response);
  Serial.println("done.");

  Serial.print("Setting eDRX configuration: ");
  if (isDRXactivated){
    MODEM.sendf("AT+CEDRXS=1,5,%s,%s",eDRX_AT_command,PTW_AT_command, ); //
  } else {
    MODEM.sendf("AT+CEDRXS=1,5,%s,%s",eDRX_AT_command,PTW_AT_command);
    // DRX not activate
  //MODEM.sendf("AT+CEDRXS=1,5,%s,%s",PTW_AT_command, eDRX_AT_command); // 
  // 1 : Enable eDRX, 5 : NB-IoT, PTW_AT_command : paging time window length, eDRX_AT_command : eDRX cycle length
  }
  
  MODEM.sendf("AT+UPSMVER=%i",PSM_VERSION); // Power Sleep Mode Version
  // 4 => PSM release 12 with context retention

  //MODEM.sendf("AT+CFUN=15"); // Reboot modem
  MODEM.waitForResponse(2000, &response);
  Serial.println("done.");

  return true;
}


void display_information(const char * at_command_description, const char * AT_commands){
  Serial.print(at_command_description);
  String imei;
  imei.reserve(256);
  MODEM.send(AT_commands);
  while (imei.equals(String("")))
  {
    MODEM.waitForResponse(1000,&imei);
  }
  
  Serial.println(imei);
}

bool apply_AT_commands() {
  Serial.print("Applying changes and saving configuration: ");
  MODEM.send("AT+CFUN=15");
  MODEM.waitForResponse(5000);
  delay(5000);

  do {
    delay(1000);
    MODEM.noop();
  } while (MODEM.waitForResponse(1000) != 1);

  Serial.println("done.");
  
  return true;
}

void loop() {
  while((is_finish = sendingDataLoop()) == false){
    ;
  }
  while (is_finish)
  {
    delay(10000);
  }
  
}