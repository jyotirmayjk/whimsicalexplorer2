#ifndef AUDIO_CONFIG_H
#define AUDIO_CONFIG_H

#include <Arduino.h>
#include <driver/i2s.h>

// ---------------------------------------------------------------- //
// I2S Audio Pin Mapping (Example: MAX98357A Speaker & INMP441 Mic)
// ---------------------------------------------------------------- //
#define I2S_PORT_RX I2S_NUM_0
#define I2S_PORT_TX I2S_NUM_1

// Microphone Pins (I2S_NUM_0)
#define I2S_MIC_WS  15
#define I2S_MIC_SD  13
#define I2S_MIC_SCK 14

// Speaker Pins (I2S_NUM_1)
#define I2S_SPK_BCLK 27
#define I2S_SPK_LRC  26
#define I2S_SPK_DOUT 25

// Audio settings required by Gemini Live 
#define SAMPLE_RATE 16000
#define BITS_PER_SAMPLE I2S_BITS_PER_SAMPLE_16BIT

bool initAudio() {
    // 1. Configure the Microphone (RX)
    i2s_config_t i2s_config_rx = {
        .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
        .sample_rate = SAMPLE_RATE,
        .bits_per_sample = BITS_PER_SAMPLE,
        .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
        .communication_format = I2S_COMM_FORMAT_STAND_I2S,
        .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
        .dma_buf_count = 4,   // Number of DMA buffers
        .dma_buf_len = 1024,  // Length of each buffer
        .use_apll = false
    };

    i2s_pin_config_t pin_config_rx = {
        .bck_io_num = I2S_MIC_SCK,
        .ws_io_num = I2S_MIC_WS,
        .data_out_num = -1, // Not used
        .data_in_num = I2S_MIC_SD
    };

    if (i2s_driver_install(I2S_PORT_RX, &i2s_config_rx, 0, NULL) != ESP_OK) {
        Serial.println("Error installing I2S RX driver.");
        return false;
    }
    if (i2s_set_pin(I2S_PORT_RX, &pin_config_rx) != ESP_OK) {
        Serial.println("Error setting I2S RX pins.");
        return false;
    }

    // 2. Configure the Speaker (TX)
    i2s_config_t i2s_config_tx = {
        .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_TX),
        .sample_rate = SAMPLE_RATE,
        .bits_per_sample = BITS_PER_SAMPLE,
        .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
        .communication_format = I2S_COMM_FORMAT_STAND_I2S,
        .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
        .dma_buf_count = 4,
        .dma_buf_len = 1024,
        .use_apll = false
    };

    i2s_pin_config_t pin_config_tx = {
        .bck_io_num = I2S_SPK_BCLK,
        .ws_io_num = I2S_SPK_LRC,
        .data_out_num = I2S_SPK_DOUT,
        .data_in_num = -1 // Not used
    };

    if (i2s_driver_install(I2S_PORT_TX, &i2s_config_tx, 0, NULL) != ESP_OK) {
        Serial.println("Error installing I2S TX driver.");
        return false;
    }
    if (i2s_set_pin(I2S_PORT_TX, &pin_config_tx) != ESP_OK) {
        Serial.println("Error setting I2S TX pins.");
        return false;
    }

    Serial.println("I2S Audio interface initialized successfully.");
    return true;
}

#endif
