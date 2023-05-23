import requests

def request_data(request):

  ACCESS_TOKEN = '82d71c867a8055c56231def294691155f843070e'
  DEVICE_ID = 'e00fce68eb125a9b43546163'
  EVENT_NAME = 'upload_data'

  url = f'https://api.particle.io/v1/devices/events'
  params = {'name': 'upload_data',
            'data': 'upload_data',
            'private': 'true',
            'ttl': '60',
            'access_token': ACCESS_TOKEN
            }

  response = requests.post(url, data=params)
  return (str(response.status_code)) 