#ifndef MY_UTIL_AA
#define MY_UTIL_AA

#include <Arduino.h>

#include "my_config.h"

// =============
// UTIL functions
int string_read_int(String s) ;
void string_read_int1(String s, int ser_data[1]) ;
void string_read_int2(String s, int ser_data[2]) ;
void string_read_int3(String s, int ser_data[3]) ;

#endif