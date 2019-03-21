import requests
import json
import settings


class ApiService:
    def get_endpoint_data(self, endpoint):
        try:
            url = 'http://{}/{}/'.format(settings.BACKEND_URL, endpoint)
            response = requests.get(url=url,
                                    headers={'Access-Token': settings.BACKEND_ACCESS_TOKEN,
                                             'Content-Type': 'application/json'})
        except (requests.ConnectionError,):
            # TU ZROBIC JAKIS HANDLING JESLI NIE DZIALA SERWER ELO
            return {}

        try:
            return response.json()
        except:
            return {}

    def send_endpoint_data(self, endpoint, data):
        try:
            url = 'http://{}/{}/'.format(settings.BACKEND_URL, endpoint)
            response = requests.post(url=url,
                                     data=json.dumps(data),
                                     headers={'Access-Token': settings.BACKEND_ACCESS_TOKEN,
                                              'Content-Type': 'application/json'})
        except (requests.ConnectionError,):
            return False, {}

        try:
            return response.status_code, response.json()
        except:
            return response.status_code, {}

    def delete_endpoint_data(self, endpoint, data):
        try:
            url = 'http://{}/{}/'.format(settings.BACKEND_URL, endpoint)
            response = requests.delete(url=url,
                                       data=json.dumps(data),
                                       headers={'Access-Token': settings.BACKEND_ACCESS_TOKEN,
                                                'Content-Type': 'application/json'})
        except (requests.ConnectionError,):
            return False, {}

        try:
            return response.status_code, response.json()
        except:
            return response.status_code, {}

    def update_endpoint_data(self, endpoint, data):
        try:
            url = 'http://{}/{}/'.format(settings.BACKEND_URL, endpoint)
            response = requests.patch(url=url,
                                      data=json.dumps(data),
                                      headers={'Access-Token': settings.BACKEND_ACCESS_TOKEN,
                                               'Content-Type': 'application/json'})
        except (requests.ConnectionError,):
            return False, {}

        try:
            return response.status_code, response.json()
        except:
            return response.status_code, {}
