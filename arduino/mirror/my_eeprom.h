#ifndef MY_EEPROM_AA
#define MY_EEPROM_AA


//==========================
#define NO_SERVOS          (2)

void  eeprom_setZeroOffsets(int zo[NO_SERVOS]);  
void  eeprom_getZeroOffsets(int zo[NO_SERVOS]);  

void  eeprom_setI2CAdress(uint8_t i2c_adress);
uint8_t  eeprom_getI2CAdress();


void eeprom_serial();


bool eeprom_init();
bool eeprom_write();
void eeprom_clear();

#endif
