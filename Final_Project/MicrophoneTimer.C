#include <wiringPi.h>
#include<mcp3004.h>
#include <iostream>
#include <stdio.h>
#include <string> // std::string

using std::cout, std::cin, std::endl, std::string;

#define BASE 100
#define SPI_CHAN 0
#define MICROPHONE_CHAN 0
#define outputPin 1
#define FREQ 1000
#define BEEP_DURATION 100
#define THRESHOLD 1.2

void SendSignal() {
  long half_cycle = (long)(1000000 / (2 * FREQ));
  long cycles = (BEEP_DURATION * FREQ) / 1000;

  for (int i = 0; i < cycles; i++) {
    digitalWrite(outputPin, HIGH);
    delayMicroseconds(half_cycle);
    digitalWrite(outputPin, LOW);
    delayMicroseconds(half_cycle);
  }
}

double WaitForPing() {
  int Counter = 0;
  while (1) {
    Counter++;
    int adcValue = analogRead(BASE + MICROPHONE_CHAN);
    double voltage = (adcValue / 1023.0) * 3.3;
    if (voltage > THRESHOLD) {
      double time_ms = Counter / 1000.0;
      printf("Time: %.2fms | ADC Value: %d | Voltage: %.2fV\n", time_ms, adcValue, voltage);
      return time_ms;
    }
    delayMicroseconds(1);
  }
}

int main(void) {
  wiringPiSetup();
  mcp3004Setup(BASE, SPI_CHAN);
  pinMode(outputPin, OUTPUT);
  std::string temp;
  
  while (1) {
    cout << "Press enter to send a signal: " << endl;
    cin >> temp;
    SendSignal();
    WaitForPing();
  }
}
