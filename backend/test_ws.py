import asyncio
import websockets
import json
import httpx
import base64

API_BASE = "http://localhost:8000/api/v1"
WS_BASE = "ws://localhost:8000/api/v1"
DEVICE_UID = "TEST_ESP32_001"

async def test_live_websocket():
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
            print("\n📝 3. Injecting 'Story Mode' context into DB...")
            from app.db.session import SessionLocal
            from app.models.db_models import Session, Device
            from app.models.enums import AppMode, ObjectCategory
            
            db = SessionLocal()
            device = db.query(Device).filter(Device.device_uid == DEVICE_UID).first()
            if device:
                active_sess = db.query(Session).filter(Session.device_id == device.id).order_by(Session.id.desc()).first()
                if active_sess:
                    active_sess.active_mode = AppMode.story
                    active_sess.current_object_name = "Happy Little Penguin"
                    active_sess.current_object_category = ObjectCategory.animals
                    db.commit()
                    print(f"✅ Set Context -> Mode: {active_sess.active_mode.value}, Object: {active_sess.current_object_name}")
            db.close()

            # Now send some fake text over to trigger the LLM to 'look' at the context we set
            print("\n🗣️ 4. Sending mock text query to Vertex AI...")
            
            await websocket.send(json.dumps({
                "type": "activity_start",
                "payload": None
            }))
            
            await websocket.send(json.dumps({
                "type": "text_message",
                "payload": {"text": "What is this?"}
            }))
            
            await websocket.send(json.dumps({
                "type": "activity_end",
                "payload": None
            }))
            
            # Wait for response (transcript or audio)
            print("\n⏳ 5. Waiting for Google Vertex AI response (Story Mode)...")
            audio_data = bytearray()
            
            while True:
                res = await websocket.recv()
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
    asyncio.run(test_live_websocket())
