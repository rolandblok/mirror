
#include "my_servo.h"
#include "my_eeprom.h"

Servo myservos[NO_SERVOS];
int   myservos_angles[NO_SERVOS];
int   myservos_angles_zero_offsets[NO_SERVOS];

bool sinus_motion = false;
void _sinus_loop() ;



// ============================
// setup
// ============================
void servo_setup(void) {

  // load the zero angles from eeprom
  eeprom_getZeroOffsets(myservos_angles_zero_offsets);
  

  for (int s = 0; s < NO_SERVOS; s ++) {
    myservos[s].attach(PIN_SERVO_1+s);  
    servo_set_calibrated_angle(s, 0, false);
  }
}

// ============================
// loop
// ============================
void servo_loop(void) {

  if (sinus_motion) {
    _sinus_loop();
  }

  for (int s = 0; s < NO_SERVOS; s++) {
    if (myservos_angles[s] > SERVO_MAX) {
      myservos_angles[s] = SERVO_MAX;
      Serial.println(" SERVO MAX LIMIT for servo " + String(s));
    } else if (myservos_angles[s] < SERVO_MIN) {
      myservos_angles[s] = SERVO_MIN;
      Serial.println(" SERVO MIN LIMIT for servo " + String(s));
    }
    myservos[s].write(myservos_angles[s]);              // tell servo to go to position in variable 'pos'
  }
}


// ============================
// position getters and setters
// ============================
void servo_get_calibrated_angles(int angles_ret[NO_SERVOS]) {
  for (int s = 0; s < NO_SERVOS; s ++) {
    angles_ret[s] = servo_get_calibrated_angle(s);
  }
}
int servo_get_calibrated_angle(int s) {
  int zerod_angle = myservos_angles[s] - myservos_angles_zero_offsets[s];
  return zerod_angle;
}
int servo_get_raw_angle(int s) {
  return myservos_angles[s];
}


void servo_set_calibrated_angles(int angles[NO_SERVOS], bool log_serial=true) {
  for (int s = 0; s < NO_SERVOS; s ++) {
    servo_set_calibrated_angle(s, angles[s], false);
  }
  if (log_serial) {
    servo_serial_print_calibrated_angles();
  }  
}
void servo_set_calibrated_angle(int s, int angle, bool log_serial=true) {
  if ((angle >= -90) || (angle <= 90)) {
    myservos_angles[s] = angle + myservos_angles_zero_offsets[s];
  }
  if (log_serial) {
    servo_serial_print_calibrated_angles();
  }
}
void servo_set_raw_angle(int s, int angle, bool log_serial=true) {
  myservos_angles[s] = angle;
  if (log_serial) {
    servo_serial_print_calibrated_angles();
  }
}
void servo_add_angles(int angles[NO_SERVOS], bool log_serial=true) {
  for (int s = 0; s < NO_SERVOS; s ++) {
    servo_add_angle(s, angles[s], false);
  }
  if (log_serial) {
    servo_serial_print_calibrated_angles();
  }
}
void servo_add_angle(int s, int angle, bool log_serial=true) {
  myservos_angles[s] += angle;
  if (log_serial) {
    servo_serial_print_calibrated_angles();
  }
}

// ============
// zero
// ============
void servo_zero(){
  for (int s = 0; s < NO_SERVOS; s ++) {
    myservos_angles_zero_offsets[s] = myservos_angles[s];
  }
  eeprom_setZeroOffsets(myservos_angles_zero_offsets);
  eeprom_serial();
}


// ============
// serial logging
// ============
void servo_serial_print_calibrated_angles() {
  int calibrated_angles[NO_SERVOS] = {};
  servo_get_calibrated_angles(calibrated_angles);
  for (int s = 0; s < NO_SERVOS-1; s ++) {
    Serial.print(String(calibrated_angles[s]) + " , ");
  }
  Serial.println(String(calibrated_angles[NO_SERVOS-1]) );
}

void servo_serial_print_raw_angles() {
  for (int s = 0; s < NO_SERVOS-1; s ++) {
    Serial.print(String(myservos_angles[s]) + " , ");
  }
  Serial.println(String(myservos_angles[NO_SERVOS-1]) );
}

void servo_serial_print_zero_offsets() {
  for (int s = 0; s < NO_SERVOS-1; s ++) {
    Serial.print(String(myservos_angles_zero_offsets[s]) + " , ");
  }
  Serial.println(String(myservos_angles_zero_offsets[NO_SERVOS-1]) );
}


// ============
// debug movement.
// ============
void servo_switch_sinus_loop(){
  sinus_motion = ! sinus_motion;
}

void _sinus_loop() {
  float phase = (float) millis() / 1000 ;

  float a0 = 90.0 + 40 * cos(phase);
  float a1 = 90.0 + 40 * sin(phase);

  myservos_angles[0] = (int) a0;
  myservos_angles[1] = (int) a1;
  
}
