import traceback
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

payload = {
  "message": "Hello",
  "session_id": "test_123",
  "form_state": {
    "hcp_name": "",
    "interaction_date": "",
    "interaction_type": "",
    "product_discussed": "",
    "materials_left": [],
    "samples_provided": [],
    "key_takeaways": "",
    "follow_up_required": False,
    "follow_up_date": "",
    "follow_up_notes": ""
  }
}

try:
    response = client.post("/api/chat", json=payload)
    print("Status Code:", response.status_code)
    print("Response:", response.text)
except Exception as e:
    print("Exception occurred:")
    traceback.print_exc()
