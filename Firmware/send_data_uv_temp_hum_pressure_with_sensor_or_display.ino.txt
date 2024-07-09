#include <Arduino.h>

// Emulate Hardware Sensor?
bool virtual_sensor = false;

#include <ESP8266WiFi.h>       // Ensure to include the ESP8266Wifi.h library, not the common library WiFi.h
#include <ESP8266HTTPClient.h> // Ensure to include the ESP8266HTTPClient.h library, not the common library HTTPClient.h
#include <WiFiClient.h>
#include <ArduinoJson.h> // Include the ArduinoJson library for JSON handling
#include <TimeLib.h>     // Include the TimeLib library for time manipulation
#include <DHT.h>         // Include the DHT library for humidity and temperature sensor handling
#include <Wire.h>
#include <Adafruit_BMP085.h>  // Include the BMP085 library
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

Adafruit_BMP085 bmp;  // Create an instance of the BMP085 class

// OLED display parameters
#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 64 // OLED display height, in pixels
#define OLED_RESET -1    // Reset pin (or -1 if sharing Arduino reset pin)
#define OLED_ADDRESS 0x3C // I2C address of the OLED display
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

String regionCode = "ap-in-1"; // Anedya region code (e.g., "ap-in-1" for Asia-Pacific/India) | For other country code, visit [https://docs.anedya.io/device/intro/#region]
String deviceID = "126eb084-8cb8-45db-9466-a86f18b3a4db";
String connectionkey = "ea9a0c8e2c5b3ec43c7507b6a1a17639"; // Fill your connection key, that you can get from your node description
// Define the type of DHT sensor (DHT11, DHT21, DHT22, AM2301, AM2302, AM2321)
#define DHT_TYPE DHT22
// Define the pin connected to the DHT sensor
#define DHT_PIN 0 // pin marked as D3 on the nodemcu
// Define I2C communication pins (adjust based on your ESP8266 board)
#define SDA_PIN D2
#define SCL_PIN D1
// Define the soil moisture sensor pin
//#define SOIL_PIN D5
// define soil and uv mux
#define S0 D6
#define S1 D7
#define S2 D8

#define ANALOG_PIN A0

float temperature;
float humidity;
float soil;
float pressure;
float uv;

char ssid[] = "HIMANSHU";     // Your WiFi network SSID
char pass[] = "88888888"; // Your WiFi network password

// Function declarations
void setDevice_time();                                       // Function to configure the NodeMCU's time with real-time from ATS (Anedya Time Services)
void anedya_submitData(String datapoint, float sensor_data); // Function to submit data to the Anedya server

// Create a DHT object
DHT dht(DHT_PIN, DHT_TYPE);

