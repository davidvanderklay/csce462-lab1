
#include <stdio.h>
#include <wiringPi.h>
#include <wiringPiSPI.h>

#define SPI_CHANNEL 0
#define SPI_SPEED 1350000
#define MCP3008_CHAN 0

int readADC(int channel) {
  unsigned char buffer[3];
  buffer[0] = 1;
  buffer[1] = (8 + channel) << 4;
  buffer[2] = 0;

  wiringPiSPIDataRW(SPI_CHANNEL, buffer, 3);

  int adcValue = ((buffer[1] & 3) << 8) + buffer[2];
  return adcValue;
}

int main() {
  if (wiringPiSPISetup(SPI_CHANNEL, SPI_SPEED) == -1) {
    printf("Failed to initialize SPI\n");
    return 1;
  }

  FILE *outputFile = fopen("mic_data.csv", "w");
  if (!outputFile) {
    printf("Error opening file for writing\n");
    return 1;
  }

  fprintf(outputFile, "ADC Value,Voltage\n"); // CSV header

  for (int i = 0; i < 10000; i++) { // Record 10,000 samples
    int adcValue = readADC(MCP3008_CHAN);
    double voltage = (adcValue / 1023.0) * 3.3;

    fprintf(outputFile, "%d,%.2f\n", adcValue, voltage); // Write to file
    delay(1); // Adjust delay for your needs
  }

  fclose(outputFile);
  printf("Data written to mic_data.csv\n");

  return 0;
}
