#include <Servo.h>
#include <math.h>

#define SERVO_MAX (130)
#define SERVO_MIN (50)


#define PIN_SERVO_1 8

#define NO_SERVOS (2)
Servo myservos[NO_SERVOS];
int   myservos_angles[NO_SERVOS];

bool sinus_motion = false;

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
      serial_print_angles();
    } else if (command.startsWith("b")) {
      long angle_read = command.substring(2).toInt();
      if ((angle_read >= 0) || (angle_read <= 180)) {
        myservos_angles[1] = angle_read;
      }
      serial_print_angles();
    } else if (command.equals("1")) {
        myservos_angles[0] = 50;
        serial_print_angles();
    } else if (command.equals("2")) {
        myservos_angles[0] = 90;
        serial_print_angles();
    } else if (command.equals("3")) {
        myservos_angles[0] = 130;
        serial_print_angles();
    } else if (command.equals("6")) {
        myservos_angles[1] = 50;
        serial_print_angles();
    } else if (command.equals("5")) {
        myservos_angles[1] = 90;
        serial_print_angles();
    } else if (command.equals("4")) {
        myservos_angles[1] = 130;
        serial_print_angles();
    } else if (command.equals("s")) {
        sinus_motion = ! sinus_motion;
    } else if (command.equals("o")) {
        myservos_angles[0] += 1;
        serial_print_angles();
    } else if (command.equals("l")) {
        myservos_angles[0] -= 1;
        serial_print_angles();
    } else if (command.equals("i")) {
        myservos_angles[1] += 1;
        serial_print_angles();
    } else if (command.equals("p")) {
        myservos_angles[1] -= 1;
        serial_print_angles();
    } else if (command.equals("O")) {
        myservos_angles[0] += 5;
        serial_print_angles();
    } else if (command.equals("L")) {
        myservos_angles[0] -= 5;
        serial_print_angles();
    } else if (command.equals("I")) {
        myservos_angles[1] += 5;
        serial_print_angles();
    } else if (command.equals("P")) {
        myservos_angles[1] -= 5;
        serial_print_angles();
    }  else if (command.equals("raw")) {
        serial_print_angles_raw();
    } else { 
        Serial.println("commands: ");
        Serial.println("  a 10   : set the servo 1 to 10 degrees");
        Serial.println("  b 10   : set the servo 2 to 10 degrees");
        Serial.println("  i - p  : left - right 1 step");
        Serial.println("  o - l  : up   - down 1 step");
        Serial.println("  I - P  : left - right 5 steps");
        Serial.println("  O - L  : up   - down 5 steps");
        Serial.println("  raw    : raw log position");
        Serial.println("  restart: restart micro controller");
        Serial.flush();
    }
  } 
}

void serial_print_angles() {
  Serial.println(" [a , b ] = " + String(myservos_angles[0]) + " , " + String(myservos_angles[1]) );
}
void serial_print_angles_raw() {
  Serial.println("" + String(myservos_angles[0]) + " , " + String(myservos_angles[1]) );
}


void setup() {
  Serial.begin(115200);
  Serial.println("Boot Started");

  for (int s = 0; s < NO_SERVOS; s ++) {
    myservos[s].attach(PIN_SERVO_1+s);  
    myservos_angles[s] = 90;
  }
  


}

void loop() {
  static int dir  = 1;
  static int pos = 0;

  loop_serial();

  if (sinus_motion) {
    sinus_loop();
  }

  for (int s = 0; s < NO_SERVOS; s++) {
    if (myservos_angles[s] > SERVO_MAX) {
      myservos_angles[s] = SERVO_MAX;
      Serial.println(" SERVO MAX LIMIT for servo " + String(s));
    } else if (myservos_angles[s] < SERVO_MIN) {
      myservos_angles[s] = SERVO_MIN;
      Serial.println(" SERVO MIN LIMIT for servo " + String(s));
    }
    myservos[s].write(myservos_angles[s]);              // tell servo to go to position in variable 'pos'
  }
  delay(0);                       // waits 15ms for the servo to reach the position

  
}

void sinus_loop() {
  float phase = (float) millis() / 1000 ;

  float a0 = 90.0 + 40 * cos(phase);
  float a1 = 90.0 + 40 * sin(phase);

  myservos_angles[0] = (int) a0;
  myservos_angles[1] = (int) a1;
  
 }
