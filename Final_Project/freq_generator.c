
#include <stdio.h>
#include <wiringPi.h>

#define outputPin 1 // WiringPi pin 1 corresponds to GPIO18, which supports PWM
#define FREQ 1000   // 5 kHz
#define BEEP_DURATION 100 // Duration of the beep in milliseconds

void tone() {
  long half_cycle =
      (long)(1000000 /
             (2 * FREQ)); // Calculate half-cycle duration in microseconds
  long cycles =
      (BEEP_DURATION * FREQ) / 1000; // Number of cycles in the beep duration

  for (int i = 0; i < cycles; i++) {
    digitalWrite(outputPin, HIGH); // Set pin HIGH
    delayMicroseconds(half_cycle); // Wait for half of the cycle
    digitalWrite(outputPin, LOW);  // Set pin LOW
    delayMicroseconds(half_cycle); // Wait for the remaining half of the cycle
  }
}

int main(void) {
  wiringPiSetup();            // Initialize WiringPi
  pinMode(outputPin, OUTPUT); // Set the pin as output

  while (1) {
    tone();     // Generate the beep tone
    delay(500); // Wait for 500 ms before next beep
  }

  return 0;
}
