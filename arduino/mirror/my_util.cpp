#include "my_util.h"

// =============
// UTIL functions
int string_read_int(String s) {
    return s.substring(1+s.indexOf(' ')).toInt();
}
void string_read_int1(String s, int ser_data[1]) {
  ser_data[0] = s.substring(1+s.indexOf(' ')).toInt();
}
void string_read_int2(String s, int ser_data[2]) {
  ser_data[0] = s.substring(1+s.indexOf(' ')).toInt();
  ser_data[1] = s.substring(1+s.indexOf(',')).toInt();
}
void string_read_int3(String s, int ser_data[3]) {
  ser_data[0] = s.substring(1+s.indexOf(' ')).toInt();
  int comma_in = s.indexOf(',');
  ser_data[1] = s.substring(1+comma_in).toInt();
  comma_in = s.indexOf(',', comma_in);
  ser_data[2] = s.substring(1+comma_in).toInt();
}
