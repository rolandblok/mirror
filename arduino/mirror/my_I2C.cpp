
void _my_i2cRequestEvent(int how_many);

// ============
// setup
void setup_i2c(){
  // enable i2c when the adress is set. If zero : master
  if (eeprom_getI2CAdress() > 0) {
    Wire.begin(eeprom_getI2CAdress());
    Wire.onReceive(_my_i2cReceiveEvent);
  } else {
    Wire.begin();
    Wire.onRequest(_my_i2cRequestEvent);
  }
  
}

// ============
// loop
void loop_i2c(void) {
  
}

void i2c_send_delta(uint8_t adress,  int x, int y) {
  
}
void i2c_send_cal_pos(uint8_t adress, int x, int y){
  
}
void i2c_send_zero(uint8_t adress) {
  Wire.beginTransmission(adress);
  Wire.write("z");
  Wire.endTransmission);
 
}
Point i2c_get_calibrated_pos(uint8_t adress) {
  Point calib_pos = {};
  Wire.beginTransmission(adress);
  Wire.write("l") ;
  Wire.endTransmission);
  Wire.requestFrom(adress, 2);
  While(Wire.Available()) {
    char c = Wire.read();
    
  }
}



// ==========
// I2C read callbacks
// ===========
void _my_i2cRequestEvent(int how_many) {
  while (1 < Wire.available()) { // loop through all but the last
    char c = Wire.read(); // receive byte as a character
    Serial.print(c);         // print the character
  }
  int x = Wire.read();    // receive byte as an integer
  Serial.println(x);         // print the integer
}

void _my_i2cRequestEvent(int howMany) {
    while (1 < Wire.available()) { // loop through all but the last
    char c = Wire.read(); // receive byte as a character
    Serial.print(c);         // print the character
  }
  int x = Wire.read();    // receive byte as an integer
  Serial.println(x);         // print the integer
}
