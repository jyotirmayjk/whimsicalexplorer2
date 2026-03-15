#include <Arduino.h>
#include <WiFi.h>
#include <WebSocketsClient.h>
#include <ArduinoJson.h>
#include <HTTPClient.h>
#include <base64.h>
#include "camera_config.h"
#include "audio_config.h"

// ---------------------------------------------------------------- //
// Configuration - Update these for your local environment
// ---------------------------------------------------------------- //
const char* ssid = "YOUR_WIFI_SSID";         // <--- CHANGE ME
const char* password = "YOUR_WIFI_PASSWORD"; // <--- CHANGE ME

// Replace with your local machine's IP address where FastAPI is running
// Run 'ifconfig' (Mac/Linux) or 'ipconfig' (Windows) to find it
const char* host_ip = "192.168.1.100";      // <--- CHANGE ME
const int port = 8000;
const char* device_uid = "ESP32_TOY_001";

// Constructed URLs
String ws_url = String("/api/v1/device/live?device_uid=") + device_uid;
String upload_url = String("http://") + host_ip + ":" + port + "/api/v1/device/media/image";

WebSocketsClient webSocket;

// Hardware State
const int BUTTON_PIN = 42; // GPIO for pushbutton (switches to GND)
bool is_recording = false;
bool was_button_pressed = false;

// ---------------------------------------------------------------- //
// API Image Upload Function
// ---------------------------------------------------------------- //
void captureAndUploadImage() {
    Serial.println("[CAM] Capturing image...");
    camera_fb_t * fb = esp_camera_fb_get();
    if (!fb) {
        Serial.println("[CAM] Camera capture failed");
        return;
    }

    Serial.println("[HTTP] Uploading image to backend...");
    HTTPClient http;
    http.begin(upload_url);
    
    // We mock generic multipart upload headers for the FastAPI endpoint
    String boundary = "Esp32MultipartBoundary";
    http.addHeader("Content-Type", "multipart/form-data; boundary=" + boundary);
    
    // Build multipart body
    String head = "--" + boundary + "\r\n";
    head += "Content-Disposition: form-data; name=\"session_id\"\r\n\r\n";
    head += "1\r\n"; // Mock active session ID
    head += "--" + boundary + "\r\n";
    head += "Content-Disposition: form-data; name=\"file\"; filename=\"capture.jpg\"\r\n";
    head += "Content-Type: image/jpeg\r\n\r\n";
    String tail = "\r\n--" + boundary + "--\r\n";
    
    // Allocate full buffer for multipart request
    size_t total_len = head.length() + fb->len + tail.length();
    uint8_t * body = (uint8_t *)malloc(total_len);
    if (body) {
        memcpy(body, head.c_str(), head.length());
        memcpy(body + head.length(), fb->buf, fb->len);
        memcpy(body + head.length() + fb->len, tail.c_str(), tail.length());
        
        // Send single buffer
        int httpResponseCode = http.sendRequest("POST", body, total_len);
                                
        if (httpResponseCode > 0) {
            Serial.printf("[HTTP] Upload successful, code: %d\n", httpResponseCode);
        } else {
            Serial.printf("[HTTP] Upload failed, error: %s\n", http.errorToString(httpResponseCode).c_str());
        }
        free(body);
    } else {
        Serial.println("[HTTP] Failed to allocate memory for image upload.");
    }
    
    http.end();
    esp_camera_fb_return(fb); // Clear memory buffer
}

// ---------------------------------------------------------------- //
// Audio Capture & Stream (50-100ms chunks)
// ---------------------------------------------------------------- //
void streamAudioChunk() {
    const size_t bytesPerChunk = 2048; // ~64ms of 16k 16-bit audio
    uint8_t micBuffer[bytesPerChunk];
    size_t bytesRead = 0;

    esp_err_t result = i2s_read(I2S_PORT_RX, &micBuffer, bytesPerChunk, &bytesRead, portMAX_DELAY);
    if (result == ESP_OK && bytesRead > 0) {
        // Build Base64 encoded payload per ADK constraint
        String base64Audio = base64::encode(micBuffer, bytesRead);

        DynamicJsonDocument doc(4096);
        doc["type"] = "audio_chunk";
        doc["payload"]["data_base64"] = base64Audio;
        
        String output;
        serializeJson(doc, output);
        webSocket.sendTXT(output);
    }
}

