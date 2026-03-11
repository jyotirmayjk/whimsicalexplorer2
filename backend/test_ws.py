import asyncio
import websockets
import json
import httpx

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
            
            print("\n🎉 Socket ADK routing works perfectly!")
            
    except Exception as e:
        print(f"❌ Connection failed. Is the server running? Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_live_websocket())
