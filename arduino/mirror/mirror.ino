

#include "my_config.h"
#include "my_util.h"
#include "my_eeprom.h"
#include "my_servo.h"
#include "my_I2C.h"



void(*resetFunc) (void) = 0; 



void serial_loop() {
  // ===============
  // serial business
  if (Serial.available() > 0) {
    String ser_command = Serial.readStringUntil(10);
    int ser_data[3];
    if (ser_command.startsWith("R")) {   // Restart
        Serial.end();  //clears the serial monitor  if used
        resetFunc();
        delay(1000);
    } else if (ser_command.startsWith("r")) {
        ser_data[0] = string_read_int(ser_command);
        if ((ser_data[0] >= 0) || (ser_data[0] <= 180)) {
          servo_set_raw_angle(0, ser_data[0]);
        }
    } else if (ser_command.startsWith("t")) {
        ser_data[0] = string_read_int(ser_command);
        if ((ser_data[0] >= -90) || (ser_data[0] <= 90)) {
          servo_set_raw_angle(1, ser_data[0]);
        }
    } else if (ser_command.startsWith("a")) {
        ser_data[0]= string_read_int(ser_command);
        servo_set_calibrated_angle(0, ser_data[0]);
    } else if (ser_command.startsWith("b")){
        ser_data[0] = string_read_int(ser_command);
        servo_set_calibrated_angle(1, ser_data[0]);
    } else if (ser_command.startsWith("c")){
        string_read_int2(ser_command, ser_data);
        servo_set_calibrated_angles(ser_data);
    } else if (ser_command.startsWith("A")) {
        ser_data[0] = string_read_int(ser_command);
        servo_add_angle(0, ser_data[0]);
    } else if (ser_command.startsWith("B")) {
        ser_data[0] = string_read_int(ser_command);
        servo_add_angle(1, ser_data[0]);
    } else if (ser_command.startsWith("C")){
        string_read_int2(ser_command,ser_data);
        servo_add_angles(ser_data);
    } else if (ser_command.startsWith("1")) {
        servo_set_raw_angle(0, 50);
    } else if (ser_command.startsWith("2")) {
        servo_set_raw_angle(0, 90);
    } else if (ser_command.startsWith("3")) {
        servo_set_raw_angle(0, 130);
    } else if (ser_command.startsWith("6")) {
        servo_set_raw_angle(1, 50);
    } else if (ser_command.startsWith("5")) {
        servo_set_raw_angle(1, 90);
    } else if (ser_command.startsWith("4")) {
        servo_set_raw_angle(1, 130);
    } else if (ser_command.startsWith("s")) {
        servo_switch_sinus_loop();
    } else if (ser_command.startsWith("o")) {
        servo_add_angle(0, 1);
    } else if (ser_command.startsWith("l")) {
        servo_add_angle(0, -1);
    } else if (ser_command.startsWith("i")) {
        servo_add_angle(1, 1);
    } else if (ser_command.startsWith("p")) {
        servo_add_angle(1, -1);
    } else if (ser_command.startsWith("O")) {
        servo_add_angle(0, 5);
    } else if (ser_command.startsWith("L")) {
        servo_add_angle(0, -5);
    } else if (ser_command.startsWith("I")) {
        servo_add_angle(1, 5);
    } else if (ser_command.startsWith("P")) {
        servo_add_angle(1, -5);
    } else if (ser_command.startsWith("kr")) {
        servo_serial_print_raw_angles();
    } else if (ser_command.startsWith("kp")) {
        servo_serial_print_calibrated_angles();
    } else if (ser_command.startsWith("kz")) {
        servo_serial_print_zero_offsets();
    } else if (ser_command.startsWith("ke")) {
        eeprom_serial();
    } else if (ser_command.startsWith("E")) {
        eeprom_clear();
    } else if (ser_command.startsWith("z")) {
        servo_zero();
    } else if (ser_command.startsWith("Ws")) {
        ser_data[0] = string_read_int(ser_command);
        Serial.println("adress " + String(ser_data[0]));
        eeprom_setI2CAdress(ser_data[0]);
    } else if (ser_command.startsWith("Wz")) {
      if (eeprom_getI2CAdress() == 0) {
        ser_data[0] = string_read_int(ser_command);
        i2c_master_send_zero(ser_data[0]);
      }
    } else if (ser_command.startsWith("Wc")) {  // SET position data
      if (eeprom_getI2CAdress() == 0) {
        string_read_int3(ser_command, ser_data);
        i2c_master_send_cal_pos(ser_data[0], ser_data[1], ser_data[2]);
      }
    } else if (ser_command.startsWith("WC")) {  // SET position data
      if (eeprom_getI2CAdress() == 0) {
        string_read_int3(ser_command, ser_data);
        i2c_master_send_delta(ser_data[0], ser_data[1], ser_data[2]);
      }
    } else if (ser_command.startsWith("Wp")) {  // SET position data
      if (eeprom_getI2CAdress() == 0) {
        string_read_int1(ser_command, ser_data);
        Point p = i2c_master_get_calibrated_pos(ser_data[0]);
        Serial.println(String(p.x) + "," + String(p.y));
      }
    } else {         
      Serial.println("unknown command " + String(ser_command));

    
//        Serial.println("commands: ");
//        Serial.println(" Absolutes: ");
//        Serial.println("  r 100: set the raw servo 1 to 100 degrees");
//        Serial.println("  t 100: set the raw servo 2 to 100 degrees");
//        Serial.println("  a 10 : set the calibrated servo 1 to 10 degrees");
//        Serial.println("  b 10 : set the calibrated servo 2 to 10 degrees");
//        Serial.println("  c -10, 10: set the calibrated servo 1,2 to -10, 10 degrees");
//        Serial.println(" Deltas: ");
//        Serial.println("  A 10 : add the servo 1 with delta 10 degrees");
//        Serial.println("  B -10: add the servo 1 with delta -10 degrees");
//        Serial.println("  C 10,-10: add the servo 1,2 with delta 10,-10 degrees");
//        Serial.println("  i - p: left - right 1 step");
//        Serial.println("  o - l: up   - down 1 step");
//        Serial.println("  I - P: left - right 5 steps");
//        Serial.println("  O - L: up   - down 5 steps");
//        Serial.println(" Logging");
//        Serial.println("  kr   : raw log position");
//        Serial.println("  kp   : log position (relative to zero angle)");
//        Serial.println("  kz   : log zero offsets");
//        Serial.println("  ke   : log eeprom");
//        Serial.println(" Calibration");
//        Serial.println("  z    : set the current position to zero position");
//        Serial.println(" I2C communications");
//        Serial.println("  Ws    : set the i2c (wire) adress (0 = master) (will only activate after reboot)");
//        Serial.println("  Wc 1,10,10 : I2C SET for slave 1 the calibrated servos 1,2 to 10, 10 degrees");
//        Serial.println("  WC 1,10,10 : I2C ADD for slave 1 the calibrated servos 1,2 to 10, 10 degrees");
//        Serial.println("  Wp 1  : I2C get for slave 1 the calibrated servo positions");
//        Serial.println("  Wz 1  : I2C zero slave 1 ");
//        Serial.println(" Other");
//        Serial.println("  R    : restart micro controller");
//        Serial.println("  E    : clear the eeprom");
//        Serial.flush();
    }
  } 
}



/** ===============================
 * Startup routine
 */
void setup() {
  Serial.begin(115200);
  Serial.println("Boot Started");

  if (eeprom_init()) {
  } else {
    Serial.println("Eeprom not valid, initialize");
    eeprom_clear();
  }
  eeprom_serial();

  i2c_setup();

  servo_setup();

}

/** ===============================
 * Loop Routine
 */
 void loop() {
  serial_loop();
  
//  i2c_loop();

  servo_loop();

  delay(0);         
}