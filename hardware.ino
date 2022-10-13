int sensor = 18;              // the pin that the sensor is atteched to
int state = LOW;             // by default, no motion detected
int val = 0;                 // variable to store the sensor status (value)

void setup() {
  pinMode(sensor, INPUT);    // initialize sensor as an input
  Serial.begin(115200);        // initialize serial
}

void loop(){
  val = digitalRead(sensor);   // read sensor value
  if(val == 1){
    Serial.println("Trigger");
    delay(5000);
  }
}
