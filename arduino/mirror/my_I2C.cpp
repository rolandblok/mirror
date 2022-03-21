#include "my_I2C.h"
#include "my_eeprom.h"
#include "my_servo.h"

#include <Wire.h>

void _my_slave_i2cRequestEvent(int how_many);

// ============
// setup
void i2c_setup(){
  // enable i2c when the adress is set. If zero : master
  if (eeprom_getI2CAdress() != 0) {
    Serial.println(" I2C slave enabled " + String(eeprom_getI2CAdress()));
    Wire.begin(eeprom_getI2CAdress());
    Wire.onReceive(_my_slave_i2cRequestEvent); // slaves
  } else {
    Serial.println(" I2C master enabled " );
    Wire.begin(); // master no 
  }
}

// ============
// loop
void i2c_loop(void) {
  
}

// ==================
// Master send routines
void i2c_master_send_delta(uint8_t adress,  int x, int y) {
  String str = "C "+String(x)+","+String(y);
  
  Wire.beginTransmission(adress);
  Wire.write(str.c_str());
  Wire.endTransmission();
}

void i2c_master_send_cal_pos(uint8_t adress, int x, int y) {
  String str = "c "+String(x)+","+String(y);
  
  Wire.beginTransmission(adress);
  Wire.write(str.c_str());
  Wire.endTransmission();
}

void i2c_master_send_zero(uint8_t adress) {
  Wire.beginTransmission(adress);
  Wire.write("z");
  Wire.endTransmission();
}

Point i2c_master_get_calibrated_pos(uint8_t adress) {
  Wire.beginTransmission(adress);
  Wire.write("l") ;
  Wire.endTransmission();
  
  Wire.requestFrom(adress, (uint8_t) 4);
  String str = "";
  while (Wire.available()) {
    str += Wire.read();
//    byte highbyte = Wire.read();
//    byte lowbyte = Wire.read();
//    calib_pos.x = (highbyte << 8) + lowbyte;
//    highbyte = Wire.read();
//    lowbyte = Wire.read();
//    calib_pos.y = (highbyte << 8) + lowbyte;
  }
  Point calib_pos = {};
  calib_pos.x = str.toInt();
  calib_pos.y = str.substring(1+str.indexOf(',')).toInt();
  return calib_pos;
}



// ==========
// I2C read callbacks for slave side
// ===========
void _my_slave_i2cRequestEvent(int how_many) {
  Serial.println(" how_many :" + String(how_many));         // print the character

  // get the command string
  String command = "";
  while (Wire.available()) { // loop through all but the last
    command = Wire.read(); // receive byte as a character
    Serial.print(String(command));         // print the character
  }
  Serial.println(" end of command");

  // interprete the command and if needed read or send the data
  int angles[NO_SERVOS];
  if (command.startsWith("l")) {   // master requests current calibrated position
    servo_get_calibrated_angles(angles);
    String data_str = ""+String(angles[0])+","+String(angles[1]);
    
    Wire.beginTransmission(0);
    Wire.write(data_str.c_str());
//    int angle = servo_get_calibrated_angle(0);
//    Wire.write(highByte(angle));
//    Wire.write(lowByte(angle));
//    angle = servo_get_calibrated_angle(1);
//    Wire.write(highByte(angle));
//    Wire.write(lowByte(angle));
    Wire.endTransmission();
  } else if (command.startsWith("c")) {   // master sets calibrated position
    string_read_int2(command, angles);
    servo_set_calibrated_angles(angles);

  } else if (command.startsWith("C")) {   // master sets delta position
    string_read_int2(command, angles);
    servo_add_angles(angles);

  } else if (command.startsWith("z")) {   // master requests current calibrated position
    servo_zero();
  } else {
    Serial.println("command not understood " + String (command));
  }


}
