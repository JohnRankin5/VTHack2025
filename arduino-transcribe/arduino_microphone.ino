/*
 * Arduino Microphone Recording for Firefighter Helmet
 * Records audio from microphone and saves as WAV file
 * Compatible with ESP32 or Arduino with SD card module
 * 
 * Hardware Requirements:
 * - ESP32 or Arduino with SD card module
 * - Microphone (I2S or analog)
 * - SD card
 * 
 * For testing: Use ESP32 with I2S microphone
 */

#include <SD.h>
#include <SPI.h>
#include <WiFi.h>  // For ESP32, use #include <WiFi.h>
// For Arduino Uno with Ethernet shield, use:
// #include <Ethernet.h>

// Pin definitions for ESP32
#define I2S_WS 25
#define I2S_SD 33
#define I2S_SCK 32
#define SD_CS 5

// Audio settings
#define SAMPLE_RATE 16000
#define BITS_PER_SAMPLE 16
#define CHANNELS 1
#define RECORD_TIME 5000  // Record for 5 seconds

// I2S configuration
#define I2S_PORT I2S_NUM_0

// Buffer for audio data
int16_t audioBuffer[1024];
int bufferIndex = 0;

// File for recording
File audioFile;

void setup() {
  Serial.begin(115200);
  Serial.println("Firefighter Helmet Microphone Test");
  
  // Initialize SD card
  if (!SD.begin(SD_CS)) {
    Serial.println("SD Card initialization failed!");
    return;
  }
  Serial.println("SD Card initialized successfully");
  
  // Initialize I2S
  i2s_config_t i2s_config = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
    .sample_rate = SAMPLE_RATE,
    .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
    .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
    .communication_format = I2S_COMM_FORMAT_STAND_I2S,
    .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
    .dma_buf_count = 8,
    .dma_buf_len = 1024,
    .use_apll = false,
    .tx_desc_auto_clear = false,
    .fixed_mclk = 0
  };
  
  i2s_pin_config_t pin_config = {
    .bck_io_num = I2S_SCK,
    .ws_io_num = I2S_WS,
    .data_out_num = I2S_PIN_NO_CHANGE,
    .data_in_num = I2S_SD
  };
  
  i2s_driver_install(I2S_PORT, &i2s_config, 0, NULL);
  i2s_set_pin(I2S_PORT, &pin_config);
  
  Serial.println("I2S initialized");
  Serial.println("Ready to record audio!");
  Serial.println("Send 'r' to start recording, 's' to stop");
}

void loop() {
  if (Serial.available()) {
    char command = Serial.read();
    
    if (command == 'r') {
      startRecording();
    } else if (command == 's') {
      stopRecording();
    } else if (command == 't') {
      testMicrophone();
    }
  }
}

void startRecording() {
  Serial.println("Starting recording...");
  
  // Create filename with timestamp
  String filename = "/audio_" + String(millis()) + ".wav";
  
  // Open file for writing
  audioFile = SD.open(filename, FILE_WRITE);
  if (!audioFile) {
    Serial.println("Error opening file for writing");
    return;
  }
  
  // Write WAV header
  writeWavHeader(audioFile, RECORD_TIME * SAMPLE_RATE * CHANNELS * 2);
  
  Serial.println("Recording... Speak now!");
  Serial.println("Recording will stop automatically in " + String(RECORD_TIME/1000) + " seconds");
  
  // Record audio
  unsigned long startTime = millis();
  size_t bytesRead;
  
  while (millis() - startTime < RECORD_TIME) {
    i2s_read(I2S_PORT, audioBuffer, sizeof(audioBuffer), &bytesRead, portMAX_DELAY);
    
    if (bytesRead > 0) {
      audioFile.write((uint8_t*)audioBuffer, bytesRead);
    }
    
    // Show progress
    if ((millis() - startTime) % 1000 < 100) {
      Serial.print(".");
    }
  }
  
  audioFile.close();
  Serial.println("\nRecording completed!");
  Serial.println("File saved as: " + filename);
  Serial.println("File size: " + String(audioFile.size()) + " bytes");
}

void stopRecording() {
  if (audioFile) {
    audioFile.close();
    Serial.println("Recording stopped manually");
  }
}

void testMicrophone() {
  Serial.println("Testing microphone...");
  
  size_t bytesRead;
  int16_t testBuffer[256];
  
  for (int i = 0; i < 10; i++) {
    i2s_read(I2S_PORT, testBuffer, sizeof(testBuffer), &bytesRead, portMAX_DELAY);
    
    if (bytesRead > 0) {
      // Calculate RMS for volume indication
      long sum = 0;
      for (int j = 0; j < bytesRead / 2; j++) {
        sum += testBuffer[j] * testBuffer[j];
      }
      int rms = sqrt(sum / (bytesRead / 2));
      
      Serial.println("Sample " + String(i) + ": RMS = " + String(rms));
    }
    
    delay(100);
  }
  
  Serial.println("Microphone test completed");
}

void writeWavHeader(File file, uint32_t dataSize) {
  // WAV header structure
  uint8_t header[44];
  
  // RIFF header
  header[0] = 'R'; header[1] = 'I'; header[2] = 'F'; header[3] = 'F';
  uint32_t fileSize = dataSize + 36;
  header[4] = fileSize & 0xFF;
  header[5] = (fileSize >> 8) & 0xFF;
  header[6] = (fileSize >> 16) & 0xFF;
  header[7] = (fileSize >> 24) & 0xFF;
  
  // WAVE format
  header[8] = 'W'; header[9] = 'A'; header[10] = 'V'; header[11] = 'E';
  
  // fmt chunk
  header[12] = 'f'; header[13] = 'm'; header[14] = 't'; header[15] = ' ';
  header[16] = 16; header[17] = 0; header[18] = 0; header[19] = 0; // fmt chunk size
  header[20] = 1; header[21] = 0; // audio format (PCM)
  header[22] = CHANNELS; header[23] = 0; // number of channels
  header[24] = SAMPLE_RATE & 0xFF;
  header[25] = (SAMPLE_RATE >> 8) & 0xFF;
  header[26] = (SAMPLE_RATE >> 16) & 0xFF;
  header[27] = (SAMPLE_RATE >> 24) & 0xFF;
  
  uint32_t byteRate = SAMPLE_RATE * CHANNELS * BITS_PER_SAMPLE / 8;
  header[28] = byteRate & 0xFF;
  header[29] = (byteRate >> 8) & 0xFF;
  header[30] = (byteRate >> 16) & 0xFF;
  header[31] = (byteRate >> 24) & 0xFF;
  
  header[32] = CHANNELS * BITS_PER_SAMPLE / 8; // block align
  header[33] = 0;
  header[34] = BITS_PER_SAMPLE; // bits per sample
  header[35] = 0;
  
  // data chunk
  header[36] = 'd'; header[37] = 'a'; header[38] = 't'; header[39] = 'a';
  header[40] = dataSize & 0xFF;
  header[41] = (dataSize >> 8) & 0xFF;
  header[42] = (dataSize >> 16) & 0xFF;
  header[43] = (dataSize >> 24) & 0xFF;
  
  file.write(header, 44);
}
