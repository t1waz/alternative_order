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
        self.current_order_boards = {}
        self.readed_order = {}
        self.current_order = 0
        self.current_boards = []

    def get_endpoint_data(self, _endpoint_string):
        try:
            response = requests.get(url='http://{}/{}/'.format(settings.BACKEND_URL, _endpoint_string),
                                    headers={'Access-Token': settings.BACKEND_ACCESS_TOKEN,
                                             'Content-Type': 'application/json'})
        except requests.ConnectionError:
            # TU ZROBIC JAKIS HANDLING JESLI NIE DZIALA SERWER ELO
            return {}
        if response.status_code == 200:
            return response.json()
        else:
            return {}

    def send_endpoint_data(self, _endpoint, _data_dict):
        response = requests.post(url='http://{}/{}/'.format(settings.BACKEND_URL, _endpoint),
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
            return eval("app.root.{}".format(_label))
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

    def update_list_property(self,_label, _data):
        app = App.get_running_app()
        if hasattr(app.root, _label):
            if type(_data) is int:
                exec("app.root.{}.append(str({}))".format(_label, _data))
            else:
                exec("app.root.{}.append('{}')".format(_label, _data))

    def clear_list_property(self, _label):
        app = App.get_running_app()
        if hasattr(app.root, _label):
            exec("app.root.{} = []".format(_label))

    def get_workers(self):
        workers_raw_data = self.get_endpoint_data('workers')

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
        if self.current_order == 0:
            self.update_label('status_label', 'READ ORDER')
            return False
        
        message = self.get_endpoint_data(_endpoint_string='boards/{}'.format(_barcode))
        if not bool(message):
            self.update_label('status_label', 'INVALID BARCODE')
            return False

        model_count = self.current_order_boards.get(message['model'], False)
        if not model_count:
            self.update_label('status_label', 'NOT IN ORDER')
            return False

        if model_count > 0:
            self.current_boards.append(_barcode)
            self.current_order_boards[message['model']] = model_count - 1
            self.update_label('status_label', 'ADDED')
        else:
            self.update_label('status_label', 'MODEL FULL')

    def check_new_order_available(self):
        order_number = self.get_label_value('order_id')
        if order_number != self.current_order:
            self.current_order = order_number
            self.load_order(order_number)

    def load_order(self, _id):
        order = self.get_endpoint_data("orders/{}".format(_id))
        boards = order.get('boards', False)
        if boards:
            self.current_order_boards = boards
            self.readed_order = boards
            self.update_label('status_label', 'ORDER LOADED')
            self.update_label('order_detail_label', order['client'])
            self.create_message_list()

    def create_message_list(self):
        self.clear_list_property('message_labels')
        index = 0
        for board, qty in self.readed_order.items():
            free_space = ' '*(20 - len(board))
            label_value = '{}:{}{}       {}    <--- LEFT'.format(board,free_space, 
                                                            qty,
                                                            self.current_order_boards[board])
            self.update_list_property('message_labels',label_value)
            index = index + 1

    def main_handling(self, _barcode):
        if self.get_label_value('main_app_name_label') is '':
            self.update_label('main_app_name_label', '{} ROOM'.format(self.station_name))

        if _barcode != 0:
            if not self.update_worker(_barcode):
                if not self.current_worker == "":
                    self.add_barcode(_barcode)
                    self.create_message_list()
                else:
                    self.update_label('status_label', 'SCAN WORKER CARD')
            self.update_barcode_list(_barcode)