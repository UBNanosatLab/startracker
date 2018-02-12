
DISPLAY=:0 SDL_VIDEO_WINDOW_POS="1560,0" python camera_simulator.py&
#DISPLAY=:0 SDL_VIDEO_WINDOW_POS="0,0" python camera_simulator.py&
pid="$!"
DISPLAY=:0 python webcam_server.py screenshot
kill $pid
sleep .2
echo Done
