from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.properties import (
    StringProperty,
    BooleanProperty,
    ObjectProperty
)

Builder.load_file('graphic.kv')

class MainWindow(Screen):

    test_property = ObjectProperty()
    elo = ObjectProperty()

    def __init__(self, **kwargs):

        super(MainWindow, self).__init__(**kwargs)


    def add(self):
        print("chuj")
        box = self.ids['box_to_add']
        self.test_property.add_widget(Label(id=self.elo, text="aaaaa", color=(0,0,0,1)))

    def remove(self):
        box = App.get_running_app()
        print(dir(box.root))
        self.elo.text = 'ASDASDASD'
        print("chuj2")

class ScanApp(App):
    def build(self):

        return MainWindow()


if __name__ == '__main__':
    ScanApp().run()
