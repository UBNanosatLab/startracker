
DISPLAY=:0 SDL_VIDEO_WINDOW_POS="1560,0" python camera_simulator.py&
pid="$!"
python webcam_server.py
kill $pid
sleep .2
echo Done
