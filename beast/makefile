CC = g++
#CFLAGS = `pkg-config --cflags opencv`
#LIBS = `pkg-config --libs opencv`

#$(CC) -g getstars.cpp -o getstars $(OBJ) $(LIBS)
#$(CC) beast.cpp -o beast $(OBJ)
all: $(OBJ)
	$(CC) -O2 -fPIC -c beast.cpp -o beast.o
	$(CC) -O2 -fPIC -c beast_wrap.cxx -o beast_wrap.o -lstdc++ -I/usr/include/python2.7
	$(CC) -shared -fPIC beast_wrap.o beast.o -o _beast.so

debug:
	$(CC) -Wall -O0 -g beast.cpp -o beast
	
