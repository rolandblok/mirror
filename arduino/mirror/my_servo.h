
#include <Servo.h>
#include <Arduino.h>


#include "my_config.h"

#define SERVO_MAX  (130)
#define SERVO_MIN  (50)

#define PIN_SERVO_1 (8)

/**
 * BROWN  = GROUND
 * RED    = 5V
 * ORANGE = signal (pwm)
 */

Servo myservos[NO_SERVOS];
int   myservos_angles[NO_SERVOS];
int   myservos_angles_zero_offsets[NO_SERVOS];

void servo_setup(void);
void servo_loop(void);

// ============================
// position getters and setters
// ============================
void servo_get_calibrated_angles(int angles_ret[NO_SERVOS]);
int  servo_get_calibrated_angle(int s);
void servo_set_calibrated_angles(int angles[NO_SERVOS]);
void servo_set_calibrated_angle(int s, int angle);

// ============
// zero
// ============
void servo_zero();


void servo_switch_sinus_loop();
