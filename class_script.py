from webcam import yolo

class alper():
    def __init__(self):
        self.counter = 8
    def sayan_fonk(self):
        #push counter data to cloud
        #threading
        self.counter += 1
        print("cloud icindeki :",self.counter)
        return self.counter

    def main(self):
        self.counter = 0
        while True:
            detections, _ = yolo()        
            try:
                print("Mid Point :",detections[0][2][0]) 
                if detections[0][2][0] > 50 and detections[0][2][0] < 200:      
                    mod = "Tracking"
                    
                if detections[0][2][0] > 304 and mod == "Tracking":
                    mod = "Counting"
                    #self.counter += 1
                    self.sayan_fonk()
                    print("sayac: ", self.counter)
                    
            except:
                print("Waiting..")

if __name__ == "__main__":
    a = alper() 
    a.main()
    
