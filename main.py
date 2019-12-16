from webcam import yolo

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
                counter += 1
                Counter()
                print("Counter: ", counter)
        except:
            print("Waiting..")

if __name__ == "__main__":
    main()
