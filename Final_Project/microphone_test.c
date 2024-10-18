
#include <mcp3004.h>
#include <stdio.h>
#include <wiringPi.h>

#define BASE 100   // Base pin for MCP3004 (or MCP3008)
#define SPI_CHAN 0 // SPI channel (CE0)
#define MICROPHONE_CHAN                                                        \
  0 // MCP3004/3008 channel where microphone is connected (channel 0)

int main(void) {
  // Initialize WiringPi and MCP3004/3008
  wiringPiSetup();
  mcp3004Setup(BASE, SPI_CHAN); // Use MCP3004/3008 with BASE 100 and SPI channel 0

  // Main loop to read from microphone
  while (1) {
    int adcValue =
        analogRead(BASE + MICROPHONE_CHAN); // Read from channel 0 (microphone)
    double voltage =
        (adcValue / 1023.0) *
        3.3; // Convert ADC value to voltage (assuming 3.3V reference)

    printf("ADC Value: %d | Voltage: %.2fV\n", adcValue,
           voltage); // Print ADC value and voltage

    delay(100); // Small delay between readings (adjust as needed)
  }

  return 0;
}
