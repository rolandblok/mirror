#ifndef MY_EEPROM_AA
#define MY_EEPROM_AA


//==========================
#define NO_SERVOS          (2)

void  eeprom_setZeroOffsets(int zo[NO_SERVOS]);  
void  eeprom_getZeroOffsets(int zo[NO_SERVOS]);  

void eeprom_serial();


bool eeprom_init();
bool eeprom_write();
void eeprom_clear();

#endif
