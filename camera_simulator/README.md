Setting up camera_simulator
---------------------------
Run this code

`sudo apt-get install python-pip`  
`sudo apt-get install python-dev`

###Now run these 

`sudo pip install PyOpenGL PyOpenGL_accelerate "PyVRML97==2.3.0a4" simpleparse numpy "OpenGLContext==2.2.0a3"`  
`sudo pip install pillow PyDispatcher PyVRML97 OpenGLContext`

If you are using Windows you will need to do a few more steps  
First download and install pygame *2.7.msi using the link below

[Pygame *2.7.msi link](http://www.pygame.org/download.shtml)

Now you need to open idle (python gui) and use that to open Chapter 12\buff_sky_small\skybox.py
now hit f5

If the sky just sits there, the mastersim probably isnt running  
ssh into intrepid@jeb.eng.buffalo.edu and type

`cd ~/master_sim/b/Matlab-Code/masterSim`   
`./run_mastersim.sh`


