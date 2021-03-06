#ifndef MY_UTIL_AA
#define MY_UTIL_AA

#include <Arduino.h>


// =============
// UTIL functions, read from string like: "xyz,1,2,3,4", then get [1][2][3][4]
int string_read_int(String s) ;
int string_read_ints(String s, int *ints) ;
int string_read_floats(String s, float *floats) ;
float _sign(float x);
int   _sign(int x);


#endif
