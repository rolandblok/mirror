
#include "my_mirrors.h"
#include "my_smooth_servo.h"

#define SERVO_ANGLE_MIN  (-40)
#define SERVO_ANGLE_MAX  ( 40)

MySmoothServo sm_servo = MySmoothServo();

// ======================
// HELPERS
// ======================
int   get_servo(int mirror, int angle) {
  return mirror * NO_ANGLES_PER_MIRROR + angle;
}

// set the servo position (in memory) if it is allowed, and move the servo.
// Return true if setpoint is allowed.
int actuate_servo(int s, int angle) {

  if ((angle >= SERVO_ANGLE_MIN) && (angle <= SERVO_ANGLE_MAX)) {
    sm_servo.set_target(s, angle);
    return true;
  } else {
    return false;
  }

}

// ============================
// setup
// ============================
void mirror_setup(void) {
  sm_servo.setup();
  
}


// ============================
// loop
// ============================
void mirror_loop(void) {
  sm_servo.loop();

}


// ============================
// position getters and setters
// ============================
void mirror_get_angles(int mirror, int angles_ret[NO_ANGLES_PER_MIRROR]) {
  for (int a = 0; a < NO_ANGLES_PER_MIRROR; a ++) {
    angles_ret[a] = mirror_get_angle(mirror, a);
  }
}
int mirror_get_angle(int mirror, int a) {
  return sm_servo.get_target(get_servo(mirror, a));
}


void mirror_set_angles(int mirror, int angles[NO_ANGLES_PER_MIRROR], bool log_serial = true) {
  for (int a = 0; a < NO_ANGLES_PER_MIRROR; a ++) {
    mirror_set_angle(mirror, a, angles[a], false);
  }
  if (log_serial) {
    mirror_serial_print_angles(mirror);
  }
}
void mirror_set_angle(int mirror, int a, int angle, bool log_serial = true) {
  int s = get_servo(mirror, a);
  sm_servo.set_target(s, angle);
  if (log_serial) {
    mirror_serial_print_angles(mirror);
  }
}

void mirror_add_angles(int mirror, int angles[NO_ANGLES_PER_MIRROR], bool log_serial = true) {
  for (int a = 0; a < NO_ANGLES_PER_MIRROR; a ++) {
    mirror_add_angle(mirror, a, angles[a], false);
  }
  if (log_serial) {
    mirror_serial_print_angles(mirror);

  }
}
void mirror_add_angle(int mirror, int a, int angle, bool log_serial = true) {
  int s = get_servo(mirror, a);
  sm_servo.add_target(s, angle);
  if (log_serial) {
    mirror_serial_print_angles(mirror);
  }
}


// ============
// serial logging
// ============
void mirror_serial_print_angles(int mirror) {
  int s = get_servo(mirror, 0);
  Serial.println(String(mirror) + "," + String(sm_servo.get_target(s)) + "," + String(sm_servo.get_target(s + 1)));
}
void mirror_serial_print_all_angles() {
  for (int m = 0; m < NO_MIRRORS; m ++) {
    int s = get_servo(m, 0);
    Serial.println(String(m) + "," + String(sm_servo.get_target(s)) + "," + String(sm_servo.get_target(s + 1)));
  }
}
