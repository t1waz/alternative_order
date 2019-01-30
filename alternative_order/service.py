from kivy.app import App
import requests
import settings
from datetime import datetime
import json


class AppService:
    def __init__(self):
        self.current_worker = ''
        self.current_comment = ''
        self.workers = {}
        self.station_name = ''
        self.current_order = {}

    def get_endpoint_data(self, _endpoint_string):
        try:
            response = requests.get(url='http://127.0.0.1:8000/{}/'.format(_endpoint_string),
                                    headers={'Access-Token': settings.BACKEND_ACCESS_TOKEN,
                                             'Content-Type': 'application/json'})
        except requests.ConnectionError:
            # TU ZROBIC JAKIS HANDLING JESLI NIE DZIALA SERWER ELO
            return '0'

        return response.json()

    def send_endpoint_data(self, _endpoint, _data_dict):
        response = requests.post(url='http://127.0.0.1:8000/{}/'.format(_endpoint),
                                 data=json.dumps(_data_dict),
                                 headers={'Access-Token': settings.BACKEND_ACCESS_TOKEN,
                                          'Content-Type': 'application/json'})
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, response.json()

    def get_label_value(self, _label):
        app = App.get_running_app()
        if hasattr(app.root, _label):
            exec("value = app.root.{}".format(_label))
            return value
        else:
            return ''

    def update_label(self, _label, _data):
        app = App.get_running_app()
        if hasattr(app.root, _label):
            if type(_data) is int:
                command = "app.root.{} = str({})".format(_label, _data)
            else:
                command = "app.root.{} = '{}'".format(_label, _data)
            exec(command)

    def get_workers(self):
        workers_raw_data = self.get_endpoint_data('workers')
        self.station_name = self.get_endpoint_data('stations/{}'.
            format(settings.STATION_NUMBER))['name']

        self.workers = {worker['barcode']: worker['username'] for 
                        worker in workers_raw_data}

    def update_worker(self, _barcode):
        if _barcode in self.workers:
            if self.current_worker is '':
                self.current_worker = self.workers[_barcode]
                self.update_label('worker_label', self.current_worker)
                self.update_label('status_label', 'welcome')
            else:
                self.current_worker = ''
                self.update_label('worker_label', '-')
                self.update_label('status_label', '-')
            return True
        return False

    def update_barcode_list(self, _data):
        barcode_labels = ['barcode_label_{}'.format(n) for n in range(10, 0, -1)]

        current_last_barcode_label = self.get_label_value('last_barcode_label')
        self.update_label('last_barcode_label', _data)

        for index,barcode_label in enumerate(barcode_labels[:-1]):
            self.update_label(_label=barcode_label, 
                              _data=self.get_label_value(barcode_labels[index+1]))

        if current_last_barcode_label != '':
            first_history_label = '{} {}'.format(datetime.now().strftime('%H:%M:%S'),
                                                 current_last_barcode_label)
        else:
            first_history_label = ''

        self.update_label(barcode_labels[-1], first_history_label)
        self.update_label('last_time_label', datetime.now().strftime('%H:%M:%S'))

    def add_barcode(self, _barcode):
        data_to_send = {
            "barcode": _barcode,
            "worker": self.current_worker,
            "station": self.station_name,
        }

        comment = self.get_label_value('comment_box')
        if comment:
            data_to_send['comment'] = comment
            self.update_label('comment_box', '')

        is_sended, message = self.send_endpoint_data(_endpoint='add_scan',
                                                     _data_dict=data_to_send)

        self.update_label('status_label', message)
        self.update_label('comment_box', '')

    def return_order(self, _id):
        return self.get_endpoint_data('orders/{}'.format(_id))

    def main_handling(self, _barcode):
        if self.get_label_value('main_app_name_label') is '':
            self.update_label('main_app_name_label', '{} ROOM'.format(self.station_name))

        if _barcode != 0:
            if not self.update_worker(_barcode):
                if not self.current_worker == "":
                    self.add_barcode(_barcode)
                    if self.get_label_value('second_category_flag') is True:
                        self.add_second_category(_barcode)
                        self.update_label('second_category_flag', False)
                else:
                    self.update_label('status_label', 'SCAN WORKER CARD')
            self.update_barcode_list(_barcode)