void setup()
{
  Serial.begin(9600); // Set the baud rate for serial communication

  // Connect to WiFi network
  WiFi.begin(ssid, pass);
  Serial.println();
  Serial.print("[SETUP] Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED)
  { // Wait until connected
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.print("Connected, IP address: ");
  Serial.println(WiFi.localIP());

  // Connect to ATS(Anedya Time Services) and configure time synchronization
  setDevice_time(); // Call function to configure time synchronization

  // Initialize the DHT sensor
  dht.begin();

  // Initialize the BMP180 sensor
  if (!bmp.begin()) {
    Serial.println("Couldn't find BMP180 sensor!");
    while (1);  // Halt if sensor is not found
  }

  // Initialize the OLED display
  if (!display.begin(SSD1306_SWITCHCAPVCC, OLED_ADDRESS)) {
    Serial.println(F("SSD1306 allocation failed"));
    for (;;); // Don't proceed, loop forever
  }
  display.display();
  delay(2000); // Pause for 2 seconds

  // Clear the buffer
  display.clearDisplay();

// define selective line 
  pinMode(S0, OUTPUT);
  pinMode(S1, OUTPUT);
  pinMode(S2, OUTPUT);

}

float readSensor(int channel) {
  digitalWrite(S0, bitRead(channel, 0));
  digitalWrite(S1, bitRead(channel, 1));
  digitalWrite(S2, bitRead(channel, 2));
  delay(10); // Small delay for stabilization
  return analogRead(ANALOG_PIN);
}


void loop()
{
  if (!virtual_sensor)
  {
    // Read the temperature and humidity from the DHT sensor
    Serial.println("Fetching data from the Physical sensor");
    temperature = dht.readTemperature();
    humidity = dht.readHumidity();
    if (isnan(humidity) || isnan(temperature))
    {
      Serial.println("Failed to read from DHT !");
      delay(10000);
      return;
    }
  }
  else
  {
    // Generate random temperature and humidity values
    Serial.println("Fetching data from the Virtual sensor");
    temperature = random(20, 30);
    humidity = random(60, 80);
  }

  // Read UV index from the GUVA-S12SD sensor
  float uvValue = readSensor(0);
  float uv = map(uvValue, 0, 1023, 0, 11);

  // Read soil moisture sensor on channel 1
  float soilValue = readSensor(1);
  float soil = map(soilValue, 1023, 0, 0, 100); // Assuming wet = 0, dry = 1023


  // Read pressure from BMP180 sensor
  pressure = bmp.readPressure() / 100.0; // Convert to hPa

  // Read soil moisture level (Digital Pin)
  //int soilValue = digitalRead(SOIL_PIN);
  //soil = (soilValue == LOW) ? 100 : 0; // Convert to percentage

  // Display data on OLED
  display.clearDisplay();
  display.setTextSize(1.5);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.print("Temp: ");
  display.print(temperature);
  display.println(" C");
  

  display.print("Humidity: ");
  display.print(humidity);
  display.println(" %");
  display.println("");

  display.print("UV Index: ");
  display.println(uv);
  

  display.print("Pressure: ");
  display.print(pressure);
  display.println(" hPa");
  display.println("");


  display.print("Soil: ");
  display.print(soil);
  display.println(" %");
  

  display.display();

  // Submit sensor data to Anedya server
  anedya_submitData("temperature", temperature);
  anedya_submitData("humidity", humidity);
  anedya_submitData("uvindex", uv);
  anedya_submitData("pressure", pressure);
  anedya_submitData("soil", soil);

  // Print sensor data to Serial Monitor
  Serial.println();
  Serial.println("Sensor Data:");
  Serial.print("Temperature: ");
  Serial.print(temperature);
  Serial.println(" C");

  Serial.print("Humidity: ");
  Serial.print(humidity);
  Serial.println(" %");

  Serial.print("UV Index: ");
  Serial.println(uv);

  Serial.print("Pressure: ");
  Serial.print(pressure);
  Serial.println(" hPa");

  Serial.print("Soil: ");
  Serial.print(soil);
  Serial.println(" %");
  Serial.println();

  delay(15000);
}




void setDevice_time()
{
  // URL to fetch real-time from Anedya server
  String time_url = "https://device." + regionCode + ".anedya.io/v1/time";

  // Attempt to synchronize time with Anedya server
  Serial.println("Time synchronizing......");
  int timeCheck = 1; // Iteration control
  while (timeCheck)
  {
    long long deviceSendTime = millis(); // Get the current device running time

    // Prepare the request payload
    StaticJsonDocument<200> requestPayload;
    requestPayload["deviceSendTime"] = deviceSendTime;
    String jsonPayload;
    serializeJson(requestPayload, jsonPayload);

    WiFiClientSecure client; // Anedya works only on HTTPS, so make sure to use WiFiClientSecure, not only WiFiClient
    HTTPClient http;         // Initialize an HTTP client
    client.setInsecure();

    // Send a POST request to fetch server time
    http.begin(client, time_url);
    http.addHeader("Content-Type", "application/json");

    int httpResponseCode = http.POST(jsonPayload);

    // Check if the request was successful
    if (httpResponseCode != 200)
    {
      Serial.println("Failed to fetch server time!");
      delay(2000);
    }
    else if (httpResponseCode == 200)
    {
      timeCheck = 0;
      Serial.println("synchronized!");
    }

    // Parse the JSON response
    DynamicJsonDocument jsonResponse(200);
    deserializeJson(jsonResponse, http.getString()); // Extract the JSON response

    // Extract the server time from the response
    long long serverReceiveTime = jsonResponse["serverReceiveTime"];
    long long serverSendTime = jsonResponse["serverSendTime"];

    // Compute the current time
    long long deviceRecTime = millis();
    long long currentTime = (serverReceiveTime + serverSendTime + deviceRecTime - deviceSendTime) / 2;
    long long currentTimeSeconds = currentTime / 1000;

    // Set device time
    setTime(currentTimeSeconds);
  }
}

// Function to submit data to Anedya server
// For more info, visit [https://docs.anedya.io/devicehttpapi/submitdata/]
void anedya_submitData(String datapoint, float sensor_data)
{
  if (WiFi.status() == WL_CONNECTED)
  {                          // Check if the device is connected to WiFi
    WiFiClientSecure client; // Initialize a secure WiFi client
    HTTPClient http;         // Initialize an HTTP client
    client.setInsecure();    // Configure the client to accept insecure connections

    // Construct the URL for submitting data to Anedya server
    String senddata_url = "https://device." + regionCode + ".anedya.io/v1/submitData";

    // Get current time and convert it to milliseconds
    long long current_time = now();                     // Get the current time from the device
    long long current_time_milli = current_time * 1000; // Convert current time to milliseconds

    // Prepare data payload in JSON format
    http.begin(client, senddata_url);                   // Initialize the HTTP client with the Anedya server URL
    http.addHeader("Content-Type", "application/json"); // Set the content type of the request as JSON
    http.addHeader("Accept", "application/json");       // Specify the accepted content type
    http.addHeader("Auth-mode", "key");                 // Set authentication mode
    http.addHeader("Authorization", connectionkey);     // Add the connection key for authorization

    // Construct the JSON payload with sensor data and timestamp
    String jsonStr = "{\"data\":[{\"variable\": \"" + datapoint + "\",\"value\":" + String(sensor_data) + ",\"timestamp\":" + String(current_time_milli) + "}]}";
    // Serial.println(jsonStr);
    // Send the POST request with the JSON payload to Anedya server
    int httpResponseCode = http.POST(jsonStr);

    // Check if the request was successful
    if (httpResponseCode > 0)
    {                                     // Successful response
      String response = http.getString();
      //Serial.println(httpResponseCode); // Get the response from the server
      // Parse the JSON response
      DynamicJsonDocument jsonSubmit_response(200);
      deserializeJson(jsonSubmit_response, response); // Extract the JSON response
                                                      // Extract the server time from the response
      int errorcode = jsonSubmit_response["errorcode"];
      if (errorcode == 0)
      { // error code  0 means data submitted successfull
        Serial.println("Data pushed to Anedya Cloud!");
      }
      else
      { // other errocode means failed to push (like: 4020- mismatch variable identifier...)
        Serial.println("Failed to push!!");
        Serial.println(response); // Print the response
      }
    }
    else
    { // Error handling for failed request
      Serial.print("Error on sending POST: ");
      Serial.println(httpResponseCode); // Print the HTTP response code
    }
    http.end(); // End the HTTP client session
  }
  else
  { // Error handling for WiFi connection failure
    Serial.println("Error in WiFi connection");
  }
}
