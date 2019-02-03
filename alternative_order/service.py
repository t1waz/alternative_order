from datetime import datetime
from api_service import ApiService
import settings
import copy


class AppService:
    def __init__(self, my_app):
        self.api = ApiService()
        self.my_app = my_app
        self.current_worker = ''
        self.workers = {}
        self.readed_order = {}
        self.current_order = 0
        self.current_boards = []
        self.init_values()

    def init_values(self):
        workers_raw_data = self.api.get_endpoint_data(endpoint='workers')

        self.my_app.main_app_name_label = '{} ROOM'.format(settings.STATION_NAME)
        self.workers = {worker['barcode']: worker['username'] for worker in workers_raw_data}

    def update_worker(self, _barcode):
        if _barcode in self.workers:
            self.my_app.worker_label = self.workers[_barcode] if not self.current_worker else '-'
            self.my_app.status_label = 'welcome' if not self.current_worker else '-'
            if not self.current_worker:
                self.current_worker = self.workers[_barcode]
                self.api.send_endpoint_data(endpoint='add_worker_scan',
                                            data={"worker_barcode": self.current_worker,
                                                  "started": True})
            else:
                self.api.send_endpoint_data(endpoint='add_worker_scan',
                                            data={"worker_barcode": self.current_worker,
                                                  "started": False})
                self.current_worker = ''
            return True
        return False

    def update_barcode_list(self, _data):
        current_last_barcode_label = self.my_app.last_barcode_label
        self.my_app.last_barcode_label = str(_data)

        for index in range(10, 1, -1):
            up_label = getattr(self.my_app, 'barcode_label_{}'.format(index - 1))
            setattr(self.my_app, 'barcode_label_{}'.format(index), up_label)

        first_label = '{} {}'.format(datetime.now().strftime('%H:%M:%S'),
                                     current_last_barcode_label)

        self.my_app.barcode_label_1 = first_label if current_last_barcode_label != '' else ''
        self.my_app.last_time_label = datetime.now().strftime('%H:%M:%S')

    def add_barcode(self, _barcode):
        status, message = self.api.send_endpoint_data(endpoint='add_sended_board',
                                                      data={"board": _barcode,
                                                            "order": self.current_order})
        if status == 200:
            self.current_boards.append(_barcode)
            self.my_app.status_label = 'ADDED'
        else:
            self.my_app.status_label = message.get('detail', "")

        if status == 200:
            self.current_boards.append(_barcode)
            self.my_app.status_label = 'ADDED'
        else:
            self.my_app.status_label = message.get('detail', "")

    def check_new_order_available(self):
        if self.my_app.order_id != self.current_order:
            if self.my_app.order_id is not 0:
                self.load_order(self.my_app.order_id)
            else:
                self.clear_order()
            self.current_order = self.my_app.order_id

    def handle_delete(self, _barcode):
        if self.delete_barcode(_barcode):
            self.my_app.status_label = 'DELETED'
        else:
            self.my_app.status_label = 'CANNOT DELETE'

        self.my_app.delete_board_button = 'DELETE BOARD'

    def check_if_send_order(self):
        if self.my_app.status_label == 'SENDING':
            already_sended_boards = self.return_current_models()
            if all(value == 0 for value in already_sended_boards.values()):
                status, message = self.api.update_endpoint_data(
                    endpoint='orders/{}'.format(self.current_order),
                    data={"completed": "true"})
                self.my_app.status_label = 'SENDED' if status == 200 else 'ERROR'
            else:
                self.my_app.status_label = 'NOT FULL'
            self.current_boards = []
            self.current_order = 0
            self.my_app.order_id = 0
            self.my_app.order_texbox.text = ''
            self.my_app.load_order_button = 'LOAD ORDER'

    def clear_order(self):
        self.my_app.order_detail_label = ''
        self.my_app.order_texbox.text = ''
        already_sended = self.api.get_endpoint_data(
            endpoint="orders/{}".format(self.current_order))['sended']

        for board in already_sended:
            if not self.delete_barcode(board):
                self.current_boards = self.api.get_endpoint_data(
                    endpoint="orders/{}".format(self.order_id))['sended']
                self.my_app.status_label = 'REMOVE ERROR'
                return False

        self.current_boards = []
        self.my_app.status_label = 'REMOVED'
        self.readed_order = {}
        self.my_app.delete_board_button = 'DELETE BOARD'

    def delete_barcode(self, _barcode):
        status, message = self.api.delete_endpoint_data(endpoint='add_sended_board',
                                                        data={"board": _barcode})

        if message == 'barcode removed from order' and status == 200:
            self.current_boards.remove(_barcode)
            return True
        else:
            return False

    def load_order(self, _id):
        order = self.api.get_endpoint_data(endpoint="orders/{}".format(_id))
        if order['completed']:
            self.my_app.status_label = 'ALREADY SENDED'
            self.my_app.load_order_button = 'LOAD ORDER'
            self.my_app.order_texbox.text = ''
            return False

        boards = order.get('boards', False)
        self.current_boards = order.get('sended', [])
        self.my_app.status_label = 'ORDER LOADED' if boards else 'NO ORDER'
        self.my_app.order_detail_label = order['client'] if boards else ''
        self.readed_order = boards if boards else {}

        self.create_message_list()

    def return_current_models(self):
        already_sended_boards = copy.deepcopy(self.readed_order)
        for board in self.current_boards:
            board_model = self.api.get_endpoint_data(endpoint='boards/{}'.format(board))['model']
            already_sended_boards[board_model] -= 1
        return already_sended_boards

    def check_if_send_order(self):
        if self.my_app.status_label == 'SENDING':
            already_sended_boards = self.return_current_models()
            if all(value == 0 for value in already_sended_boards.values()):
                status, message = self.api.update_endpoint_data(
                    endpoint='orders/{}'.format(self.current_order),
                    data={"completed": "true"})
                self.my_app.status_label = 'SENDED' if status == 200 else 'ERROR'
            else:
                self.my_app.status_label = 'NOT FULL'
                return False
            self.current_boards = []
            self.current_order = 0
            self.my_app.order_id = 0
            self.my_app.order_texbox.text = ''
            self.my_app.load_order_button = 'LOAD ORDER'
            self.my_app.order_detail_label = ''

    def create_message_list(self):
        self.my_app.message_labels = []
        already_sended_boards = self.return_current_models()

        for index, board in enumerate(self.readed_order):
            self.my_app.message_labels.append('{}:{}{}{}{}'.format(board,
                                                                   ' ' * (20 - len(board)),
                                                                   self.readed_order[board],
                                                                   '        ',
                                                                   already_sended_boards[board]))

    def main_handling(self, _barcode):
        if not self.update_worker(_barcode):
            if not self.current_order:
                self.my_app.status_label = 'READ ORDER'
            elif not self.current_worker:
                self.my_app.status_label = 'SCAN WORKER CARD'
            else:
                if self.my_app.delete_board_button == 'CANCEL DELETE':
                    self.handle_delete(_barcode)
                else:
                    self.add_barcode(_barcode)
                self.create_message_list()
        self.update_barcode_list(_barcode)
