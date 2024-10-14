#include <stdio.h>
#include <wiringPi.h>

#define outputPin 0
#define C4 261.6 // hz
#define period 1
void tone() {
  long half_cycle = (long)(1000000 / (2 * C4)) long numberOfLoops =
      (long)(freq * period) for (int i = 0; i < numberOfLoops; i++) {
    setPinOn(gpioBase, outputPin);
    delayMicroseconds(half_cycle);
  }
}

void run() {
  tone();
  delay(20);
}

int main() {
  while (1) {
    run();
  }
}
