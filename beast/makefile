CC = g++
CFLAGS = `pkg-config --cflags opencv`
LIBS = `pkg-config --libs opencv`

all: $(OBJ)
	$(CC) -g beast.cpp -o beast $(OBJ) $(LIBS)
