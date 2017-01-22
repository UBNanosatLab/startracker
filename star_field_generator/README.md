Installing:

(assuming you have already done the README.md in ../camera_simulator)
Note: if you only want to use one of the pregenerated sky tiles, this is unnecessary)

sudo apt-get install blender display
sudo pip install sphere2cube

Usage:
./generate_cube.sh n

generates 6 textures of size n*1024 X n*1024 if they do not already exist.

If they do already exist, set them to be the current texture in ../camera_simulator (but do not generate)
