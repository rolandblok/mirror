#include "my_util.h"

// =============
// UTIL functions
int string_read_int(String s) {
    return s.substring(1+s.indexOf(',')).toInt();
}
void string_read_ints(String s, int *ser_data, int n_o_commas){
  int comma_ind = 0;
  for (int n = 0; n < n_o_commas; n ++) {
    comma_ind = s.indexOf(',', comma_ind+1);
    ser_data[n] = s.substring(1+comma_ind).toInt();
  }
}
void string_read_int1(String s, int ser_data[1]) {
  string_read_ints(s, ser_data, 1);
}
void string_read_int2(String s, int ser_data[2]) {
  string_read_ints(s, ser_data, 2);
}
void string_read_int3(String s, int ser_data[3]) {
  string_read_ints(s, ser_data, 3);

}
