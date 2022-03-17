#include <math.h>
#include <Wire.h>

#include "my_config.h"
#include "my_eeprom.h"
#include "my_servo.h"



void(*resetFunc) (void) = 0; 

void loop_serial() {
  // ===============
  // serial business
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil(10);
    if (command.equals("restart")) {
      Serial.end();  //clears the serial monitor  if used
      resetFunc();
      delay(1000);
    } else if (command.startsWith("ar")) {
      long angle_read = command.substring(2).toInt();
      if ((angle_read >= 0) || (angle_read <= 180)) {
        myservos_angles[0] = angle_read;
      }
      serial_print_raw_angles();
    } else if (command.startsWith("br")) {
      long angle_read = command.substring(2).toInt();
      if ((angle_read >= -90) || (angle_read <= 90)) {
        myservos_angles[1] = angle_read;
      }
      serial_print_raw_angles();
    } else if (command.startsWith("cr")) {
      int ar = command.substring(2).toInt();
      int br = command.substring(1+command.indexOf(',')).toInt();
      if (((ar >= 0) || (ar <= 180)) && ((br >= 0) || (br <= 180))) {
        myservos_angles[0] = ar;
        myservos_angles[1] = br;
      }
      serial_print_raw_angles();
    } else if (command.startsWith("a")) {
      long angle_read = command.substring(2).toInt();
      servo_set_calibrated_angle(0, angle_read);
      serial_print_calibrated_angles();
    } else if (command.startsWith("b")) {
      long angle_read = command.substring(2).toInt();
      servo_set_calibrated_angle(1, angle_read);
      serial_print_calibrated_angles();
    } else if (command.startsWith("c")) {
      int angles[NO_SERVOS] = {};
      angles[0] = command.substring(2).toInt();
      angles[1] = command.substring(1+command.indexOf(',')).toInt();
      servo_set_calibrated_angles(angles);
      serial_print_calibrated_angles();
    } else if (command.startsWith("A")) {
      long angle_read = command.substring(2).toInt();
      myservos_angles[0] += angle_read;
      serial_print_calibrated_angles();
    } else if (command.startsWith("B")) {
      long angle_read = command.substring(2).toInt();
      myservos_angles[1] += angle_read;
      serial_print_calibrated_angles();
    } else if (command.startsWith("C")) {
      myservos_angles[0] += command.substring(2).toInt();
      myservos_angles[1] += command.substring(1+command.indexOf(',')).toInt();
      serial_print_calibrated_angles();
    } else if (command.equals("1")) {
        myservos_angles[0] = 50;
        serial_print_calibrated_angles();
    } else if (command.equals("2")) {
        myservos_angles[0] = 90;
        serial_print_calibrated_angles();
    } else if (command.equals("3")) {
        myservos_angles[0] = 130;
        serial_print_calibrated_angles();
    } else if (command.equals("6")) {
        myservos_angles[1] = 50;
        serial_print_calibrated_angles();
    } else if (command.equals("5")) {
        myservos_angles[1] = 90;
        serial_print_calibrated_angles();
    } else if (command.equals("4")) {
        myservos_angles[1] = 130;
        serial_print_calibrated_angles();
    } else if (command.equals("s")) {
        servo_switch_sinus_loop();
    } else if (command.equals("o")) {
        myservos_angles[0] += 1;
        serial_print_calibrated_angles();
    } else if (command.equals("l")) {
        myservos_angles[0] -= 1;
        serial_print_calibrated_angles();
    } else if (command.equals("i")) {
        myservos_angles[1] += 1;
        serial_print_calibrated_angles();
    } else if (command.equals("p")) {
        myservos_angles[1] -= 1;
        serial_print_calibrated_angles();
    } else if (command.equals("O")) {
        myservos_angles[0] += 5;
        serial_print_calibrated_angles();
    } else if (command.equals("L")) {
        myservos_angles[0] -= 5;
        serial_print_calibrated_angles();
    } else if (command.equals("I")) {
        myservos_angles[1] += 5;
        serial_print_calibrated_angles();
    } else if (command.equals("P")) {
        myservos_angles[1] -= 5;
        serial_print_calibrated_angles();
    } else if (command.equals("lograw")) {
        serial_print_raw_angles();
    } else if (command.equals("logpos")) {
        serial_print_calibrated_angles();
    } else if (command.equals("logzero")) {
        serial_print_zero_offsets();
    } else if (command.equals("logeepr")) {
        eeprom_serial();
    } else if (command.equals("clreepr")) {
        eeprom_clear();
    } else if (command.equals("zero")) {
        servo_zero();
    } else { 
        Serial.println("commands: ");
        Serial.println(" Absolutes: ");
        Serial.println("  ar 100  : set the raw servo 1 to 100 degrees");
        Serial.println("  br 100  : set the raw servo 2 to 100 degrees");
        Serial.println("  cr -100, 100  : set the raw servo 2 to -100, 100 degrees");
        Serial.println("  a 10    : set the scalibrated ervo 1 to 10 degrees");
        Serial.println("  b 10    : set the calibrated servo 2 to 10 degrees");
        Serial.println("  c -10, 10   : set the calibrated servo A,B 2 to -10, 10 degrees");
        Serial.println(" Deltas: ");
        Serial.println("  A 10   : add the servo 1 with delta 10 degrees");
        Serial.println("  B -10  : add the servo 1 with delta -10 degrees");
        Serial.println("  C 10,-10  : add the servo A,B with delta 10,-10 degrees");
        Serial.println("  i - p  : left - right 1 step");
        Serial.println("  o - l  : up   - down 1 step");
        Serial.println("  I - P  : left - right 5 steps");
        Serial.println("  O - L  : up   - down 5 steps");
        Serial.println(" Logging");
        Serial.println("  lograw : raw log position");
        Serial.println("  logpos : log position (relative to zero angle)");
        Serial.println("  logzero: log zero offsets");
        Serial.println("  logeepr: log eeprom");
        Serial.println(" Calibration");
        Serial.println("  zero   : set the current position to zero position");
        Serial.println(" Other");
        Serial.println("  restart: restart micro controller");
        Serial.println("  clreepr: clear the eeprom");
        Serial.flush();
    }
  } 
}

