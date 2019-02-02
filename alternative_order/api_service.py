import requests
import json
import settings



class ApiService:
    def get_endpoint_data(self, _endpoint_string):
        try:
            url = 'http://{}/{}/'.format(settings.BACKEND_URL, _endpoint_string)
            response = requests.get(url=url,
                                    headers={'Access-Token': settings.BACKEND_ACCESS_TOKEN,
                                             'Content-Type': 'application/json'})
        except requests.ConnectionError:
            # TU ZROBIC JAKIS HANDLING JESLI NIE DZIALA SERWER ELO
            return {}

        return response.json()

    def send_endpoint_data(self, _endpoint, _data_dict):
        response = requests.post(url='http://{}/{}/'.format(settings.BACKEND_URL, _endpoint),
                                 data=json.dumps(_data_dict),
                                 headers={'Access-Token': settings.BACKEND_ACCESS_TOKEN,
                                          'Content-Type': 'application/json'})
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, response.json()

    def delete_endpoint_data(self, _endpoint, _data_dict):
        response = requests.delete(url='http://{}/{}/'.format(settings.BACKEND_URL, _endpoint),
                                 data=json.dumps(_data_dict),
                                 headers={'Access-Token': settings.BACKEND_ACCESS_TOKEN,
                                          'Content-Type': 'application/json'})
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, response.json()
