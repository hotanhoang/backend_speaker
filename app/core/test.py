import requests
files = {'file1': open('data/negative/00003.wav', "rb"), 'file2': open('data/negative/00003.wav', "rb")}
resp = requests.post('http://localhost:5000/predict', files=files)
print(resp.text)