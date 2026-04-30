/*
  Arduino Nano 2-channel waveform source for the FPGA logic analyzer.

  Wiring:
    Nano D2  -> logic analyzer channel 0
    Nano D3  -> logic analyzer channel 1
    Nano GND -> Boolean Board / DUT GND

  Output:
    D2: 1 kHz square wave
    D3: 250 Hz square wave

  Use a 5 V tolerant level shifter if your Nano is a 5 V board. The Boolean
  Board FPGA inputs are 3.3 V only.
*/

const byte WAVE_CH0_PIN = 2;
const byte WAVE_CH1_PIN = 3;

const unsigned long CH0_HALF_PERIOD_US = 500;   // 1 kHz square wave
const unsigned long CH1_HALF_PERIOD_US = 2000;  // 250 Hz square wave

unsigned long ch0_last_toggle_us = 0;
unsigned long ch1_last_toggle_us = 0;
bool ch0_state = false;
bool ch1_state = false;

void setup() {
  pinMode(WAVE_CH0_PIN, OUTPUT);
  pinMode(WAVE_CH1_PIN, OUTPUT);

  digitalWrite(WAVE_CH0_PIN, LOW);
  digitalWrite(WAVE_CH1_PIN, LOW);
}

void loop() {
  unsigned long now_us = micros();

  if (now_us - ch0_last_toggle_us >= CH0_HALF_PERIOD_US) {
    ch0_last_toggle_us += CH0_HALF_PERIOD_US;
    ch0_state = !ch0_state;
    digitalWrite(WAVE_CH0_PIN, ch0_state ? HIGH : LOW);
  }

  if (now_us - ch1_last_toggle_us >= CH1_HALF_PERIOD_US) {
    ch1_last_toggle_us += CH1_HALF_PERIOD_US;
    ch1_state = !ch1_state;
    digitalWrite(WAVE_CH1_PIN, ch1_state ? HIGH : LOW);
  }
}
