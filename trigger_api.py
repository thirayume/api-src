import sys
import requests
import json


def get_token():
    url = "http://localhost:8000/token"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    data = {
        "grant_type": "password",
        "username": "johndoe",
        "password": "secret",
        "scope": "",
        "client_id": "",
        "client_secret": "",
    }

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data["access_token"]
        return access_token
    else:
        raise Exception(f"Failed to get token: {response.status_code}, {response.text}")

# C:\Python311\python.exe C:\ws-api\trigger_api.py 
operation = sys.argv[1]
url = sys.argv[2]

print(operation)
print(url)

try:
    data = sys.argv[3]
    data = data.replace("{", "").replace("}", "")
    data = data.replace("\"", "")

    # แบ่งข้อมูลเป็น list ของ dictionaries
    data_list = data.split("},")

    # สร้าง list ของ dictionaries ที่ถูกต้อง
    corrected_data = []
    for item in data_list:
        item = item.strip()  # ลบช่องว่าง
        pairs = item.split(",")
        obj = {}
        for pair in pairs:
            key, value = pair.split(":")
            if key.endswith("ID"):
                obj[key.strip()] = value.strip()
            else:
                obj[key.strip()] = value.strip()
        corrected_data.append(obj)

    # แปลงเป็น JSON
    json_data = json.dumps(corrected_data, ensure_ascii=False, indent=4)
    json_data = json_data.replace("[", "").replace("]", "")
except Exception as error:
    print("An exception occurred:", error)
    print("No data provided")
    pass


# Get the token
token = get_token()
# Use the token in your other script or application
# print(token)

headers = {
    "accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": "Bearer " + token,
}

# Set the timeout value in seconds
timeout_value = 5

try:
    print(json_data)
    match operation:
        case "I":
            response = requests.post(url, data=json_data, headers=headers, timeout=timeout_value)
        case "U":
            response = requests.put(url, data=json_data, headers=headers, timeout=timeout_value)
        case "D":
            response = requests.delete(url, data=json_data, headers=headers, timeout=timeout_value)
        case _:
            print("Operation not supported")

except NameError as e:
    print("No data need")
    match operation:
        case "I":
            response = requests.post(url, headers=headers, timeout=timeout_value)
        case "U":
            response = requests.put(url, headers=headers, timeout=timeout_value)
        case "D":
            response = requests.delete(url, headers=headers, timeout=timeout_value)
        case _:
            print("Operation not supported")

print(response.status_code)
if response.status_code == 200:
    print(f"Successful: {response.status_code}, {response.text}")
elif response.status_code == 204:
    print(f"Successful: {response.status_code}, {response.text}")
else:
    raise Exception(f"Failed to send data: {response.status_code}, {response.text}")
