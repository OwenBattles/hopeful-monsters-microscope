/*
 * Echo test sketch - use this to verify Python ↔ Arduino serial communication.
 *
 * Upload this to your Arduino, close the Serial Monitor, then run:
 *   python test_arduino_connection.py
 *
 * You should see "PONG" when you send "PING" from a terminal, or use the
 * Python test script which just reads - this sketch will print "READY" on boot
 * and echo back any line you send (prefixed with "ECHO:").
 */

void setup() {
  Serial.begin(115200);
  Serial.println("READY");
}

void loop() {
  if (Serial.available()) {
    String line = Serial.readStringUntil('\n');
    line.trim();
    if (line.length() > 0) {
      if (line == "PING") {
        Serial.println("PONG");
      } else {
        Serial.print("ECHO: ");
        Serial.println(line);
      }
    }
  }
}
