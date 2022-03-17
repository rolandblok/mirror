

#include "my_config.h"
#include "my_servo.h"

void setup_i2c(void);
void loop_i2c(void);

void i2c_send_delta(uint8_t adress,  int x, int y);
void i2c_send_cal_pos(uint8_t adress, int x, int y);
void i2c_send_zero(uint8_t adress);
Point i2c_get_calibrated_pos(uint8_t adress);
