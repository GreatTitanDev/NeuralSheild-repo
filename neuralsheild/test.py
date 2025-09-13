import requests

class NeuralShieldClient:
    def __init__(self, api_key):
        self.api_key = "KFCriyDqP7xGex1mpZ904e1YT1wqSXY59MB7aUSSTLg"
        self.base_url = "http://localhost:5000/api"
        
    def detect_spam(self, text, platform="email"):
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": self.api_key
        }
        data = {
            "text": text,
            "platform": platform
        }
        response = requests.post(f"{self.base_url}/detect", 
                               json=data, headers=headers)
        return response.json()
        
# Usage
client = NeuralShieldClient("your_api_key_here")
result = client.detect_spam("Win a free iPhone!")
print(result)