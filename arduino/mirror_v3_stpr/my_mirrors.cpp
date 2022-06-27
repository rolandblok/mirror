
#include "my_mirrors.h"
#include "my_steppers.h"


MySteppers my_steppers = MySteppers();

// ======================
// HELPERS
// ======================
float   get_stepper(int mirror, int angle) {
  return mirror * NO_ANGLES_PER_MIRROR + angle;
}


void mirror_setup(void){
  my_steppers.start_homing();
}

// ============================
// loop
// ============================
void mirror_loop(void) {
  my_steppers.loop();

}


// ============================
// position getters and setters
// ============================
void mirror_get_angles(int mirror, float angles_ret[NO_ANGLES_PER_MIRROR]) {
  for (int a = 0; a < NO_ANGLES_PER_MIRROR; a ++) {
    angles_ret[a] = mirror_get_angle(mirror, a);
  }
}
float mirror_get_angle(int mirror, int a) {
  return my_steppers.get_target(get_stepper(mirror, a));
}

void mirrors_set_8angles(int mirror_start, float *angles, bool log_serial){
  long start_time = millis();
  for (int m = 0; m < 4; m++) {
    for (int a = 0; a < NO_ANGLES_PER_MIRROR; a ++) {
      mirror_set_angle(m+mirror_start, a, angles[m*NO_ANGLES_PER_MIRROR + a], false);
    }
  }
  if (log_serial) {
    Serial.println("D " + String(millis() - start_time));
  }
}

void mirror_set_angles(int mirror, float angles[NO_ANGLES_PER_MIRROR], bool log_serial = true) {
  for (int a = 0; a < NO_ANGLES_PER_MIRROR; a ++) {
    mirror_set_angle(mirror, a, angles[a], false);
  }
  if (log_serial) {
    mirror_serial_print_angles(mirror);
  }
}
void mirror_set_angle(int mirror, int a, float angle, bool log_serial = true) {
  int s = get_stepper(mirror, a);
  my_steppers.set_target(s, angle);
  if (log_serial) {
    mirror_serial_print_angles(mirror);
  }
}

void mirror_add_angles(int mirror, float angles[NO_ANGLES_PER_MIRROR], bool log_serial = true) {
  for (int a = 0; a < NO_ANGLES_PER_MIRROR; a ++) {
    mirror_add_angle(mirror, a, angles[a], false);
  }
  if (log_serial) {
    mirror_serial_print_angles(mirror);

  }
}
void mirror_add_angle(int mirror, int a, float angle, bool log_serial = true) {
  int s = get_stepper(mirror, a);
  my_steppers.add_target(s, angle);
  if (log_serial) {
    mirror_serial_print_angles(mirror);
  }
}


// ============
// serial logging
// ============
void mirror_serial_print_angles(int mirror) {
  int s = get_stepper(mirror, 0);
  Serial.println(String(mirror) + "," + String(my_steppers.get_target(s)) + "," + String(my_steppers.get_target(s + 1)));
}
void mirror_serial_print_all_angles() {
  for (int m = 0; m < NO_MIRRORS; m ++) {
    int s = get_stepper(m, 0);
    Serial.println(String(m) + "," + String(my_steppers.get_target(s)) + "," + String(my_steppers.get_target(s + 1)));
  }
}
