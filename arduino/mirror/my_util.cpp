#include "my_util.h"

// =============
// UTIL functions
int string_read_int(String s) {
    return s.substring(1+s.indexOf(' ')).toInt();
}
void string_read_int2(String s, int ser_data[NO_SERVOS]) {
  ser_data[0] = s.substring(1+s.indexOf(' ')).toInt();
  ser_data[1] = s.substring(1+s.indexOf(',')).toInt();
}
