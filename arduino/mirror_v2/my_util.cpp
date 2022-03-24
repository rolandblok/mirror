#include "my_util.h"

// =============
// UTIL functions
int string_read_int(String s) {
    return s.substring(1+s.indexOf(',')).toInt();
}
void string_read_ints(String s, int *ser_data) {
  int comma_index = 0;
  int data_index = 0;
  while (true) {
      comma_index = s.indexOf(',', comma_index);
      if (comma_index == -1) {
        return;
      } else {
        ser_data[data_index] = s.substring(1+comma_index).toInt();
        data_index ++;
      }
  }
}