// ================================
// I2C position getters and setters 
// ================================

void serial_print_calibrated_angles() {
  int calibrated_angles[NO_SERVOS] = {};
  servo_get_calibrated_angles(calibrated_angles);
  for (int s = 0; s < NO_SERVOS-1; s ++) {
    Serial.print(String(calibrated_angles[s]) + " , ");
  }
  Serial.println(String(calibrated_angles[NO_SERVOS-1]) );
}

void serial_print_raw_angles() {
  for (int s = 0; s < NO_SERVOS-1; s ++) {
    Serial.print(String(myservos_angles[s]) + " , ");
  }
  Serial.println(String(myservos_angles[NO_SERVOS-1]) );
}

void serial_print_zero_offsets() {
  for (int s = 0; s < NO_SERVOS-1; s ++) {
    Serial.print(String(myservos_angles_zero_offsets[s]) + " , ");
  }
  Serial.println(String(myservos_angles_zero_offsets[NO_SERVOS-1]) );
}


/** ===============================
 * Startup routine
 */
void setup() {
  Serial.begin(115200);
  Serial.println("Boot Started");

  if (eeprom_init()) {
    eeprom_serial();
  } else {
    Serial.println("Eeprom not valid, initialize");
    eeprom_clear();
    eeprom_serial();
  }

  setup_i2c();

  servo_setup();

}

/** ===============================
 * Loop Routine
 */
 void loop() {
  loop_serial();
  loop_i2c();

  servo_loop();

  delay(0);         
}
