import socket
import threading
import RPi.GPIO as GPIO
import time 

class Conveyor:
    def __init__(self):
        self.ip = ""
        self.port = 8888
        self.data = "_".encode()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.ip,self.port))
        self.out1 = 13
        self.out2 = 11
        self.out3 = 15
        self.out4 = 12
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.out1,GPIO.OUT)
        GPIO.setup(self.out2,GPIO.OUT)
        GPIO.setup(self.out3,GPIO.OUT)
        GPIO.setup(self.out4,GPIO.OUT) 

    def start(self):
        t = threading.Thread(target=self.Thread)
        t.start()

    def Thread(self):
        print("Thread Has Been Started")
        self.event = threading.Event()
        while True:
            self.data, _ = self.sock.recvfrom(1024)
                          
    def main(self):
        print("Listening The Thread")    
        print(self.data)
        if self.data.decode() == "Start":
            GPIO.output(self.out1,GPIO.LOW)
            GPIO.output(self.out2,GPIO.LOW)
            GPIO.output(self.out3,GPIO.LOW)
            GPIO.output(self.out4,GPIO.LOW)
            while True:
                print("Rotating The Stepper Motor ")
                print(self.data)
                self.stepper()
                if self.data.decode() == "Stop":
                    print("Going Out Of The LOOP")
                    GPIO.output(self.out1,GPIO.LOW)
                    GPIO.output(self.out2,GPIO.LOW)
                    GPIO.output(self.out3,GPIO.LOW)
                    GPIO.output(self.out4,GPIO.LOW)
                    break
        
    def stepper(self):
        GPIO.output(self.out1,GPIO.HIGH)
        GPIO.output(self.out2,GPIO.LOW)
        GPIO.output(self.out3,GPIO.LOW)
        GPIO.output(self.out4,GPIO.LOW)
        time.sleep(0.03)
        GPIO.output(self.out1,GPIO.HIGH)
        GPIO.output(self.out2,GPIO.HIGH)
        GPIO.output(self.out3,GPIO.LOW)
        GPIO.output(self.out4,GPIO.LOW)
        time.sleep(0.03)      
        GPIO.output(self.out1,GPIO.LOW)
        GPIO.output(self.out2,GPIO.HIGH)
        GPIO.output(self.out3,GPIO.LOW)
        GPIO.output(self.out4,GPIO.LOW)
        time.sleep(0.03)
        GPIO.output(self.out1,GPIO.LOW)
        GPIO.output(self.out2,GPIO.HIGH)
        GPIO.output(self.out3,GPIO.HIGH)
        GPIO.output(self.out4,GPIO.LOW)
        time.sleep(0.03)     
        GPIO.output(self.out1,GPIO.LOW)
        GPIO.output(self.out2,GPIO.LOW)
        GPIO.output(self.out3,GPIO.HIGH)
        GPIO.output(self.out4,GPIO.LOW)
        time.sleep(0.03)
        GPIO.output(self.out1,GPIO.LOW)
        GPIO.output(self.out2,GPIO.LOW)
        GPIO.output(self.out3,GPIO.HIGH)
        GPIO.output(self.out4,GPIO.HIGH)
        time.sleep(0.03)      
        GPIO.output(self.out1,GPIO.HIGH)
        GPIO.output(self.out2,GPIO.LOW)
        GPIO.output(self.out3,GPIO.LOW)
        GPIO.output(self.out4,GPIO.HIGH)
        time.sleep(0.03)
            
if __name__ == '__main__':
    class_variable = Conveyor()
    class_variable.start()    
    while True:
        class_variable.main()