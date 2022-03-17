#include <Wire.h>


void(*resetFunc) (void) = 0; 

// ===============
// serial business
// ===============
void loop_serial() {
  // ===============
  // serial business
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil(10);
    if (command.equals("restart")) {
      Serial.end();  //clears the serial monitor  if used
      resetFunc();
      delay(1000);
    } elif (command.startsWith("c") {
      
    }
  }
}



void setup() {
  // put your setup code here, to run once:
  Wire.begin();
  Serial.begin(115200);
}



void loop() {
  // put your main code here, to run repeatedly:

  loop_serial();


}
