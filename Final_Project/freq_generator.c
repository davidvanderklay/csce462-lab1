
#include <stdio.h>
#include <wiringPi.h>

#define outputPin 1 // WiringPi pin 1 corresponds to GPIO18, which supports PWM
#define FREQ 5000   // 5 kHz

void tone() {
  long half_cycle =
      (long)(1000000 /
             (2 * FREQ));    // Calculate half-cycle duration in microseconds
  long numberOfLoops = FREQ; // Number of cycles per second (frequency)

  for (int i = 0; i < numberOfLoops; i++) {
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
    tone();   // Generate the tone
    delay(1); // Small delay to ensure continuous tone
  }

  return 0;
}
