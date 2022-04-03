#include "my_smooth_servo.h"
#include "my_util.h"


//https://rootsaid.com/pca9685-servo-driver/

#define SERVOMIN  (150) // This is the 'minimum' pulse length count (out of 4096)
#define SERVOMAX  (600) // This is the 'maximum' pulse length count (out of 4096)
#define USMIN  (600) // This is the rounded 'minimum' microsecond length based on the minimum pulse of 150
#define USMAX  (2400) // This is the rounded 'maximum' microsecond length based on the maximum pulse of 600
#define SERVO_FREQ (50) // Analog servos run at ~50 Hz updates

// Smooth Moving.
#define MAX_ACCEL (500e-6)    // degrees / ms^2
#define MAX_SPEED (500e-3)   // degrees / ms
#define ANGLE_ACCURACY  (1)  // degree
#define TICK_TIME  (10)      // ms


MySmoothServo::MySmoothServo(int adress_offset = 0) {
  servo_controller = Adafruit_PWMServoDriver(0x40 + adress_offset);

}

void MySmoothServo::setup(void) {
  servo_controller.begin();
  servo_controller.setOscillatorFrequency(27000000);
  servo_controller.setPWMFreq(SERVO_FREQ);
  for (int s = 0; s < NO_SERVOS; s++) {
    cur_angles[s] = 0;
    cur_speeds[s] = 0;
    set_target(s, 0);
    actuate_angle(s);
  }
  last_update_ms = millis();

}

void MySmoothServo::loop(void) {
  float d_time_ms = (float)(millis() - last_update_ms);
  if (d_time_ms > TICK_TIME) {
    for (int s = 0; s < NO_SERVOS; s ++) {
      float target_angle = target_angles[s];
      float err = target_angle - cur_angles[s];
      if ( abs ( err ) > ANGLE_ACCURACY ) {    
      
        boolean thisDir = ( cur_speeds[s] * cur_speeds[s] / MAX_ACCEL / 2.0 >= abs ( err )) ;
        cur_speeds[s] += MAX_ACCEL * d_time_ms * ( thisDir ? - _sign ( cur_speeds[s] ) : _sign ( err )) ;
        cur_speeds[s] = constrain ( cur_speeds[s], -MAX_SPEED, MAX_SPEED) ;
        cur_angles[s] += d_time_ms * cur_speeds[s];

        actuate_angle(s);
        Serial.println(String(s) + " "  + String(target_angles[s]) +" " + String(cur_angles[s]) +" " + String(cur_speeds[s]) );
      } else {
        cur_speeds[s] = 0;
        cur_angles[s] = target_angles[s];
      }
    }
    last_update_ms = millis();
  }

  
}

float  MySmoothServo::get_target(int s){
  return(target_angles[s]);
}

void MySmoothServo::add_target(int s, float angle) {
  set_target(s, target_angles[s] + angle);
}

void MySmoothServo::set_target(int s, float angle) {
  target_angles[s] = angle;
}

void MySmoothServo::actuate_angle(int s) {
  int pulse_width = map(cur_angles[s], -90.0, 90.0, SERVOMIN, SERVOMAX);
  Serial.println(" actuate " + String(s) +" " + String(pulse_width));
  servo_controller.setPWM(s, 0, pulse_width);
}
