#ifndef MY_I2C_AA
#define MY_I2C_AA


#include <Arduino.h>

#include "my_config.h"


void i2c_setup(void);
void i2c_loop(void);

void i2c_send_delta(uint8_t adress,  int x, int y);
void i2c_send_cal_pos(uint8_t adress, int x, int y);
void i2c_send_zero(uint8_t adress);
Point i2c_get_calibrated_pos(uint8_t adress);

#endif
