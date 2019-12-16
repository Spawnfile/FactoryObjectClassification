import cv2
from webcam import yolo

duracell_counter = 0
micron_counter = 0
scissors_counter = 0
def counter(object_id, duracell_counter= 0, micron_counter= 0, scissors_counter= 0):
    if object_id == "duracell":
        #duracell_counter += 1
        print("Duracell Counter: ", duracell_counter)
    elif object_id == "micron":
        micron_counter += 1
        print("Micron Counter: ", micron_counter)
    elif object_id == "makas":
        scissors_sayi = scissors_counter + 1
        print("Scissors Counter: ", scissors_sayi)
        scissors_counter = scissors_sayi
    #counting algoritm
    #return counting_object to gui
    pass

def cloud(a):
    #push counter data to cloud
    #threading
    pass

def main():

    while True:
        detections, _, top_left_coordinates, bottom_right_coordinates = yolo()
        try:
            print(top_left_coordinates)
            print(bottom_right_coordinates)
            print("Object: ",detections[0][0].decode())
            print("Middle Point: ",detections[0][2][0])        
            print(duracell_counter)
            detection_counter = len(detections)
            print("Detection")
            counter("makas")
            print("sea")
            return detection_counter
        except:
            print("Waiting..")


if __name__ == "__main__":
    main()
