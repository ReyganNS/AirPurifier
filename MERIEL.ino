#include <WiFi.h>
#include <DHT.h>
#include <PubSubClient.h>

const char* ssid = "CLARA";
const char* password = "Clararasmine";
const char* mqtt_server = "broker.hivemq.com";
const int RELAY_PIN = 26;
const int MQ135_PIN = 34;
#define DHT_PIN 25
#define DHTTYPE DHT11
DHT dht(DHT_PIN, DHTTYPE);

WiFiClient espClient;
PubSubClient client(espClient);

void setup_wifi() {
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void sensor() {
  float suhu = dht.readTemperature();
  float kelembaban = dht.readHumidity();
  int udara = analogRead(MQ135_PIN);
  
  if (isnan(suhu) || isnan(kelembaban) || udara == 0) {
    Serial.println("Failed to read sensor data!");
    return;
  }

  char payload[100];
  snprintf(payload, sizeof(payload), "{\"suhu\":%.2f,\"kelembaban\":%.2f,\"udara\":%d}", suhu, kelembaban, udara);

  Serial.print("Sending sensor data: ");
  Serial.println(payload);
  client.publish("kualitas/sensor", payload);
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect("CLARA")) {
      Serial.println("connected");
      client.subscribe("clara/kontrol");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again");
    }
  }
}

void callback(char* topic, byte* message, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  
  String messageStr;
  for (int i = 0; i < length; i++) {
    messageStr += (char)message[i];
  }
  Serial.println(messageStr);
  
  if (strcmp(topic, "clara/kontrol") == 0) {
    if (messageStr.equals("1")) {
      digitalWrite(RELAY_PIN, LOW);
      Serial.println("Relay turned on");
    } else if (messageStr.equals("0")) {
      digitalWrite(RELAY_PIN, HIGH);
      Serial.println("Relay turned off");
    } else if (messageStr.equals("2")) {
      int udara = analogRead(MQ135_PIN);
      if (udara > 1000) {
        digitalWrite(RELAY_PIN, LOW);
        Serial.println("Relay turned on (auto)");
      } else {
        digitalWrite(RELAY_PIN, HIGH);
        Serial.println("Relay turned off (auto)");
      }
    }
  }
}

void setup() {
  Serial.begin(9600);
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, HIGH);

  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
  dht.begin();
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
  sensor();
}
