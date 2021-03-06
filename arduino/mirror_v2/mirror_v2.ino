#include "HardwareSerial.h"
#include "SoftwareSerial.h"

#include "my_util.h"
#include "my_mirrors.h"

// PIN 5 : SCL
// PIN 4 : SDA

void(*resetFunc) (void) = 0; 

bool sinus_move = false;
unsigned long sinus_last_update_ms = 0;

// ===============
// serial business
void serial_loop() {
  static int selected_mirror = 0;
  
  if (Serial.available() > 0) {
    String ser_command = Serial.readStringUntil('\n');
    float ser_data[8] = {}; 
    if (ser_command.startsWith("R")) {   // Restart
        Serial.end();  //clears the serial monitor  if used
        resetFunc();
        delay(1000);
    } else if (ser_command.startsWith("a")) {
        string_read_floats(ser_command, ser_data);
        mirror_set_angle((int)(ser_data[0]), 0, ser_data[1]);
    } else if (ser_command.startsWith("b")){
        string_read_floats(ser_command, ser_data);
        mirror_set_angle((int)(ser_data[0]), 1, ser_data[1]);
    } else if (ser_command.startsWith("c")){
        string_read_floats(ser_command, ser_data);
        mirror_set_angles((int)(ser_data[0]), ser_data+1, true);
    } else if (ser_command.startsWith("d")){
        string_read_floats(ser_command, ser_data);
        mirrors_set_8angles(0, ser_data);
    } else if (ser_command.startsWith("e")){
        string_read_floats(ser_command, ser_data);
        mirrors_set_8angles(4, ser_data);
    } else if (ser_command.startsWith("A")) {
        string_read_floats(ser_command, ser_data);
        mirror_add_angle((int)(ser_data[0]), 0, ser_data[1]);
    } else if (ser_command.startsWith("B")) {
        string_read_floats(ser_command, ser_data);
        mirror_add_angle((int)(ser_data[0]), 1, ser_data[1]);
    } else if (ser_command.startsWith("C")){
        string_read_floats(ser_command, ser_data);
        mirror_add_angles((int)(ser_data[0]), ser_data+1);
    } else if (ser_command.startsWith("m")) {
        selected_mirror = string_read_int(ser_command);
    } else if (ser_command.startsWith("1")) {
        mirror_set_angle(selected_mirror, 0, -35);
    } else if (ser_command.startsWith("2")) {
        mirror_set_angle(selected_mirror, 0, 0);
    } else if (ser_command.startsWith("3")) {
        mirror_set_angle(selected_mirror, 0, 35);
    } else if (ser_command.startsWith("6")) {
        mirror_set_angle(selected_mirror, 1, -35);
    } else if (ser_command.startsWith("5")) {
        mirror_set_angle(selected_mirror, 1, 0);
    } else if (ser_command.startsWith("4")) {
        mirror_set_angle(selected_mirror, 1, 35);
    } else if (ser_command.startsWith("o")) {
        mirror_add_angle(selected_mirror, 0, 1);
    } else if (ser_command.startsWith("l")) {
        mirror_add_angle(selected_mirror, 0, -1);
    } else if (ser_command.startsWith("i")) {
        mirror_add_angle(selected_mirror, 1, 1);
    } else if (ser_command.startsWith("p")) {
        mirror_add_angle(selected_mirror, 1, -1);
    } else if (ser_command.startsWith("O")) {
        mirror_add_angle(selected_mirror, 0, 5);
    } else if (ser_command.startsWith("L")) {
        mirror_add_angle(selected_mirror, 0, -5);
    } else if (ser_command.startsWith("I")) {
        mirror_add_angle(selected_mirror, 1, 5);
    } else if (ser_command.startsWith("P")) {
        mirror_add_angle(selected_mirror, 1, -5);
    } else if (ser_command.startsWith("km")) {
        int mirror = string_read_int(ser_command);
        mirror_serial_print_angles(mirror);
    } else if (ser_command.startsWith("kp")) {
        mirror_serial_print_all_angles();
    } else if (ser_command.startsWith("son")) {
        mirror_smooth(true);
    } else if (ser_command.startsWith("soff")) {
        mirror_smooth(false);
    } else if (ser_command.startsWith("s")) {
        sinus_move = !sinus_move;
    } else {         
      Serial.println("unknown command " + String(ser_command));

    
//        Serial.println("commands: ");
//        Serial.println(" Absolutes: ");
//        Serial.println("  a,0,10 : set for mirror 0 the servo 1 to 10 degrees");
//        Serial.println("  b,1,10 : set for mirror 1 the servo 2 to 10 degrees");
//        Serial.println("  c,2,-10, 10: set for mirror 2 servos 1,2 to -10, 10 degrees");
//        Serial.println("  d,1,1,2,2,3,3,4,4: set for mirror 0,1,2,3 servos 1,2 to ... degrees");
//        Serial.println("  e,1,1,2,2,3,3,4,4: set for mirror 4,5,6,7 servos 1,2 to -10, 10 degrees");
//        Serial.println(" Deltas: ");
//        Serial.println("  A,0,10 : add for mirror 0 the servo 1 with delta 10 degrees");
//        Serial.println("  B,1,-10: add for mirror 1 the servo 1 with delta -10 degrees");
//        Serial.println("  C,2,10,-10: add for mirror 2 the servos 1,2 with delta 10,-10 degrees");
//        Serial.println(" Step Moving: ");
//        Serial.println("  m 1  : select mirror 1 for step moving:");
//        Serial.println("  i - p: left - right 1 step");
//        Serial.println("  o - l: up   - down 1 step");
//        Serial.println("  I - P: left - right 5 steps");
//        Serial.println("  O - L: up   - down 5 steps");
//        Serial.println("  1,2,3,4,5,6: set selected mirror/servo to -40,0,40 degrees");
//        Serial.println(" Logging");
//        Serial.println("  km,1 : log for mirror 1 the position ");
//        Serial.println("  kp   : log position (relative to zero angle)");
//        Serial.println(" Other");
//        Serial.println("  R    : restart micro controller");
//        Serial.println("  son  : smooth move on");
//        Serial.println("  soff : smooth move off");
//        Serial.flush();
    }
  } 
  Serial.flush();
}



/** ===============================
 * Startup routine
 */
void setup() {
  Serial.begin(115200);
  Serial.println("Boot Narcissus Started");

  mirror_setup();

}

/** ===============================
 * Loop Routine
 */
void loop() {


  if (sinus_move) {
    loop_sinus();
  }
  
  serial_loop();
  mirror_loop();

  delay(20);         
}


// ====================
// for debug: SINUS move
void loop_sinus() {
  static float angle = 0;
  angle += ((float)(millis() - sinus_last_update_ms)) / 500.0;
  float a = 30 * sin(angle);
  float b = 30 * cos(angle);
  float angles[16];
  for (int i = 0 ; i < NO_MIRRORS; i++) {
    angles[i*2+0] = a;
    angles[i*2+1] = b;
  }

  mirrors_set_8angles(0, angles, false);
  mirrors_set_8angles(4, angles+8, false);
  
  sinus_last_update_ms = millis();
}
