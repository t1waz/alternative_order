from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from scanner import BarcodeScanner
from service import AppService
import threading
from kivy.properties import (
    StringProperty,
    ObjectProperty,
    NumericProperty,
    ListProperty
)


Builder.load_file('graphic.kv')


class ScannerThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.barcode_scanner = BarcodeScanner()
        self.app_service = AppService()
        self.last_barcode_scan = 0

    def run(self):
        self.app_service.get_workers()
        while True:
            current_barcode_scan = self.barcode_scanner.ask_data()
            self.app_service.main_handling(current_barcode_scan)
            self.app_service.check_new_order_available()


class MessageWindow(Popup):
    message_box = ObjectProperty()
    def __init__(self, **kwargs):
        super(MessageWindow, self).__init__(**kwargs)


class MainWindow(Screen):
    main_app_name_label = StringProperty('PACKAGE ROOM')
    last_barcode_label = StringProperty('')
    last_time_label = StringProperty('-')
    status_label = StringProperty('connected')
    worker_label = StringProperty('-')
    order_detail_label = StringProperty('NO ORDER')
    order_number_texbox = ObjectProperty()
    order_id = NumericProperty()
    for index in range(1, 11):
        variable_name = 'barcode_label_{}'.format(index)
        exec(variable_name + '  = StringProperty()')
    message_labels = ListProperty()

    def __init__(self, **kwargs):
        super(MainWindow, self).__init__(**kwargs)

    def exit_app(self):
        App.get_running_app().stop()

    def show_info(self, *args):
        message_window = MessageWindow()
        message_window.message_box.add_widget(Label())
        for each in self.message_labels:
            message_window.message_box.add_widget(Label(text=each))
        message_window.message_box.add_widget(Label())
        message_window.open()

    def load_order(self, *args):
        try:
            self.order_id = int(self.order_number_texbox.text)
        except ValueError:
            self.order_id = 0

    def update_padding(self, text_input, *args):
        text_width = text_input._get_text_width(
            text_input.text,
            text_input.tab_width,
            text_input._label_cached
        )

        text_input.padding_x = (text_input.width - text_width) / 2


class ScanApp(App):
    def __init__(self, **kwargs):
        ScannerThread().start()
        super(ScanApp, self).__init__(**kwargs)

    def build(self):
        return MainWindow()


if __name__ == '__main__':
    ScanApp().run()
