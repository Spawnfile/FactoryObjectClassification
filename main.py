from webcam import yolo
import socket

IP = "192.168.1.32"
PORT = 8888
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def cloud(counter):
    #send data to cloud
    pass

def Counter():
    print("Object Counted..")
    return True

def main():
    counter = 0 
    while True:
        detections, _ = yolo()        
        try:
            print("Mid Point :", detections[0][2][0]) 
            if detections[0][2][0] > 50 and detections[0][2][0] < 200:      
                mod = "Tracking"
                
            if detections[0][2][0] > 304 and mod == "Tracking":
                mod = "Counting"
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                counter += 1
                sock.sendto(str(counter).encode(), (IP, PORT))
                print("Counter: ", counter)
        except:
            print("Waiting..")

if __name__ == "__main__":
    main()
