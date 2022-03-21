#include "my_eeprom.h"

#include <Arduino.h>
#include <EEPROM.h>

#define SERVO_ZERO_DEFAULT (90)
#define NO_SERVOS          (2)
//=================================
// ROLAND IMPLEMENTATION 
//=================================

typedef struct EepromMem_struct {
  byte    valid;
  int     zero_offsets[NO_SERVOS];
  uint8_t i2c_adress;   // zero if master
  
  byte    checksum;
} EepromMem;


//extern EepromMem eeprom_mem_glb;
EepromMem eeprom_mem_glb;


// ===============
// getters setters
// ===============

void  eeprom_setZeroOffsets(int zo[NO_SERVOS]){
  for (int s = 0; s < NO_SERVOS; s++) {
    eeprom_mem_glb.zero_offsets[s] = zo[s];
  }
  eeprom_write();
}

void  eeprom_getZeroOffsets(int zo[NO_SERVOS]) {
  if (eeprom_mem_glb.valid) {
    for (int s = 0; s < NO_SERVOS; s++) {
      zo[s] = eeprom_mem_glb.zero_offsets[s];
    }
  } else {
    for (int s = 0; s < NO_SERVOS; s++) {
      zo[s] = SERVO_ZERO_DEFAULT;
    }
  }
}

void  eeprom_setI2CAdress(uint8_t i2c_adress) {
  eeprom_mem_glb.i2c_adress = i2c_adress;
  eeprom_write();
}

uint8_t  eeprom_getI2CAdress() {
  return eeprom_mem_glb.i2c_adress;
}


// ================
// SPECIFIC HELPERS
// ================
byte checksum(EepromMem eeprom_memo_arg) {
  byte checksum_v = 1;
  for (int s = 0; s < NO_SERVOS; s++) {
    checksum_v += (byte) eeprom_memo_arg.zero_offsets[s];
  }
  checksum_v += eeprom_memo_arg.i2c_adress;
  return checksum_v;
}

void _eeprom_serial(EepromMem eeprom_mem_tmp) {
  Serial.println("--EEPROM--------");
  Serial.println(" valid " + String(eeprom_mem_tmp.valid) );  
  for (int s = 0; s < NO_SERVOS; s ++) {
     Serial.println(" zero_offset [" + String(s) + "] : " + String(eeprom_mem_tmp.zero_offsets[s]));
  }
  Serial.println(" i2c adress : " + String(eeprom_mem_tmp.i2c_adress) );  
  Serial.println(" checksum " + String(eeprom_mem_tmp.checksum) );  
  Serial.println("----------------");
}
void eeprom_serial() {
  _eeprom_serial(eeprom_mem_glb);
}


void eeprom_clear() {
  for (int s = 0; s < NO_SERVOS; s++) {
    eeprom_mem_glb.zero_offsets[s] = SERVO_ZERO_DEFAULT;
  }
  eeprom_write();
}


// ===============
// GENERICS
// ===============
bool eeprom_init() {
  EepromMem eeprom_mem_tmp;
  EEPROM.get(0, eeprom_mem_tmp);
  if (eeprom_mem_tmp.valid == 1) {
    if (eeprom_mem_tmp.checksum == checksum(eeprom_mem_tmp)) {
      eeprom_mem_glb = eeprom_mem_tmp;
    } else {
      Serial.println("eeprom checksum invalid");
      return false;
    }
  } else {
    Serial.println("eeprom read invalid");
    return false;
  }

  return true;
}

bool eeprom_write() {
  eeprom_mem_glb.valid = 1;
  eeprom_mem_glb.checksum = checksum(eeprom_mem_glb);
  EEPROM.put(0, eeprom_mem_glb);

  return true;
}
