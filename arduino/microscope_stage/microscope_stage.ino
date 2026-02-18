/*
 * Microscope Stage Controller
 * Arduino firmware for X/Y stepper control via serial.
 *
 * Protocol:
 *   MOVE X Y   - Move to absolute position (steps)
 *   HOME       - Move to (0, 0) and set as origin
 *
 * Response: DONE (or ERR message)
 *
 * Hardware: Adafruit Metro 328 (Arduino Uno compatible)
 * Requires: AccelStepper library (Sketch > Include Library > Manage Libraries)
 *
 * Stepper driver pins (e.g. A4988, DRV8825) - adjust for your wiring:
 *   X: STEP=2, DIR=3, ENABLE=4
 *   Y: STEP=5, DIR=6, ENABLE=7
 */

#include <AccelStepper.h>

// === Pin configuration - adjust for your hardware ===
#define X_STEP_PIN  2
#define X_DIR_PIN   3
#define X_EN_PIN    4

#define Y_STEP_PIN  5
#define Y_DIR_PIN   6
#define Y_EN_PIN    7

// Driver interface: 1 = step, 1 = direction
AccelStepper stepperX(AccelStepper::DRIVER, X_STEP_PIN, X_DIR_PIN);
AccelStepper stepperY(AccelStepper::DRIVER, Y_STEP_PIN, Y_DIR_PIN);

const long MAX_SPEED = 2000;    // steps/sec
const long ACCEL = 500;         // steps/sec^2

void setup() {
  Serial.begin(115200);

  // Enable pins (LOW = enabled for most drivers)
  pinMode(X_EN_PIN, OUTPUT);
  pinMode(Y_EN_PIN, OUTPUT);
  digitalWrite(X_EN_PIN, LOW);
  digitalWrite(Y_EN_PIN, LOW);

  stepperX.setMaxSpeed(MAX_SPEED);
  stepperX.setAcceleration(ACCEL);
  stepperX.setCurrentPosition(0);

  stepperY.setMaxSpeed(MAX_SPEED);
  stepperY.setAcceleration(ACCEL);
  stepperY.setCurrentPosition(0);

  Serial.println("READY");
}

void loop() {
  if (Serial.available()) {
    String line = Serial.readStringUntil('\n');
    line.trim();
    if (line.length() == 0) return;

    if (line == "HOME") {
      stepperX.moveTo(0);
      stepperY.moveTo(0);
      runBoth();
      Serial.println("DONE");
    }
    else if (line.startsWith("MOVE ")) {
      long x = 0, y = 0;
      int idx = 5;  // skip "MOVE "
      int space = line.indexOf(' ', idx);
      if (space > 0) {
        x = line.substring(idx, space).toInt();
        y = line.substring(space + 1).toInt();
      }
      stepperX.moveTo(x);
      stepperY.moveTo(y);
      runBoth();
      Serial.println("DONE");
    }
    else {
      Serial.print("ERR unknown: ");
      Serial.println(line);
    }
  }
}

void runBoth() {
  while (stepperX.distanceToGo() != 0 || stepperY.distanceToGo() != 0) {
    stepperX.run();
    stepperY.run();
  }
}
