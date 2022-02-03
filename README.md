# car_counter
Python script to count cars by using OpenCV lib optimized for using on a Raspberry Pi 4.

## Features
Program counts cars on a video stream and uploads the counts to Thingspeak.com. It differentiates between the direction of travel. Furthermore it uploads the CPU temp of the pi as a part of healthmonitoring of the system.

In Debug Mode (postfix -d) a file output.avi is saved with marked image crop.

## Usage
Clone repo to your Raspberry Pi and insert your Thingspeak.com write-key `key = "HERE_YOUR_THINGSPEAK_WRITEKEY"`. Run `python3 car_counter_BGsub.py -d` first to capture a video `output.avi` from the camera. After that define the picture crop to resize the detection zone. X1, X2, Y1, Y2 are the corenerstones of the detection zone in px. Eg.:
```
# Define picture crop -> Check in debug mode!
roixy = [ 470, 675, 200, 337 ]   # X1, X2, Y1, Y2
```
After that rerun `python3 car_counter_BGsub.py -d` and check the correct place of the detection zone. After all you can run the programm `python3 car_counter_BGsub.py` to start counting and uploading the counts to Thingspeak.com

## Note
I build for the Raspberry Pi and the Camera a waterproof case from a sanitary pipe. So, the system runs now for month without any problems. You can check the results on my [Thingspeak.com-channel](https://thingspeak.com/channels/1521548).

![car_counter_1](https://user-images.githubusercontent.com/98514822/152338992-629f6a18-d625-456b-b1ce-af7694e5e03e.jpg)
![car_counter_2](https://user-images.githubusercontent.com/98514822/152338995-1004e53d-9e4e-46f2-a6ae-ba2c5f58dfc2.jpg)
![car_counter_3](https://user-images.githubusercontent.com/98514822/152338997-e8b4b55a-eb58-49cd-ada7-233f3787d66b.jpg)

## Requirements
python
openCV
numpy
gpiozero

Inspired by
https://www.youtube.com/watch?v=HXDD7-EnGBY
