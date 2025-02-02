// #include <HTTP_Method.h>
// #include <Middlewares.h>
// #include <Uri.h>
#include <WebServer.h>

#include <WiFi.h>
#include <HardwareSerial.h>

// #include <WiFiAP.h>
// #include <WiFiClient.h>
// #include <WiFiGeneric.h>
// #include <WiFiMulti.h>
// #include <WiFiSTA.h>
// #include <WiFiScan.h>
// #include <WiFiServer.h>
// #include <WiFiType.h>
// #include <WiFiUdp.h>

#include "DHT.h"

HardwareSerial Serial2(1);  // Create Serial2 instance (Using UART1)

// #include <WiFi.h>
// #include <WebServer.h>  // ESP32 WebServer library

#define DHTPIN 33   // Pin where the sensor is connected
#define DHTTYPE DHT11 // Sensor type
#define LED_SCREEN_TX 21  // Change this if needed
#define red1 39
#define red2 37
#define WIFI_SSID "ICHACK25"  // Use the network name (SSID) here
#define WIFI_PASSWORD "p2P4v3ZnQK"  // Use the Wi-Fi password


DHT dht(DHTPIN, DHTTYPE);
WebServer server(80);  // Create a web server on port 80

// void setup() {
//   Serial.begin(9600); // Initialize the serial monitor
//   dht.begin();        // Initialize the sensor
// }

// void loop() {
//   float humidity = dht.readHumidity();           // Read humidity
//   float temperatureC = dht.readTemperature();   // Temperature in Celsius
//   float temperatureF = dht.readTemperature(true); // Temperature in Fahrenheit
//   float temperatureK = temperatureC + 273.15;   // Temperature in Kelvin

//   if (isnan(humidity) || isnan(temperatureC)) {
//     Serial.println("Error reading data!");
//     return;
//   }

//   // Output data to the serial monitor
//   Serial.print("Temperature: ");
//   Serial.print(temperatureC);
//   Serial.print("°C, ");
//   Serial.print(temperatureF);
//   Serial.print("°F, ");
//   Serial.print(temperatureK);
//   Serial.println("K");

//   Serial.print("Humidity: ");
//   Serial.print(humidity);
//   Serial.println("%");

//   delay(2000); // Delay between readings

// }

// #########################



void setup() {
  Serial.begin(9600);  // Initialize the serial monitor
  Serial2.begin(9600, SERIAL_8N1, -1, LED_SCREEN_TX);  // Initialize Serial2 for LED screen, TX only
  dht.begin();           // Initialize the sensor
  Serial.print("hi");
  
  pinMode(red1, OUTPUT);
  pinMode(red2, OUTPUT);
  digitalWrite(red1, LOW);
  digitalWrite(red2, LOW);
  // Connect to Wi-Fi
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to Wi-Fi...");
  }
  

  server.begin();  // Start the server
}

void loop() {
  
  Serial.println("Connected to Wi-Fi");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
  // Send data to LED screen
  float humidity = dht.readHumidity();
  float temperatureC = dht.readTemperature();
  String message = "Temp: " + String(temperatureC) + "C, Hum: " + String(humidity) + "%\n";
  Serial2.print(message);  // Transmit data over Serial2 (TX)

  // Handle HTTP requests
  server.on("/data", HTTP_GET, []() {
    float humidity = dht.readHumidity();
    float temperatureC = dht.readTemperature();
    if (isnan(humidity) || isnan(temperatureC)) {
      server.send(500, "text/plain", "Error reading data!");
      return;
    }
    if (temperatureC > 27.5){
      digitalWrite(red1, HIGH);
      delay(5000);  // Delay between readings

    }
    else{
      
      digitalWrite(red1, LOW);
    }
    String data = "Temperature: " + String(temperatureC) + "°C\nHumidity: " + String(humidity) + "%";
    server.send(200, "text/plain", data);


  });


  server.handleClient();  // Handle incoming client requests

  // Print temperature and humidity readings periodically
  // float humidity = dht.readHumidity();
  // float temperatureC = dht.readTemperature();
  
  // if (!isnan(humidity) && !isnan(temperatureC)) {
  //   Serial.print("Temperature: ");
  //   Serial.print(temperatureC);
  //   Serial.print("°C, Humidity: ");
  //   Serial.print(humidity);
  //   Serial.println("%");
  // }

  delay(2000);  // Delay between readings
}