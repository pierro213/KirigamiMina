

unsigned long timer = 0;
long loopTime = 5000;   // microseconds
const int numReadings = 10;

float readings[numReadings];      // the readings from the analog input
int readIndex = 0;              // the index of the current reading
float total = 0;                  // the running total
float average = 0;                // the average
unsigned int resistor = 10000;  // the resistor in series with the kirigami
float currentValue = 0;          // the tension value read between the kirigami and resistor (so the tension at the border of the resistor, 0-1023)
float previous = 0;             // for filtration use
float valueKirigami = 0;        // the final resistivity of the kirigami
float previousFiltered = 0;
float filtered = 0;
const int LED1 = 3;
const int LED2 = 5;
const int LED3 = 9;
int kirigamiPin = A0;

void setup() {
  // initialize serial communication with computer:
  
  pinMode(LED1, OUTPUT);
  pinMode(LED2, OUTPUT);
  pinMode(LED3, OUTPUT);
  timer = micros();
  Serial.begin(38400);
  // initialize all the readings to 0:
  for (int thisReading = 0; thisReading < numReadings; thisReading++) {
    readings[thisReading] = 0;
  }
}

void loop() {
  timeSync(loopTime);
  // subtract the last reading:
  total = total - readings[readIndex];
  // read from the sensor:
  previous = currentValue;
  currentValue = (analogRead(kirigamiPin)/1023.0) * 5.0;
  previousFiltered = filtered;
  filtered = 0.969*previousFiltered + 0.0155*currentValue + 0.0155*previous;


  
  valueKirigami = 5.0*(resistor/filtered) - resistor;
  readings[readIndex] = valueKirigami;
  // add the reading to the total:
  total = total + readings[readIndex];
  // advance to the next position in the array:
  readIndex = readIndex + 1;
//Serial.println(valueKirigami);
  // if we're at the end of the array...
  if (readIndex >= numReadings) {
    // ...wrap around to the beginning:
    readIndex = 0;
  }

  // calculate the average:
  average = total / numReadings;
  // send it to the computer as ASCII digits
  //Serial.println(average);
  sendToPC(&average);  
  //delay(100);        // delay in between reads for stability
  int m = map(average, 10000, 3500, 0, 765);
  if (m > 510)
{
  int v = m-510;  
  analogWrite(LED1, 255);
  analogWrite(LED2, 255);
  analogWrite(LED3, v);
}
else if (m > 255)
{
  int v1 = m-510;  
  analogWrite(LED1, 255);
  analogWrite(LED2, v1);
  analogWrite(LED3, 0); 
}
else
{
  analogWrite(LED1, m);
  analogWrite(LED2, 0);
  analogWrite(LED3, 0); 
}
}

void timeSync(unsigned long deltaT)
{
  unsigned long currTime = micros();
  long timeToDelay = deltaT - (currTime - timer);
  if (timeToDelay > 5000)
  {
    delay(timeToDelay / 1000);
    delayMicroseconds(timeToDelay % 1000);
  }
  else if (timeToDelay > 0)
  {
    delayMicroseconds(timeToDelay);
  }
  else
  {
      // timeToDelay is negative so we start immediately
  }
  timer = currTime + timeToDelay;
}

/*void sendToPC(int* data)
{
  byte* byteData = (byte*)(data);
  Serial.write(byteData, 2);
}*/

void sendToPC(float* data)
{
  byte* byteData = (byte*)(data);
  Serial.write(byteData, 4);
}
