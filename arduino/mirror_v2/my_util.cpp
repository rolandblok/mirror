#include "my_util.h"

// =============
// UTIL functions
int string_read_int(String s) {
    return s.substring(1+s.indexOf(',')).toInt();
}
int string_read_ints(String s, int *ints) {
  int comma_index = 0;
  int data_index = 0;
  while (true) {
      comma_index = s.indexOf(',', comma_index+1);
      if (comma_index == -1) {
        return data_index;
      } else {
        ints[data_index] = s.substring(1+comma_index).toInt();
        data_index ++;
      }
  }
}
