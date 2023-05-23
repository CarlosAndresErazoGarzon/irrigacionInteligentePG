import requests, json

ACCESS_TOKEN = '82d71c867a8055c56231def294691155f843070e'
DEVICES = ['e00fce68eb125a9b43546163', 'e00fce68c0f65c75fc4aa85b']

def verify_devices(request):
  for device in DEVICES:
    response = post_data(device)

    if response.status_code == 200:
      data = response.json()

      if 'name' in data:
        print(data['name'])
      else:
        print("error")

      break
    else:
      print(response.status_code)

def update_wTime(device, new_wTime):

  url = f'https://api.particle.io/v1/devices/{device}/update_wTime'

  params = {
      'access_token': ACCESS_TOKEN,
      'arg': new_wTime
  }

  response = requests.post(url, data=params)

  return response

def post_data(device):

  response = update_wTime(device, 3000)

  print(response.text)

  url = f'https://api.particle.io/v1/devices/{device}/alive'
  params = {
            'private': 'true',
            'ttl': '60',
            'access_token': ACCESS_TOKEN,
            }

  response = requests.post(url, data=params)
      
  return response

