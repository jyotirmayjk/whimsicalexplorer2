# Kids Pokédex - App Mode Testing Plan

This document outlines the testing strategy for the three main modes of the Kids Pokédex app (Story, Learn, and Explorer), records the progress made so far, and documents current technical issues.

## 📋 Overall Testing Scope

The goal is to verify the end-to-end "Scan and Speak" loop:
1. **Selection**: User selects a mode on the Mobile App.
2. **Context**: Backend receives the mode and object context (e.g., "Story" + "Penguin").
3. **Simulation**: Simulated or real device connects via WebSocket.
4. **Generation**: Vertex AI Live Agent generates a context-aware response using the Gemini Live BIDI stream.
5. **Output**: Device receives streamed audio and displays transcripts.

---

## ⚡ Steps Taken So Far

### 1. Protocol Alignment
- **ServerLiveEvent**: Updated `websockets.py` to wrap all outgoing messages in the `ServerLiveEvent` envelope required by the ESP32 firmware.
- **WebSocket Gateway**: Refined the `live_request_queue` to handle incoming audio and text messages.

### 2. Backend Bug Fixes
- **ADK Session Initialization**: Fixed a critical bug where the ADK `InMemorySessionService` was not creating a session before `runner.run_live()` was called, leading to "Session not found" errors.
- **Database Corruption**: Resolved a Pydantic/SQLAlchemy crash caused by an invalid enum value ("Mythical Creature") injected during early testing.
- **Text-Fallback Support**: Added a `text_message` handler to the live WebSocket so we can trigger the AI turn using text strings instead of needing high-quality PCM audio files during simulation.

### 3. Environment & Credentials
- **Vertex AI Configuration**: Updated `.env` with real Project ID and specified `GOOGLE_GENAI_USE_VERTEXAI=TRUE`.
- **Startup Injection**: Modified `main.py` to force-set Vertex AI environment variables at application startup to ensure the ADK client picks them up.

---

## 🛑 Current Issues & Blockers

### 1. Vertex AI Model Availability (Close Code 1008)
The primary blocker is finding a model that is both **Live API compatible** and **enabled for your project/region**.
- **`gemini-2.0-flash-exp`**: Deprecated or inaccessible.
- **`gemini-2.5-flash-native-audio-preview-...`**: Returns `policy violation (1008)`. This usually means the model is not yet whitelisted for Vertex AI project-auth in your specific region (`us-central1` or `global`).
- **`gemini-2.5-flash`**: Available in the project but returns `not supported in the live api` when used over WebSockets.

### 2. Audio Format Alignment
- The system is configured for **16kHz 16-bit Mono PCM** input. We need to ensure the firmware (ESP32) and the test scripts send exactly this format to avoid "Static" or "Garbled" AI understanding.

---

## 🚀 Future Testing Steps

### Phase 1: Model Verification (Next Immediate Task)
- [ ] Verify if `gemini-2.0-flash-001` succeeds on Vertex AI.
- [ ] If Vertex AI continues to fail, consider temporary use of **Google AI Studio API Key** to verify logic before returning to Vertex.

### Phase 2: Mode Validation
- [ ] **Story Mode**: Inject "Story" mode + "Penguin" -> Verify AI tells a children's story about a penguin.
- [ ] **Learn Mode**: Inject "Learn" mode + "Car" -> Verify AI teaches 3 facts about cars.
- [ ] **Explorer Mode**: Inject "Explorer" mode + "Tree" -> Verify AI asks engaging questions about nature.

### Phase 3: Hardware Integration
- [ ] Connect the ESP32 firmware to the backend.
- [ ] Test real-time VAD (Voice Activity Detection) triggers.
- [ ] Verify audio playback quality on the I2S speaker.
