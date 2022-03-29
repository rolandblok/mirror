
#include "my_mirrors.h"

//https://rootsaid.com/pca9685-servo-driver/
#define SERVOMIN  (150) // This is the 'minimum' pulse length count (out of 4096)
#define SERVOMAX  (600) // This is the 'maximum' pulse length count (out of 4096)
#define USMIN  (600) // This is the rounded 'minimum' microsecond length based on the minimum pulse of 150
#define USMAX  (2400) // This is the rounded 'maximum' microsecond length based on the maximum pulse of 600
#define SERVO_FREQ (50) // Analog servos run at ~50 Hz updates

#define NO_SERVOS (NO_MIRRORS*NO_ANGLES_PER_MIRROR)


Adafruit_PWMServoDriver servo_controller = Adafruit_PWMServoDriver(0x40);

int   myservos_angles[NO_SERVOS];

// ======================
// HELPERS
// ======================
int   get_servo(int mirror, int a) {
  return mirror * NO_ANGLES_PER_MIRROR + a;
}

bool _activate_servo(int s, int angle) {
  if ((angle >= SERVO_ANGLE_MIN) && (angle <= SERVO_ANGLE_MAX)) {
    myservos_angles[s] = angle;
    int pulse_width = map(angle, -90, 90, SERVOMIN, SERVOMAX);
    servo_controller.setPWM(s, 0, pulse_width);
    return true;
  } else {
    return false;
  }

}

// ============================
// setup
// ============================
void mirror_setup(void) {
    servo_controller.begin();
    servo_controller.setOscillatorFrequency(27000000);
    servo_controller.setPWMFreq(SERVO_FREQ);
    for (int s = 0; s < NO_SERVOS; s++) {
      myservos_angles[s] = 0;
    }
}



// ============================
// loop
// ============================
void mirror_loop(void) {


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
  return myservos_angles[get_servo(mirror, a)];
}


void mirror_set_angles(int mirror, int angles[NO_ANGLES_PER_MIRROR], bool log_serial = true) {
  for (int a = 0; a < NO_ANGLES_PER_MIRROR; a ++) {
    mirror_set_angle(mirror, a, angles[a], false);
  }
  if (log_serial) {
    mirror_serial_print_angles();
  }
}
void mirror_set_angle(int mirror, int a, int angle, bool log_serial = true) {
  _activate_servo(get_servo(mirror, a), angle);
  if (log_serial) {
    mirror_serial_print_angles();
  }
}

void mirror_add_angles(int mirror, int angles[NO_ANGLES_PER_MIRROR], bool log_serial = true) {
  for (int a = 0; a < NO_ANGLES_PER_MIRROR; a ++) {
    mirror_add_angle(mirror, a, angles[a], false);
  }
  if (log_serial) {
    mirror_serial_print_angles();
  }
}
void mirror_add_angle(int mirror, int a, int angle, bool log_serial = true) {
  int s = get_servo(mirror, a);
  int new_angle = myservos_angles[s] + angle;
  _activate_servo(s, new_angle);
  if (log_serial) {
    mirror_serial_print_angles();
  }
}


// ============
// serial logging
// ============
void mirror_serial_print_angles() {
  for (int m = 0; m < NO_MIRRORS; m ++) {
    int s = get_servo(m, 0);
    Serial.println(" mirror " + String(m) + " : " + String(myservos_angles[s]) + " , " + String(myservos_angles[s + 1]));
  }
}
