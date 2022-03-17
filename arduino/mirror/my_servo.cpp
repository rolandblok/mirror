
#include "my_servo.h"
#include "my_eeprom.h"

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
    servo_set_calibrated_angle(s, 0);
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
void get_calibrated_angles(int angles_ret[NO_SERVOS]) {
  for (int s = 0; s < NO_SERVOS; s ++) {
    angles_ret[s] = servo_get_calibrated_angle(s);
  }
}
int get_calibrated_angle(int s) {
  int zerod_angle = myservos_angles[s] - myservos_angles_zero_offsets[s];
  return zerod_angle;
}

void set_calibrated_angles(int angles[NO_SERVOS]) {
  for (int s = 0; s < NO_SERVOS; s ++) {
    servo_set_calibrated_angle(s, angles[s]);
  }
}
void set_calibrated_angle(int s, int angle) {
  if ((angle >= -90) || (angle <= 90)) {
    myservos_angles[s] = angle + myservos_angles_zero_offsets[s];
  }
}

// ============
// zero
// ============
void zero(){
  for (int s = 0; s < NO_SERVOS; s ++) {
    myservos_angles_zero_offsets[s] = myservos_angles[s];
  }
  eeprom_setZeroOffsets(myservos_angles_zero_offsets);
  eeprom_serial();
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
