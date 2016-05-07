#include <iostream>     // cout
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>    /* For O_RDWR */
#include <sys/mman.h>


using namespace std;

struct constelation {
	int s[4];
	double p[6];
	struct constelation *last;
};

//will be loaded from calibration.txt
double ARC_ERR=6.6902;
int IMG_X=1392;
int IMG_Y=1040;
double ARC_PER_PIX=15.7527;
double DEG_X=6.0774;
double DEG_Y=4.54468;

//will be loaded from dbsize.txt
int PARAM1=406;
int PARAM2=407;
int PARAM3=409;
int NUMCONST=64140;


int i1_max=PARAM1/2;
int i2_max=PARAM2/2;
int i3_max=PARAM3/2;

//i1..3 = int(p1..3+1)/2


void *map;
struct constelation *starptr;
void initdb() {
    
    /* Open a file for writing.
     *  - Creating the file if it doesn't exist.
     *  - Truncating it to 0 size if it already exists. (not really needed)
     *
     * Note: "O_WRONLY" mode is not sufficient when mmaping.
     */
    
    const char *filepath = "beastdb.bin";

    int fd = open(filepath, O_RDWR | O_CREAT | O_TRUNC, (mode_t)0600);
    
    if (fd == -1)
    {
        perror("Error opening file for writing");
        exit(EXIT_FAILURE);
    }

    // Stretch the file size to the size of the (mmapped) array of char

    size_t mapsize = i1_max*i2_max*i3_max;
    size_t starptrsize = NUMCONST;
    size_t dbsize = mapsize*sizeof(void*) + starptrsize*sizeof(struct constelation);
    
    
    if (lseek(fd, dbsize-1, SEEK_SET) == -1)
    {
        close(fd);
        perror("Error calling lseek() to 'stretch' the file");
        exit(EXIT_FAILURE);
    }
    
    if (write(fd, "", 1) == -1)
    {
        close(fd);
        perror("Error writing last byte of the file");
        exit(EXIT_FAILURE);
    }
    

    // Now the file is ready to be mmapped.
    map = mmap(0, dbsize, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
    starptr=(struct constelation*)(map+mapsize*sizeof(void*));
    
    if (map == MAP_FAILED)
    {
        close(fd);
        perror("Error mmapping the file");
        exit(EXIT_FAILURE);
    }
    
    memset(map, 0, dbsize);
    // Write it now to disk
    if (msync(map, dbsize, MS_SYNC) == -1)
    {
        perror("Could not sync the file to disk");
    }
    
    // Don't forget to free the mmapped memory
    if (munmap(map, dbsize) == -1)
    {
        close(fd);
        perror("Error un-mmapping the file");
        exit(EXIT_FAILURE);
    }

    // Un-mmaping doesn't close the file, so we still need to do that.
    close(fd);
}

int main (int argc, char** argv) {
	//load the stardb
	initdb();
	
}

