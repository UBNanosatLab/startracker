CC = g++
CFLAGS = `pkg-config --cflags opencv`
LIBS = `pkg-config --libs opencv`

all: $(OBJ)
	$(CC) beast.cpp -o beast $(OBJ)
	$(CC) -g getstars.cpp -o getstars $(OBJ) $(LIBS)
