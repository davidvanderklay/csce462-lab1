import pigpio
import time

# Configuration
SPEAKER_PIN = 18  # GPIO pin connected to the speaker
FREQUENCY = 15000  # Frequency in Hz
DURATION = 2  # Duration in seconds


def generate_tone(frequency, duration):
    pi = pigpio.pi()
    if not pi.connected:
        print("Could not connect to pigpio daemon.")
        return

    pi.set_mode(SPEAKER_PIN, pigpio.OUTPUT)

    # Start square wave
    pi.wave_add_new()
    wave = []
    high_time = int(500000 / frequency)  # Microseconds for HIGH
    low_time = high_time  # Microseconds for LOW
    wave.append(pigpio.pulse(1 << SPEAKER_PIN, 0, high_time))  # Set HIGH
    wave.append(pigpio.pulse(0, 1 << SPEAKER_PIN, low_time))  # Set LOW
    pi.wave_add_generic(wave)
    wave_id = pi.wave_create()

    if wave_id >= 0:
        pi.wave_send_repeat(wave_id)
        print(f"Generating {frequency} Hz tone for {duration} seconds.")
        time.sleep(duration)
        pi.wave_tx_stop()
        pi.wave_delete(wave_id)

    pi.stop()
    print("Tone generation complete.")


if __name__ == "__main__":
    try:
        generate_tone(FREQUENCY, DURATION)
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
