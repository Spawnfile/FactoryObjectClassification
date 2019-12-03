# FactoryObjectClassification

**TO DO's in this project.**

-Object Definition
  -Water Bottle
  -++something

-Preparing a dataset

-Write a custom NN to make predictions and detections.

-Prepare a GUI for these. GUI will has 3 specs.
  -Live CAM and detection screen (Updating per frame) 
  -Objects counts
  -Start-stop the production line

Production line is working => start detection and counting
Production line is **NOT** working => stop detection and counting (Live Stream keep going but counting and detection will not going on)
(Kivy)

-write a main python code for counting and combine it with NN and import main NN code to use. 

**STRUCTURE**

-Step motor controlling a conveyor belt with raspberry pi

-Raspberry Pi controlled by PC via UDP on same network.

-PC doing detection and send cameras frames to GUI

-GUI showing these frames + controlling conveyor belt for starting and stoping.


**FlowChart**

-Capture Frame

-Do Detection

-Send frames to GUI

-Count Objects -------->1 Thread to push these information to cloud. (Power BI)


