#ifndef SECRETS_H
#define SECRETS_H

// Wi-Fi Credentials
//#define WIFI_SSID "GoCongDongTienGiang"
//#define WIFI_PASSWORD "P@ssw0rdTui0cho#iBjetDa^u"
//#define WIFI_SSID "International University"
//#define WIFI_PASSWORD ""
//#define WIFI_SSID "realme7i"
//#define WIFI_PASSWORD "12345678"
#define WIFI_SSID "Hảu Hảu"
#define WIFI_PASSWORD "03012006"
//#define WIFI_SSID "Lynxi"
//#define WIFI_PASSWORD "Chissica"
// MQTT Broker Settings
#define MQTT_SERVER "192.168.207.87"
#define MQTT_PORT 80 // Default MQTT port

// MQTT Topics
#define MQTT_ALIVE_TOPIC_PREFIX "unit/"
#define MQTT_ALIVE_TOPIC_SUFFIX "/alive"
#define MQTT_COMMAND_TOPIC_PREFIX "unit/"
#define MQTT_COMMAND_TOPIC_SUFFIX "/command"
#define MQTT_STATUS_TOPIC_PREFIX "unit/"
#define MQTT_STATUS_TOPIC_SUFFIX "/status"
#define MQTT_FIRMWARE_UPDATE_TOPIC "firmware/update"

// Firmware Update URL
#define FIRMWARE_URL "https://api.captechvn.com/api/v1/file/firmware.bin"
#define OPEN_INTERVAL 15000 // 10 seconds
// Status
#define status_interval 10000 // 30 seconds
#endif