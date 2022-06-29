#ifndef MY_SMOOTH_SERVO_AA
#define MY_SMOOTH_SERVO_AA

#define NO_STEPPERS (2)

#include <Arduino.h>
#include <Wire.h>
#include "AccelStepper.h"

typedef enum HomeStates {IDLE = 0, SEARCHING, MOVEBACK, HOMED} HomeStates;


class MySteppers {
  private :
    AccelStepper steppers[NO_STEPPERS];

    HomeStates home_states[NO_STEPPERS];
    bool       error_state;

    int  other_stepper(int s);
    bool home_stepper(int s) ;

  public:
    
    MySteppers();
    void start_homing(void);
    void loop(void);
    bool home(void);
    float  get_target(int s);
    void   set_target(int s, float angle);
    void   add_target(int s, float angle);


};

#endif
