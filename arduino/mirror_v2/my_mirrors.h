#ifndef MY_MIRROR_AA
#define MY_MIRROR_AA

#include <Arduino.h>

#define NO_MIRRORS (8)
#define NO_ANGLES_PER_MIRROR (2)


/**
 * BROWN  = GROUND
 * RED    = 5V
 * ORANGE = signal (pwm)
 */

void mirror_setup(void);
void mirror_loop(void);

// ============================
// position getters and setters
// ============================
void mirror_get_angles(int mirror, int angles_ret[NO_ANGLES_PER_MIRROR]) ;
int  mirror_get_angle(int mirror, int a);

void mirror_set_angles(int mirror, int angles[NO_ANGLES_PER_MIRROR], bool log_serial=true);
void mirror_set_angle(int mirror, int a, int angle, bool log_serial=true);

void mirror_add_angles(int mirror, int angles[NO_ANGLES_PER_MIRROR], bool log_serial=true);
void mirror_add_angle(int mirror, int a, int angle, bool log_serial=true);

// ============
// serial logging
// ============
void mirror_serial_print_angles(int mirror) ;
void mirror_serial_print_all_angles() ;



#endif
