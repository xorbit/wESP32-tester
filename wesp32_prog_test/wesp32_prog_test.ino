// wESP32-Prog tester using STM8S103 board and sDuino

#define IO0   PA1
#define EN    PA2

void setup() {
  // Initialize digital pin LED_BUILTIN as an output.
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, 1);
  // Initialize EN and IO0 test pins as input with pullup
  pinMode(IO0, INPUT_PULLUP);
  pinMode(EN, INPUT_PULLUP);
  
  // Init serial port to 115200 bps
  Serial_begin(115200);
}

void loop() {
  // Read a byte from serial port
  int c = Serial_read();
  // Did we get a byte?
  if (c >= 0) {
    // Set lowest bit to value of IO0
    c = (c & 0xFE) | (digitalRead(IO0) ? 0x01 : 0);
    // Set second lowest bit to value of EN
    c = (c & 0xFD) | (digitalRead(EN) ? 0x02 : 0);
    // Echo byte back with altered IO0 and EN bits
    Serial_write(c);
    // Set the green LED state according to the second highest bit
    digitalWrite(LED_BUILTIN, (c & 0x40) ? 0 : 1);
  }
}
