#include "my_steppers.h"
#include "my_util.h"


//https://rootsaid.com/pca9685-servo-driver/

#define STEPPER_ANGLE_MIN  (-800)
#define STEPPER_ANGLE_MAX  ( 800)

// Smooth Moving.
#define HOME_STEPS      (1000)
#define HOME_BACK_STEPS (360)
#define WORK_ACCEL (1600)   
#define WORK_SPEED (1600)   
#define HOME_ACCEL (400)      
#define HOME_SPEED (100)      

const int STEP_PINS[NO_STEPPERS]    = {2,5,8,11,14,17,20,23};
const int DIR_PINS[NO_STEPPERS]     = {3,6,9,12,15,18,21,24};
const int SWITCH_PINS[NO_STEPPERS]  = {4,7,10,13,16,19,22,25};


MySteppers::MySteppers() {
  for (int s = 0; s < NO_STEPPERS; s++) {
    steppers[s] = AccelStepper(AccelStepper::DRIVER, STEP_PINS[s], DIR_PINS[s]);
    pinMode(SWITCH_PINS[s], INPUT_PULLUP);

    steppers[s].setMaxSpeed(HOME_SPEED);
    steppers[s].setAcceleration(HOME_ACCEL);
    steppers[s].moveTo(0);

    home_states[s] = IDLE;
  }
}


/**
 * @brief if steppers are homed and not triggering endstop : move them.
 *        If not home, but homing started : do the homing.
 * 
 */
void MySteppers::loop(void) {
    if (error_state) {
      return;
    }

    bool homed = true;
    for (int s = 0; s < NO_STEPPERS; s++) {
      homed = homed && (home_states[s] == HOMED);
    }

    if (homed) {
      for (int s = 0; s < NO_STEPPERS; s++) {
        if (!digitalRead(SWITCH_PINS[s])) {
          Serial.println("endstop " + String(s) + " triggered, stop");
          error_state = true;
          return;
        }
        steppers[s].run();
      }

    } else {
      for (int s = 0; s < NO_STEPPERS; s += 2) {
        if (home_states[s] != HOMED) {
          home_stepper(s);
        } else {
          home_stepper(s+1);
        }
      }
    }
}
 

float  MySteppers::get_target(int s){
  return((float) steppers[s].targetPosition());
}

void MySteppers::add_target(int s, float angle) {
  set_target(s, (float) steppers[s].targetPosition() + angle);
}

void MySteppers::set_target(int s, float angle) {
  
  if (angle > STEPPER_ANGLE_MAX ) {
    angle = STEPPER_ANGLE_MAX;
  } else if (angle < STEPPER_ANGLE_MIN ) {
    angle = STEPPER_ANGLE_MIN;
  }
  steppers[s].moveTo(angle);

}


/**
 * @brief start the homing of all servos.
 * 
 */
void MySteppers::start_homing(){
   for (int s = 0; s < NO_STEPPERS; s++) {
    home_states[s] = SEARCHING;
   }
}

/**
 * @brief Homing routine. Call in loop
 * 
 * @param s servo id
 * @return true homing is done
 * @return false homing still ongoing
 */
bool MySteppers::home_stepper(int s) {

  if (home_states[s] == HOMED) {
    return true;
  } 

  if (home_states[s] == IDLE) {
    return false;
  }

  // Check if other switch is hit : error state
  int s2 = other_stepper(s);
  if (!digitalRead(SWITCH_PINS[s2])) {
    Serial.println("@homing " + String(s)+ " stepper " + String(s2) + " switch. NOK.");
    error_state = true;
    return false;
  }
  
  if (home_states[s] == SEARCHING) {
    if (!digitalRead(SWITCH_PINS[s])) {
      home_states[s] = MOVEBACK;
      steppers[s].setMaxSpeed(WORK_SPEED);
      steppers[s].setAcceleration(WORK_ACCEL);
      steppers[s].move(-HOME_BACK_STEPS);
    } else if (steppers[s].isRunning()) {
      steppers[s].run();
    } else {
      steppers[s].move(HOME_STEPS);
    }    
  
  } else if (home_states[s] == MOVEBACK) {
    if ( steppers[s].isRunning() ) {
      steppers[s].run();
    } else {
      home_states[s] = HOMED;
      steppers[s].setCurrentPosition(0);
      Serial.println("s " + String(s) + " homed");
      
      digitalWrite(LED_BUILTIN, LOW);
      return true;
    }
  }
  
  return false;
}


/**
 * @brief return the other stepper that pairs with this one
 *     0-->1
 *     1-->0
 *     2-->3
 *     3-->2 (etc)
 * 
 * @param s stepper number
 */
int MySteppers::other_stepper(int s) {
  return s + (s%2==1)?-1:1;
}
