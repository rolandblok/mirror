#include "my_steppers.h"
#include "my_util.h"

// https://rootsaid.com/pca9685-servo-driver/

#define STEPPER_ANGLE_MIN (-800)
#define STEPPER_ANGLE_MAX (800)

// Smooth Moving.
#define HOME_STEPS (1000)
#define HOME_BACK_STEPS (360)
#define WORK_ACCEL (1600)
#define WORK_SPEED (1600)
#define HOME_ACCEL (200)
#define HOME_SPEED (400)

//                                      0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15
const int DIR_PINS[NO_STEPPERS] = {2, 4};//, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32};
const int STEP_PINS[NO_STEPPERS] = {3, 5};//, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33};
const int SWITCH_PINS[NO_STEPPERS] = {6,7};//{34, 35, 36, 37, 38, 39, 40, 41, 42, 42, 43, 44, 45, 46, 47, 48};
const int ENABLE_PIN = 24;



MySteppers::MySteppers()
{
  pinMode(ENABLE_PIN, OUTPUT); 
  digitalWrite(ENABLE_PIN, LOW); 
  for (int s = 0; s < NO_STEPPERS; s++)
  {
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
void MySteppers::loop(void)
{
  
  if (error_state)
  {

    return;
  }

  bool homed = true;
  for (int s = 0; s < NO_STEPPERS; s++)
  {
    homed = homed && (home_states[s] == HOMED);
  }


  if (homed)
  {
    for (int s = 0; s < NO_STEPPERS; s++)
    {
      if (!digitalRead(SWITCH_PINS[s]))
      {
        Serial.println("ES " + String(s) + " stop");
        error_state = true;
        return;
      }
      steppers[s].run();
    }
  } else {
    for (int s = 0; s < NO_STEPPERS; s += 2)
    {
      if (home_states[s] != HOMED)
      {
        home_stepper(s);
      } else {
        home_stepper(s + 1);
      }
    }
  }
}

float MySteppers::get_target(int s)
{
  return ((float)steppers[s].targetPosition());
}

void MySteppers::add_target(int s, float angle)
{
  set_target(s, (float)steppers[s].targetPosition() + angle);
}

void MySteppers::set_target(int s, float angle)
{

  if (angle > STEPPER_ANGLE_MAX)
  {
    angle = STEPPER_ANGLE_MAX;
  } else if (angle < STEPPER_ANGLE_MIN) {
    angle = STEPPER_ANGLE_MIN;
  }
  steppers[s].moveTo(angle);
}

/**
 * @brief start the homing of all servos.
 *
 */
void MySteppers::start_homing()
{
  Serial.println("start homeing");
  for (int s = 0; s < NO_STEPPERS; s++)
  {
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
bool MySteppers::home_stepper(int s)
{

  if (home_states[s] == HOMED)
  {
    return true;
  }

  if (home_states[s] == IDLE)
  {
    return false;
  }

  // Check if other switch is hit : error state
  int s2 = other_stepper(s);
  if (!digitalRead(SWITCH_PINS[s2]))
  {
    Serial.println("@homing : trigger " + String(s2) + " during homing " + String(s) + " NOK:error");
    error_state = true;
    return false;
  }

  if (home_states[s] == SEARCHING)
  {
    if (!digitalRead(SWITCH_PINS[s]))
    {
      Serial.println("homed " + String(s) + " , move back");
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
    if (steppers[s].isRunning())
    {
      steppers[s].run();
    }
    else
    {
      home_states[s] = HOMED;
      steppers[s].setCurrentPosition(0);
      Serial.println("s " + String(s) + " homed");

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
int MySteppers::other_stepper(int s)
{
  return s + ((s % 2 == 1) ? -1 : 1);
}
