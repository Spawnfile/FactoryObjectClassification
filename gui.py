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
from datetime import date
import socket
from kivy.core.window import Window

class ConnectPage(FloatLayout): 
    def __init__(self, **kwargs):

        self.UDP_IP = "192.168.1.32" 
        self.UDP_PORT = 8888
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        super().__init__(**kwargs) 
        self.today = str(date.today().strftime("%d.%m.%y"))

        self.img1=Image(size_hint=(0.5, 0.5), pos_hint={'x':-0.02 ,'y':0.30})
        self.add_widget(self.img1)
        self.img2=Image(size_hint=(0.5, 0.5), pos_hint={'x':0.5 ,'y':0.30})
        self.add_widget(self.img2)
        
        self.makas_counter = 0
        self.micron_counter = 0
        self.mod = None
        Clock.schedule_interval(self.update, 1.0/33.0)
        print("Class Inits")
        self.class_1_count = Label(markup=True, halign="left", valign="middle", font_size=70, pos_hint={'x':0,'y':-0.1}) 
        self.class_2_count= Label(markup=True, halign="left", valign="middle", font_size=50, pos_hint={'x':0,'y':0.15})
        self.micron_count = Label(markup=True, halign="left", valign="middle", font_size=70, pos_hint={'x':0,'y':-0.3})
        self.micron= Label(text="Micron Sayısı",halign="left", valign="middle", font_size=50, pos_hint={'x':0,'y':-0.2})
        self.class_3_count= Label(text="Makas Sayısı",halign="left", valign="middle", font_size=50, pos_hint={'x':0,'y':0})  
        self.class_4_count= Label(text="Bant Durumu",halign="left", valign="middle", font_size=50, pos_hint={'x':0,'y':0.25})  
        
        self.add_widget(self.micron_count)
        self.add_widget(self.micron)
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
        MESSAGE = "Start".encode()
        self.sock.sendto(MESSAGE, (self.UDP_IP, self.UDP_PORT))
        message_class_2 = "[color=00FF00]ÇALIŞIYOR[/color]"              
        chat_app.connect_page.count_update_class_2(message_class_2)

    def stop_button_act(self, *_):
        print("Stop Conveyor Belt")
        MESSAGE = "Stop".encode()
        self.sock.sendto(MESSAGE, (self.UDP_IP, self.UDP_PORT))
        message_class_2 = "[color=FF0000]DURUYOR[/color]"
        chat_app.connect_page.count_update_class_2(message_class_2)

    def count_update_class_2(self, message_class_2):
        self.class_2_count.text = str(message_class_2)  

    def SaveClass_1(self, frame):
        #FOR MAKAS CLASS
        print("Cloud icindeki :", self.makas_counter)       
        buf1 = cv2.flip(frame, 0)
        buf = buf1.tostring()
        texture2 = Texture.create(size=(buf1.shape[1], buf1.shape[0]), colorfmt='bgr')
        texture2.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        self.img2.texture = texture2
        filename = "/home/alper/Desktop/FactoryObjectClassification/dataset/makas/" + str(self.makas_counter) + self.today + ".jpg"
        print(filename)
        cv2.imwrite(filename,frame)
        print("resim")
        return True

    def SaveClass_2(self, frame):
        #FOR MİCRON CLASS
        print("Cloud icindeki :", self.micron_counter)       
        buf1 = cv2.flip(frame, 0)
        buf = buf1.tostring()
        texture2 = Texture.create(size=(buf1.shape[1], buf1.shape[0]), colorfmt='bgr')
        texture2.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        self.img2.texture = texture2
        filename = "/home/alper/Desktop/FactoryObjectClassification/dataset/micron/" + str(self.micron_counter) + self.today + ".jpg"
        print(filename)
        cv2.imwrite(filename,frame)
        print("resim")
        return True

    def update(self, dt):
        detections, frame = yolo()
        try:
            mid_point = detections[0][2][1]
            name = detections[0][0].decode()
            print("Mid Point :", mid_point) 
            if mid_point > 50 and mid_point < 200:      
                self.mod = "Tracking"
                
            if mid_point > 304 and self.mod == "Tracking":
                self.mod = "Counting"
                if name == "makas":
                    self.makas_counter += 1
                    self.class_1_count.text = str(self.makas_counter)
                    self.SaveClass_1(frame)
                    print("Makas Counter: ", self.makas_counter)
                elif name == "micron":
                    self.micron_counter += 1
                    self.micron_count.text = str(self.micron_counter)
                    self.SaveClass_2(frame)
                    print("Micron Counter: ", self.micron_counter)
        except:
            print("Waiting..")
            pass
        
        buf1 = cv2.flip(frame, 0)
        buf = buf1.tostring()
        texture1 = Texture.create(size=(buf1.shape[1], buf1.shape[0]), colorfmt='bgr')
        texture1.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        self.img1.texture = texture1
        #self.img2.texture = texture1
    
class EpicApp(App):
    def build(self):
        self.screen_manager = ScreenManager()
        self.connect_page = ConnectPage()
        screen_1 = Screen(name='Connect')
        screen_1.add_widget(self.connect_page)
        self.screen_manager.add_widget(screen_1)
        return self.screen_manager

if __name__ == "__main__":
    Window.fullscreen = 'fake'
    chat_app = EpicApp()
    chat_app.run()

