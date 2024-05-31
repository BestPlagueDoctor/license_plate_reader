# License Plate Reader
## Sam Knight
This is code that I wrote whilst in school at the University of Illinois at Urbana-Champaign. This project is essentially a smart dashcam - after taking dashcam footage using an Rpi4, the footage is rsync'd to a server running linux where each frame is then processed. A custom YOLOv3 model trained on vehicle plates from the OpenImages dataset reads each frame and crops the license plate, and EasyOCR then reads the text and identifies the plate humber. 
