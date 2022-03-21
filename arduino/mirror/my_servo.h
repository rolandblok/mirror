#ifndef MY_SERVO_AA
#define MY_SERVO_AA

#include <Arduino.h>
#include <Servo.h>



#include "my_config.h"

#define SERVO_MAX  (130)
#define SERVO_MIN  (50)

#define PIN_SERVO_1 (8)

/**
 * BROWN  = GROUND
 * RED    = 5V
 * ORANGE = signal (pwm)
 */

void servo_setup(void);
void servo_loop(void);

// ============================
// position getters and setters
// ============================
void servo_get_calibrated_angles(int angles_ret[NO_SERVOS]);
int  servo_get_calibrated_angle(int s);
int  servo_get_raw_angle(int s);

void servo_set_calibrated_angles(int angles[NO_SERVOS], bool log_serial=true);
void servo_set_calibrated_angle(int s, int angle, bool log_serial=true);
void servo_set_raw_angle(int s, int angle, bool log_serial=true);

void servo_add_angles(int angles[NO_SERVOS], bool log_serial=true);
void servo_add_angle(int s, int angle, bool log_serial=true);

// ============
// zero
// ============
void servo_zero();

// ============
// serial logging
// ============
void servo_serial_print_calibrated_angles() ;
void servo_serial_print_raw_angles() ;
void servo_serial_print_zero_offsets() ;

// ============
// debug movement.
// ============
void servo_switch_sinus_loop();


#endif
