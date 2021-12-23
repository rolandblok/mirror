#include <Servo.h>


#define PIN_SERVO_1 8

#define NO_SERVOS (2)
Servo myservos[NO_SERVOS];
int   myservos_angles[NO_SERVOS];
/**
 * BROWN  = GROUND
 * RED    = 5V
 * ORANGE = signal (pwm)
 */

void(*resetFunc) (void) = 0; 



void loop_serial() {
  // ===============
  // serial business
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil(10);
    if (command.equals("restart")) {
      Serial.end();  //clears the serial monitor  if used
      resetFunc();
      delay(1000);
    } else if (command.startsWith("a")) {
      long angle_read = command.substring(2).toInt();
      if ((angle_read >= 0) || (angle_read <= 180)) {
        myservos_angles[0] = angle_read;
      }
    } else if (command.startsWith("b")) {
      long angle_read = command.substring(2).toInt();
      if ((angle_read >= 0) || (angle_read <= 180)) {
        myservos_angles[1] = angle_read;
      }
    } else { 
        Serial.println("commands: ");
        Serial.println("  a 10   : set the servo 1 to 10 degrees");
        Serial.println("  b 10   : set the servo 2 to 10 degrees");
        Serial.println("  restart: restart micro controller");
        Serial.flush();
    }
  } 
}


void setup() {
  Serial.begin(115200);
  Serial.println("Boot Started");

  for (int s = 0; s < NO_SERVOS; s ++) {
    myservos[s].attach(PIN_SERVO_1+s);  
    myservos_angles[s] = 0;
  }
  


}

void loop() {
  static int dir  = 1;
  static int pos = 0;

  loop_serial();

  for (int s = 0; s < NO_SERVOS; s++) {
    myservos[s].write(myservos_angles[s]);              // tell servo to go to position in variable 'pos'
  }
  delay(15);                       // waits 15ms for the servo to reach the position

  
}
