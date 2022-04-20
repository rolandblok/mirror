#ifndef MY_SMOOTH_SERVO_AA
#define MY_SMOOTH_SERVO_AA

#define NO_SERVOS (16)

#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>



class MySmoothServo {
  private :
    Adafruit_PWMServoDriver servo_controller;
    float target_angles[NO_SERVOS]; // degrees
    float cur_angles[NO_SERVOS];    // degrees
    float cur_speeds[NO_SERVOS];    // degrees / ms
    long  last_update_ms;           // ms
    bool  smooth_enabled ; 

    float active_deadband[NO_SERVOS];
    void  actuate_angle(int s);     // actuate the servo
    

  public:
    
    MySmoothServo(int adress_offset = 0);
    void setup(void);
    void loop(void);
    void servo_smooth(bool enable);
    float  get_target(int s);
    void   set_target(int s, float angle);
    void   add_target(int s, float angle);


};



#endif
