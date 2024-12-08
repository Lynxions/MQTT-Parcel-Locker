#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <Ticker.h>
#include "secrets.h"
#include "ESP8266httpUpdate.h"
#include <time.h>  // For time synchronization

const char* ssid = WIFI_SSID;
const char* password = WIFI_PASSWORD;
const char* mqtt_server = MQTT_SERVER;
const char* firmware_url = FIRMWARE_URL;

#define ledPin 2

Ticker lockOffTickers[4];

// Initializes the espClient
WiFiClient httpClient;
PubSubClient client(httpClient);

const int lockPins[4] = {5, 0, 14, 13}; // ESP32 pins GPIO5 (D1), GPIO0 (D3), GPIO14 (D5), GPIO13 (D7)
const char* lockTopics[4] = {"rpi/locker1", "rpi/locker2", "rpi/locker3", "rpi/locker4"};

bool lockStates[4] = {false, false, false, false};
bool controlLocks[4] = {false, false, false, false};
unsigned long lockOnTimes[4] = {0, 0, 0, 0};

const long interval = OPEN_INTERVAL; // interval of 5s

String commandTopic;
String firmwareTopic = "lockers/firmware";
const char* aliveTopic = "lockers/alive";

void blink_led(unsigned int times, unsigned int duration){
    for (unsigned int i = 0; i < times; i++) {
        digitalWrite(ledPin, HIGH);
        delay(duration);
        digitalWrite(ledPin, LOW); 
        delay(200);
    }
}

void setup_wifi(){
    delay(50);
    Serial.println();
    Serial.print("Connecting to ");
    Serial.println(ssid);
    WiFi.begin(ssid, password);   

    int c=0;
    while(WiFi.status() != WL_CONNECTED){
        blink_led(2, 200); //blink LED twice (for 200ms ON time) to indicate that wifi not connected
        delay(100);
        Serial.print(".");
        c=c+1;
        if(c>50){
            ESP.restart(); //restart ESP after 10 seconds
        }        
    }

    Serial.println("");
    Serial.println("WiFi connected");
    Serial.println("IP address: ");
    Serial.println(WiFi.localIP());
}

void connect_mqttServer(){
    while (!client.connected()) {
        Serial.print("Connecting to MQTT broker at ");
        Serial.print(mqtt_server);
        Serial.print(":");
        Serial.println(MQTT_PORT);

        srand(time(0));  // Seed the random number generator
        int randomId = rand();
        String clientId = "locker-" + String(randomId);

        // Define Last Will and Testament
        const char* willMessage = "0";
        int willQoS = 1;
        bool willRetain = true;

        // Attempt to connect with LWT
        if (client.connect(clientId.c_str(), NULL, NULL, aliveTopic, willQoS, willRetain, willMessage)) {
            Serial.println("Connected to MQTT broker");

            // Publish alive message upon connection
            client.publish(aliveTopic, "1", true);
            Serial.print("Published to: ");
            Serial.println(aliveTopic);

            // Subscribe to necessary topics
            client.subscribe(commandTopic.c_str());
            client.subscribe(firmwareTopic.c_str());
            for (int i = 0; i < 4; i++) {
              client.subscribe(lockTopics[i]);
            };
        } else {
            Serial.print("Failed to connect to MQTT, rc=");
            Serial.print(client.state());
            Serial.println(". Trying again in 5 seconds...");
            delay(5000);
        }
    }
}

void handleLock(int lockIndex, bool turnOn) {
    if (turnOn) {
        digitalWrite(lockPins[lockIndex], HIGH);
        lockStates[lockIndex] = true;
        lockOnTimes[lockIndex] = millis();
        Serial.print("Lock ");
        Serial.print(lockIndex + 1);
        Serial.println(" is open");
        controlLocks[lockIndex] = true;
    } else {
        digitalWrite(lockPins[lockIndex], LOW);
        lockStates[lockIndex] = false;
        Serial.print("Lock ");
        Serial.print(lockIndex + 1);
        Serial.println(" is closed");
        controlLocks[lockIndex] = false;
    }
}

// Add OTA update function
void performOTA() {
    Serial.println("Starting OTA update...");
    Serial.print("Firmware URL: ");
    Serial.println(FIRMWARE_URL);

    // Use WiFiClient for HTTP
    WiFiClientSecure client;
    client.setInsecure(); // Use this only for testing purposes, for production use proper certificate validation

    // Perform OTA update
    t_httpUpdate_return ret = ESPhttpUpdate.update(client, FIRMWARE_URL);

    switch (ret) {
        case HTTP_UPDATE_FAILED:
            Serial.printf("OTA Update Failed. Error (%d): %s\n", ESPhttpUpdate.getLastError(), ESPhttpUpdate.getLastErrorString().c_str());
            break;
        case HTTP_UPDATE_NO_UPDATES:
            Serial.println("No OTA Update Available.");
            break;
        case HTTP_UPDATE_OK:
            Serial.println("OTA Update Successful.");
            break;
    }
}

//this function will be executed whenever there is data available on subscribed topics
void callback(char* topic, byte* message, unsigned int length) {
    Serial.print("Message arrived on topic: ");
    Serial.print(topic);
    Serial.print(". Message: ");
    String messageTemp;
    
    for (unsigned int i = 0; i < length; i++) {
        messageTemp += (char)message[i];
    }

    for (int i = 0; i < 4; i++) {
        if (String(topic) == lockTopics[i]) {
            if (messageTemp == String("{\"cell\":\"on\"}") && !lockStates[i]) {
                handleLock(i, true);
            }
            if (messageTemp == String("{\"cell\":\"off\"}")) {
                handleLock(i, false);
            }
        }
    }

    // Handle firmware update command
    if (String(topic) == firmwareTopic) {
        Serial.println("Firmware update command received.");
        performOTA();
    }
}

void setup(){
    Serial.begin(115200);
        
    for (int i = 0; i < 4; i++) {
        pinMode(lockPins[i], OUTPUT);
    }

    setup_wifi();
    configTime(25200, 0, "pool.ntp.org", "time.nist.gov"); // Initialize time synchronization

    client.setServer(mqtt_server, MQTT_PORT); //1883 is the default port for MQTT server
    client.setCallback(callback);  

    // Get MAC address
    String macAddress = WiFi.macAddress();
    macAddress.replace(":", ""); // Remove colons for topic
    commandTopic = "locker/" + macAddress + "/command";
}

void publishLockOff(int lockIndex) {
    client.publish(lockTopics[lockIndex], "off", 0);
}

void topicPublishOn() {
    for (int i = 0; i < 4; i++) {
        if (controlLocks[i]) {
            client.publish(lockTopics[i], "on" , 0);
            controlLocks[i] = false;
            lockOffTickers[i].once(interval/1000, std::bind(publishLockOff, i));
        }
    }
}

void loop(){
    if (!client.connected()){
        connect_mqttServer();
    }
    client.loop();

    // Update time
    time_t now;
    time(&now);

    //function to publish
    unsigned long currentMillis = millis();
    for (int i = 0; i < 4; i++) {
        if (lockStates[i] && currentMillis - lockOnTimes[i] >= interval) {
            digitalWrite(lockPins[i], LOW);
            lockStates[i] = false;
            Serial.print("Lock ");
            Serial.print(i + 1);
            Serial.println(" is closed after 5 seconds");
        }
    }

    topicPublishOn();
}