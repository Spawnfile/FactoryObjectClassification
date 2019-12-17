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
from webcam import yolo
from threading import Thread

class ConnectPage(FloatLayout): 
    def __init__(self, **kwargs):
        super().__init__(**kwargs) 
        self.img1=Image(size_hint=(0.5, 0.5), pos_hint={'x':-0.02 ,'y':0.30})
        self.add_widget(self.img1)
        self.img2=Image(size_hint=(0.5, 0.5), pos_hint={'x':0.5 ,'y':0.30})
        self.add_widget(self.img2)

        self.counter = 0
        self.mod = None
        Clock.schedule_interval(self.update, 1.0/33.0)
        print("Class Inits")
        self.class_1_count = Label(markup=True, halign="left", valign="middle", font_size=70, pos_hint={'x':0,'y':-0.1}) 
        self.class_2_count= Label(markup=True, halign="left", valign="middle", font_size=50, pos_hint={'x':0,'y':0.15})
        self.class_3_count= Label(text="Sayılan Obje",halign="left", valign="middle", font_size=50, pos_hint={'x':0,'y':0})  
        self.class_4_count= Label(text="Bant Durumu",halign="left", valign="middle", font_size=50, pos_hint={'x':0,'y':0.25})  
        
        self.add_widget(self.class_3_count)
        self.add_widget(self.class_1_count)
        self.add_widget(self.class_2_count)
        self.add_widget(self.class_4_count)

        self.button_basla = Button(text="BAŞLA", font_size=30, size_hint=(0.08, 0.08), pos_hint={'x':0.40, 'y':0}, background_color = [0,1,0,1])
        self.button_basla.bind(on_press=self.start_button_act)
        self.add_widget(self.button_basla)

        self.button_dur = Button(text="DUR", font_size=30, size_hint=(0.08, 0.08), pos_hint={'x':0.48, 'y':0}, background_color = [1,0,0,1])
        self.button_dur.bind(on_press=self.stop_button_act)
        self.add_widget(self.button_dur)

    def start_button_act(self, *_):
        print("Start Conveyor Belt")
        message_class_2 = "[color=00FF00]ÇALIŞIYOR[/color]"              
        chat_app.connect_page.count_update_class_2(message_class_2)

    def stop_button_act(self, *_):
        print("Stop Conveyor Belt")
        message_class_2 = "[color=FF0000]DURUYOR[/color]"
        chat_app.connect_page.count_update_class_2(message_class_2)
    
    def sayan_fonk(self, frame):
        self.counter += 1
        print("cloud icindeki :", self.counter)
        self.class_1_count.text = str(self.counter)
        buf1 = cv2.flip(frame, 0)
        buf = buf1.tostring()
        texture2 = Texture.create(size=(buf1.shape[1], buf1.shape[0]), colorfmt='bgr')
        texture2.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        self.img2.texture = texture2
        print("resim")
        return self.counter       

    def count_update_class_2(self, message_class_2):
        self.class_2_count.text = str(message_class_2)      

    def update(self, dt):
        detections, frame = yolo()
        try:
            print("Mid Point :",detections[0][2][0]) 
            if detections[0][2][0] > 50 and detections[0][2][0] < 200:      
                self.mod = "Tracking"
                
            if detections[0][2][0] > 304 and self.mod == "Tracking":
                self.mod = "Counting"
                #self.counter += 1
                self.sayan_fonk(frame)
                print("Counter: ", self.counter)
                
        except:
            print("Waiting..")
            pass
        
        #print("Update func")
        buf1 = cv2.flip(frame, 0)
        buf = buf1.tostring()
        texture1 = Texture.create(size=(buf1.shape[1], buf1.shape[0]), colorfmt='bgr')
        texture1.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        self.img1.texture = texture1
        #self.img2.texture = texture1
    
    def thread_start(self):
        try:
            t = Thread(target = self.thread_udp_read, args=(1,))
            t.daemon = True #for working forever
            t.start()
            print("Thread Started")
        except:
            print("Thread Does not Started")
    
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

