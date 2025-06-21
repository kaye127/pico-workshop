import urequests
api_url = 'https://172.20.10.5:3000/data'
from setup import device_name
headers = {"Content-Type": "application/json"}

def send_data(temperature):
    payload = {
        "deviceName": device_name,
        "temperature": temperature
    }
       
    try:
        print("Sending data to API...")
        res = urequests.post(api_url, json=payload, headers=headers)
        print(res)
        if res.status_code != 200:
            print("Error:", res.status_code, res.text)
        else:
            print("Sent:", res.text)
        res.close()  
    except Exception as e:
        print("Error sending data:", e)
