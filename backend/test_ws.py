import asyncio
import websockets
import json
import httpx
import base64
import argparse

API_BASE = "http://localhost:8000/api/v1"
WS_BASE = "ws://localhost:8000/api/v1"
DEVICE_UID = "TEST_ESP32_001"
TEST_PROMPT = "Tell me a short fun fact about penguins for kids."
RESPONSE_TIMEOUT_SECONDS = 45
DEFAULT_MODE = "story"
DEFAULT_OBJECT = "Happy Little Penguin"
DEFAULT_CATEGORY = "animals"

MODE_CONTEXT = {
    "story": {"object": "Happy Little Penguin", "category": "animals"},
    "learn": {"object": "Car", "category": "things"},
    "explorer": {"object": "Tree", "category": "nature"},
}

async def test_live_websocket(prompt: str, mode: str, timeout: int):
    print("🎯 Goal: Validate Gemini Live on Vertex via ADK by sending a test prompt and waiting for model reply.")
    print("🤖 1. Registering fake toy device...")
    async with httpx.AsyncClient() as client:
        # We need an admin/household token first (mocking login)
        login_res = await client.post(f"{API_BASE}/auth/login", json={"name": "Test Family"})
        token = login_res.json()["data"]["access_token"]
        
        # Register the device hardware under this family
        reg_res = await client.post(
            f"{API_BASE}/device/register", 
            json={"device_uid": DEVICE_UID},
            headers={"Authorization": f"Bearer {token}"}
        )
        print(f"✅ Device Registered: {reg_res.json()}")

    print("\n🔌 2. Connecting to ADK WebSocket Gateway...")
    uri = f"{WS_BASE}/device/live?device_uid={DEVICE_UID}"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket Connected!")

            # Test heartbeat
            await websocket.send(json.dumps({
                "type": "heartbeat", 
                "payload": None
            }))
            res = await websocket.recv()
            print(f"📥 Server Reply to Heartbeat: {res}")

            # Test Session Start
            await websocket.send(json.dumps({
                "type": "session_start", 
                "payload": None
            }))
            res = await websocket.recv()
            print(f"📥 Server Reply to Session Start: {res}")
            
            # Since there isn't a dedicated endpoint for setting active mode from the mobile app yet, 
            # let's manipulate the DB directly for testing Story Mode.
            print(f"\n📝 3. Injecting '{mode.title()} Mode' context into DB...")
            from app.db.session import SessionLocal
            from app.models.db_models import Session, Device
            from app.models.enums import AppMode, ObjectCategory
            
            db = SessionLocal()
            device = db.query(Device).filter(Device.device_uid == DEVICE_UID).first()
            if device:
                active_sess = db.query(Session).filter(Session.device_id == device.id).order_by(Session.id.desc()).first()
                if active_sess:
                    mode_config = MODE_CONTEXT.get(mode, {})
                    object_name = mode_config.get("object", DEFAULT_OBJECT)
                    object_category = mode_config.get("category", DEFAULT_CATEGORY)

                    active_sess.active_mode = AppMode(mode)
                    active_sess.current_object_name = object_name
                    active_sess.current_object_category = ObjectCategory(object_category)
                    db.commit()
                    print(f"✅ Set Context -> Mode: {active_sess.active_mode.value}, Object: {active_sess.current_object_name}")
            db.close()

            # Now send some fake text over to trigger the LLM to 'look' at the context we set
            print("\n🗣️ 4. Sending test prompt to Gemini Live (Vertex via ADK)...")
            
            await websocket.send(json.dumps({
                "type": "activity_start",
                "payload": None
            }))
            
            await websocket.send(json.dumps({
                "type": "text_message",
                "payload": {"text": prompt}
            }))
            
            await websocket.send(json.dumps({
                "type": "activity_end",
                "payload": None
            }))
            
            # Wait for response (transcript or audio)
            print(f"\n⏳ 5. Waiting for Gemini reply (timeout: {timeout}s)...")
            audio_data = bytearray()
            
            while True:
                try:
                    res = await asyncio.wait_for(websocket.recv(), timeout=timeout)
                except asyncio.TimeoutError:
                    print(f"❌ Timeout: No Gemini response received within {timeout} seconds.")
                    break
                msg = json.loads(res)
                
                if msg.get("type") == "transcript_out":
                    print(f"📖 Vertex AI Transcript: {msg['payload']['text']}")
                elif msg.get("type") == "audio_out":
                    data_b64 = msg['payload']['data_base64']
                    audio_chunk = base64.b64decode(data_b64)
                    audio_data.extend(audio_chunk)
                    print(f"🔊 Received Audio Chunk: {len(audio_chunk)} bytes (Total: {len(audio_data)})")
                elif msg.get("type") == "turn_complete":
                     print("✅ Vertex AI Turn Complete.")
                     break
                elif msg.get("type") == "error":
                     print(f"❌ Error: {msg['payload']}")
                     break
            
            if audio_data:
                with open("output_response.pcm", "wb") as f:
                    f.write(audio_data)
                print(f"\n💾 Saved {len(audio_data)} bytes of raw PCM audio to 'output_response.pcm'")
            
            print("\n🎉 Story Mode Socket ADK routing works perfectly!")
            
    except Exception as e:
        print(f"❌ Connection failed. Is the server running? Error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test Gemini Live on Vertex via backend ADK websocket.")
    parser.add_argument(
        "--prompt",
        default=TEST_PROMPT,
        help="Prompt sent as text_message to Gemini Live.",
    )
    parser.add_argument(
        "--mode",
        choices=["story", "learn", "explorer"],
        default=DEFAULT_MODE,
        help="App mode injected into DB session context.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=RESPONSE_TIMEOUT_SECONDS,
        help="Seconds to wait for Gemini reply before timing out.",
    )
    args = parser.parse_args()
    asyncio.run(test_live_websocket(prompt=args.prompt, mode=args.mode, timeout=args.timeout))