// ---------------------------------------------------------------- //
// WebSocket Event Handler
// ---------------------------------------------------------------- //
void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
    if (type == WStype_CONNECTED) {
        Serial.println("[WS] Connected!");
        StaticJsonDocument<200> doc;
        doc["type"] = "session_start";
        doc["payload"] = nullptr;
        String output;
        serializeJson(doc, output);
        webSocket.sendTXT(output);
    } 
    else if (type == WStype_TEXT) {
        DynamicJsonDocument doc(8192); // Generous for base64 packets
        DeserializationError error = deserializeJson(doc, payload);
        if (!error) {
            const char* eventType = doc["type"];
            
            if (strcmp(eventType, "audio_out") == 0) {
                // Intercept Server AI Audio and Play through Speaker
                const char* b64Audio = doc["payload"]["data_base64"];
                if (b64Audio) {
                     String encodedAudio = String(b64Audio);
                     int decodedLen = base64::decodedLength(encodedAudio.c_str(), encodedAudio.length());
                     uint8_t* pcmBuffer = (uint8_t*) malloc(decodedLen);
                     
                     if (pcmBuffer != NULL) {
                         base64::decode(encodedAudio.c_str(), pcmBuffer);
                         
                         size_t bytesWritten;
                         i2s_write(I2S_PORT_TX, pcmBuffer, decodedLen, &bytesWritten, portMAX_DELAY);
                         free(pcmBuffer);
                     }
                }
            } 
            else if (strcmp(eventType, "interrupted") == 0) {
                Serial.println("[ADK] Server acknowledged Interruption. Instantly clearing speaker buffers!");
                i2s_zero_dma_buffer(I2S_PORT_TX);
            }
        }
    }
}

// ---------------------------------------------------------------- //
// Arduino Setup & Loop
// ---------------------------------------------------------------- //
void setup() {
    Serial.begin(115200);
    pinMode(BUTTON_PIN, INPUT_PULLUP);
    delay(1000);

    Serial.println("\n--- Kids Pokédex ESP32 Booting ---");

    bool camera_ok = initCamera();
    bool audio_ok = initAudio();

    if (!camera_ok) {
        Serial.println("[BOOT] Camera init failed. Check XCLK/HREF and camera ribbon orientation.");
    }
    if (!audio_ok) {
        Serial.println("[BOOT] Audio init failed. Check mic/speaker wiring.");
    }

    // Connect to WiFi
    WiFi.begin(ssid, password);
    Serial.print("Connecting to WiFi.");
    while (WiFi.status() != WL_CONNECTED) { delay(500); }
    Serial.println("\nWiFi connected.");

    // Setup ADK WebSocket Connection
    webSocket.begin(host_ip, port, ws_url);
    webSocket.onEvent(webSocketEvent);
    webSocket.setReconnectInterval(5000); 
}

void loop() {
    webSocket.loop();
    
    // Hold physical button to "Scan and Speak"
    bool current_button_state = (digitalRead(BUTTON_PIN) == LOW);
    
    if (current_button_state && !was_button_pressed) {
        // Just Pressed: Interrupt Server + Upload Image Context
        Serial.println("[BTN] Pressed! Sending interrupt and activity_start.");
        
        StaticJsonDocument<200> interrupt_doc; interrupt_doc["type"] = "interrupt";
        String wsInterrupt; serializeJson(interrupt_doc, wsInterrupt);
        webSocket.sendTXT(wsInterrupt);

        StaticJsonDocument<200> activity_doc; activity_doc["type"] = "activity_start";
        String wsActivity; serializeJson(activity_doc, wsActivity);
        webSocket.sendTXT(wsActivity);
        
        i2s_zero_dma_buffer(I2S_PORT_TX); // Local ducking
        captureAndUploadImage();
        
        is_recording = true;
        was_button_pressed = true;
        
    } else if (current_button_state && was_button_pressed) {
        // Held Down: Continuously stream microphone chunks ~64ms each
        if (is_recording && webSocket.isConnected()) {
             streamAudioChunk();
        }
        
    } else if (!current_button_state && was_button_pressed) {
        // Just Released: End turn
        Serial.println("[BTN] Released! Sending activity_end.");
        
        StaticJsonDocument<200> activity_doc; activity_doc["type"] = "activity_end";
        String wsActivity; serializeJson(activity_doc, wsActivity);
        webSocket.sendTXT(wsActivity);

        is_recording = false;
        was_button_pressed = false;
    }
}
