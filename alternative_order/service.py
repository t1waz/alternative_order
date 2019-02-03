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
        workers_raw_data = self.api.get_endpoint_data('workers')

        self.my_app.main_app_name_label = '{} ROOM'.format(settings.STATION_NAME)
        self.my_app.status_label = 'connected'

        self.workers = {worker['barcode']: worker['username'] for worker in workers_raw_data}

    def update_worker(self, _barcode):
        # tu zrobic handling jesli wbija sie ktos inny a ja jestem juz wbity
        if _barcode in self.workers:
            self.my_app.worker_label = self.workers[_barcode] if not self.current_worker else '-'
            self.my_app.status_label = 'welcome' if not self.current_worker else '-'
            self.current_worker = self.workers[_barcode] if not self.current_worker else ''
            return True
        return False

    def update_barcode_list(self, _data):
        current_last_barcode_label = self.my_app.last_barcode_label
        self.my_app.last_barcode_label = str(_data)

        for index in range(10, 1, -1):
            up_label = getattr(self.my_app, 'barcode_label_{}'.format(index - 1))
            setattr(self.my_app, 'barcode_label_{}'.format(index), up_label)

        if current_last_barcode_label != '':
            first_history_label = '{} {}'.format(datetime.now().strftime('%H:%M:%S'),
                                                 current_last_barcode_label)
        else:
            first_history_label = ''

        self.my_app.barcode_label_1 = first_history_label
        self.my_app.last_time_label = datetime.now().strftime('%H:%M:%S')

    def add_barcode(self, _barcode):
        my_scan = {"board": _barcode,
                   "order": self.current_order}
        status, message = self.api.send_endpoint_data('add_sended_board',my_scan)
        self.my_app.status_label = 'ADDED' if status else message['detail']
        if status:
            current_board = self.api.get_endpoint_data(_endpoint_string='boards/{}'.format(_barcode))
            self.current_boards.append(_barcode)

    def handle_delete(_barcode):
        self.status_label = 'DELETED' if self.delete_barcode(_barcode) else 'CANNOT DELETE'
        self.my_app.delete_board_button = 'DELETE BOARD'

    def check_new_order_available(self):
        if self.my_app.order_id != self.current_order:
            if self.my_app.order_id is not 0:
                self.load_order(self.my_app.order_id)
            else:
                self.clear_order()
            self.current_order = self.my_app.order_id

    def check_if_send_order(self):
        if self.my_app.status_label == 'SENDING':
            # if all(value == 0 for value in .values()):
            #     a, b = self.api.update_endpoint_data('orders/{}/'.format(self.order_id),
            #                                   {"completed": true})
            #     print(a,b)
            #     self.my_app.status_label = 'SENDED'
            pass


    def clear_order(self):
        self.my_app.order_detail_label = ''
        self.my_app.order_texbox.text = ''
        # tutaj wstawic zeby bralo z zamowienia a nie z cache appki
        removed_all = True
        for board in self.current_boards:
            if not self.delete_barcode(board):
                removed_all = False
        #
        self.current_boards = []
        self.my_app.delete_board_button = 'DELETE BOARD'
        self.my_app.status_label = 'REMOVED' if removed_all else 'REMOVE ERROR'
        self.readed_order = {}


    def delete_barcode(self, _barcode):
        status, message = self.api.delete_endpoint_data('add_sended_board',
                                                        {"board": _barcode})

        if message == 'barcode removed from order' and status:
            current_board = self.api.get_endpoint_data('boards/{}'.format(_barcode))
            self.current_boards.remove(_barcode)
            return True
        else:
            return False

    def load_order(self, _id):
        order = self.api.get_endpoint_data("orders/{}".format(_id))
        boards = order.get('boards', False)
        self.current_boards = order.get('sended', False)
        self.my_app.status_label = 'ORDER LOADED' if boards else 'NO ORDER'
        self.my_app.order_detail_label = order['client'] if boards else ''
        self.readed_order = boards if boards else {}
        self.current_boards = [] # tu zmienic zeby bralo z sended_board
        if not boards:
            self.my_app.order_texbox.text = ''
            self.my_app.load_order_button = 'LOAD ORDER'
        self.create_message_list()

    def create_message_list(self):
        self.my_app.message_labels = []
        index = 0
        already_sended_boards = copy.deepcopy(self.readed_order)
        for board in self.current_boards:
            already_sended_boards[self.api.get_endpoint_data('boards/{}'.format(board))['model']] -= 1
        print(already_sended_boards)
        for board, qty in self.readed_order.items():
            self.my_app.message_labels.append(
                '{}:{}{}{}{}'.format(board,
                                     ' ' * (20 - len(board)),
                                     qty,
                                     '        ',
                                     already_sended_boards[board]))
            index = index + 1

    def main_handling(self, _barcode):
        if not self.update_worker(_barcode):
            if self.current_order == 0:
                self.my_app.status_label = 'READ ORDER'
            else:
                if not self.current_worker == "":
                    if self.my_app.delete_board_button == 'CANCEL DELETE':
                        self.handle_delete(_barcode)
                    else:
                        self.add_barcode(_barcode)
                    self.create_message_list()
                else:
                    self.my_app.status_label = 'SCAN WORKER CARD'
        self.update_barcode_list(_barcode)
