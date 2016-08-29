CC = g++
CFLAGS = `pkg-config --cflags opencv`
LIBS = `pkg-config --libs opencv`

all: $(OBJ)
	$(CC) -g -O0 beast.cpp -o beast $(OBJ)
	$(CC) -g getstars.cpp -o getstars $(OBJ) $(LIBS)
