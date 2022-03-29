

#include "my_util.h"
#include "my_mirrors.h"

void(*resetFunc) (void) = 0; 

void serial_loop() {
  static int selected_mirror = 0;
  // ===============
  // serial business
  if (Serial.available() > 0) {
    String ser_command = Serial.readStringUntil(10);
    int ser_data[3];
    if (ser_command.startsWith("R")) {   // Restart
        Serial.end();  //clears the serial monitor  if used
        resetFunc();
        delay(1000);
    } else if (ser_command.startsWith("m")) {
        selected_mirror = string_read_int(ser_command);
    } else if (ser_command.startsWith("a")) {
        ser_data[0]= string_read_int(ser_command);
        mirror_set_angle(selected_mirror, 0, ser_data[0]);
    } else if (ser_command.startsWith("b")){
        ser_data[0] = string_read_int(ser_command);
        mirror_set_angle(selected_mirror, 1, ser_data[0]);
    } else if (ser_command.startsWith("c")){
        string_read_int2(ser_command, ser_data);
        mirror_set_angles(selected_mirror, ser_data);
    } else if (ser_command.startsWith("A")) {
        ser_data[0] = string_read_int(ser_command);
        mirror_add_angle(selected_mirror, 0, ser_data[0]);
    } else if (ser_command.startsWith("B")) {
        ser_data[0] = string_read_int(ser_command);
        mirror_add_angle(selected_mirror, 1, ser_data[0]);
    } else if (ser_command.startsWith("C")){
        string_read_int2(ser_command,ser_data);
        mirror_add_angles(selected_mirror, ser_data);
    } else if (ser_command.startsWith("1")) {
        mirror_set_angle(selected_mirror, 0, -40);
    } else if (ser_command.startsWith("2")) {
        mirror_set_angle(selected_mirror, 0, 0);
    } else if (ser_command.startsWith("3")) {
        mirror_set_angle(selected_mirror, 0, 40);
    } else if (ser_command.startsWith("6")) {
        mirror_set_angle(selected_mirror, 1, -40);
    } else if (ser_command.startsWith("5")) {
        mirror_set_angle(selected_mirror, 1, 0);
    } else if (ser_command.startsWith("4")) {
        mirror_set_angle(selected_mirror, 1, 40);
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
    } else if (ser_command.startsWith("kp")) {
        mirror_serial_print_angles();
    } else {         
      Serial.println("unknown command " + String(ser_command));

    
//        Serial.println("commands: ");
//        Serial.println(" Select Servo: ");
//        Serial.println("  m,1 : select mirror 1");
//        Serial.println(" Absolutes: ");
//        Serial.println("  a,10 : set the servo 1 to 80 degrees");
//        Serial.println("  b,10 : set the servo 2 to 80 degrees");
//        Serial.println("  c,-10, 10: set the servo 1,2 to -10, 10 degrees");
//        Serial.println(" Deltas: ");
//        Serial.println("  A,10 : add the servo 1 with delta 10 degrees");
//        Serial.println("  B,-10: add the servo 1 with delta -10 degrees");
//        Serial.println("  C,10,-10: add the servo 1,2 with delta 10,-10 degrees");
//        Serial.println("  i - p: left - right 1 step");
//        Serial.println("  o - l: up   - down 1 step");
//        Serial.println("  I - P: left - right 5 steps");
//        Serial.println("  O - L: up   - down 5 steps");
//        Serial.println(" Logging");
//        Serial.println("  kp   : log position (relative to zero angle)");
//        Serial.println(" Other");
//        Serial.println("  R    : restart micro controller");
//        Serial.flush();
    }
  } 
}



/** ===============================
 * Startup routine
 */
void setup() {
  Serial.begin(115200);
  Serial.println("Boot Started");

  mirror_setup();

}

/** ===============================
 * Loop Routine
 */
 void loop() {
  serial_loop();
  mirror_loop();

  delay(0);         
}
