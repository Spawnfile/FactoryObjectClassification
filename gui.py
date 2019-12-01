import kivy
import cv2
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager, Screen


class ConnectPage(FloatLayout): 
    def __init__(self, **kwargs):
        super().__init__(**kwargs) 
        self.img1=Image(size_hint=(0.5, 0.5), pos_hint={'x':0.1 ,'y':0.30})
        self.add_widget(self.img1)
        Clock.schedule_interval(self.update, 1.0/33.0)
        
        #Will be added imported from network outpu to show instead of clock and update function.
        self.class_1_count = Label(halign="left", valign="middle", font_size=30, pos_hint={'x':0.22,'y':0.1}) 
        self.class_2_count= Label(halign="left", valign="middle", font_size=30, pos_hint={'x':0.22,'y':0}) 

        self.add_widget(self.class_1_count)
        self.add_widget(self.class_2_count)

        self.button_basla = Button(text="BAŞLA", font_size=12, size_hint=(0.1, 0.1), pos_hint={'x':0.7, 'y':0.2})
        self.button_basla.bind(on_press=self.start_button_act)
        self.add_widget(self.button_basla)

        self.button_dur = Button(text="DUR", font_size=12, size_hint=(0.1, 0.1), pos_hint={'x':0.8, 'y':0.2})
        self.button_dur.bind(on_press=self.stop_button_act)
        self.add_widget(self.button_dur)

        self.capture = cv2.VideoCapture(2)

    def start_button_act(self, *_):
        print("start butonuna basıldı")
        message_class_1 = "start butonu"
        chat_app.connect_page.count_update_class_1(message_class_1)
        
    def stop_button_act(self, *_):
        print("stop butonuna basıldı")
        message_class_2 = "stop butonu"
        chat_app.connect_page.count_update_class_2(message_class_2)
    
    def count_update_class_1(self, message_class_1):
        self.class_1_count.text = str(message_class_1)        

    def count_update_class_2(self, message_class_2):
        self.class_2_count.text = str(message_class_2)      

    def update(self, dt):
        ret, frame = self.capture.read()
        buf1 = cv2.flip(frame, 0)
        buf = buf1.tostring()
        texture1 = Texture.create(size=(buf1.shape[1], buf1.shape[0]), colorfmt='bgr')
        texture1.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        self.img1.texture = texture1
    

class EpicApp(App):
    def build(self):
        self.screen_manager = ScreenManager()
        self.connect_page = ConnectPage()
        screen_1 = Screen(name='Connect')
        screen_1.add_widget(self.connect_page)
        self.screen_manager.add_widget(screen_1)
        return self.screen_manager


if __name__ == "__main__":
    chat_app = EpicApp()
    chat_app.run()
