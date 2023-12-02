import requests
from secret import USERNAME, PASSWORD

url = "http://127.0.0.1:8000/api/v1/find_profiles"

# Specify the required parameters (username, password, photo file, keywords, chunk_size)
payload = {
    'username': USERNAME,
    'password': PASSWORD,
    'keywords': 'Machine Learning Engineer UFAZ',
    'chunk_size': 50,
    'threshold': 0.4,
}

files = {'photo': ('example.jpg', open('photos/example.jpeg', 'rb'))}

# Send the POST request
response = requests.post(url, data=payload, files=files)

# Print the response
print(response.status_code)
print(response.json())
