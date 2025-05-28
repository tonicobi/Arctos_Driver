# Arctos_Driver
Arctos Driver

ArctosDriver for RoboDK - User Guide

This guide explains how to install and use the custom driver developed to control the Arctos robot from
RoboDK.

1. Introduction
This driver allows you to control a custom robot (Arctos) using RoboDK's Driver API.
It has been tested with a robot running GRBLHAL firmware and an ESP32 for WiFi connection.

2. Requirements
- RoboDK installed (with educational license or free)
- Arctos robot configured with GRBL over WiFi (TCP socket)
- Python 3 installed and available in system PATH
- RoboDK Python API available (comes with RoboDK)
  
3. Files Provided
- ArctosDriver.py: The driver script to place in the Robot_Drivers folder of RoboDK
- This guide
  
4. Installation Steps
- Open RoboDK.
- Go to Tools -> Options -> Python and make sure Python is correctly configured.
- Place the file ArctosDriver.py into RoboDK's "Robot_Drivers" folder.
   Example: C:/RoboDK/Robot_Drivers/
-Restart RoboDK.
- Load your Arctos.robot file.
- Right click on the robot -> Connect -> Select "ArctosDriver" and click "Connect".
    
5. Connection
The driver uses a persistent TCP socket connection.
Default IP: 192.168.0.1
Port: 8888
Make sure the robot is powered and the IP is reachable.

6. Troubleshooting
- Check the robot IP and port.
- Monitor the RoboDK log window (Tools -> Show Log).
- Test using a simple program with MoveJ or MoveL commands.
  
7. License
This driver was developed for educational use and is shared with the RoboDK community.
