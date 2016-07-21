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
	int last;
};
int *map;
struct constelation *starptr;

void add_entry(int mapidx,int curr_const) {
	int *staridx;
	for (staridx=&map[mapidx];(*staridx)!=-1;staridx=&(starptr[*staridx].last));
	*staridx=curr_const;
}

double ARC_ERR;
int PARAM1,PARAM2,PARAM3,NUMCONST;
int i1_max,i2_max,i3_max;

//i1..3 = int(p1..3+1)/2


int main (int argc, char** argv) {
	//load the stardb
    if (argc!=6){
        cout<<"Usage: ./beastgen PARAM1 PARAM2 PARAM3 NUMCONST ARC_PER_PIX < info/starline.txt"<<endl;
        exit(0);
    }
    int PARAM1=atoi(argv[1]);
    int PARAM2=atoi(argv[2]);
    int PARAM3=atoi(argv[3]);
    int NUMCONST=atoi(argv[4]);
    int ARC_ERR=atof(argv[5]);

    int i1_max=PARAM1/2;
    int i2_max=PARAM2/2;
    int i3_max=PARAM3/2;

    size_t mapsize = i1_max*i2_max*i3_max;
    size_t starptrsize = NUMCONST;
    size_t dbsize = mapsize*sizeof(void*) + starptrsize*sizeof(struct constelation);
    
    /* Open a file for writing.
     *  - Creating the file if it doesn't exist.
     *  - Truncating it to 0 size if it already exists. (not really needed)
     *
     * Note: "O_WRONLY" mode is not sufficient when mmaping.
     */

    const char *filepath = "beastdb.bin";
    int fd = open(filepath, O_RDWR | O_CREAT | O_TRUNC, (mode_t)0600);
    if (fd == -1) {
        perror("Error opening file for writing");
        exit(EXIT_FAILURE);
    }

    // Stretch the file size to the size of the (mmapped) array of char


    if (lseek(fd, dbsize-1, SEEK_SET) == -1) {
        close(fd);
        perror("Error calling lseek() to 'stretch' the file");
        exit(EXIT_FAILURE);
    }
    
    if (write(fd, "", 1) == -1) {
        close(fd);
        perror("Error writing last byte of the file");
        exit(EXIT_FAILURE);
    }
    

    // Now the file is ready to be mmapped.

    map = (int*)mmap(0, dbsize, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
    starptr=(struct constelation*)(map+mapsize*sizeof(void*));

    
    if (map == MAP_FAILED)
    {
        close(fd);
        perror("Error mmapping the file");
        exit(EXIT_FAILURE);
    }
    memset(map, -1, dbsize);
    
    for (int curr_const=0;curr_const<NUMCONST;curr_const++){
	for (int i=0;i<6;i++) cin>>starptr[curr_const].p[i];
	for (int i=0;i<4;i++) cin>>starptr[curr_const].s[i];
	int i1=(int)(starptr[curr_const].p[0]/ARC_ERR+.5)%PARAM1;i1=i1/2+i1&1;
	int i2=(int)(starptr[curr_const].p[1]/ARC_ERR+.5)%PARAM2;i2=i2/2+i2&1;
	int i3=(int)(starptr[curr_const].p[2]/ARC_ERR+.5)%PARAM3;i3=i3/2+i3&1;

    int i1_l=((i1-1)%i1_max)*i2_max*i3_max;
    int i1_u=((i1)%i1_max)*i2_max*i3_max;
    int i2_l=((i2-1)%i2_max)*i3_max;
    int i2_u=((i2)%i2_max)*i3_max;
    int i3_l=((i3-1)%i3_max);
    int i3_u=((i3)%i3_max);
        
    
    add_entry(i1_l+i2_l+i3_l,curr_const);
    add_entry(i1_u+i2_l+i3_l,curr_const);
    add_entry(i1_l+i2_u+i3_l,curr_const);
    add_entry(i1_u+i2_u+i3_l,curr_const);
    add_entry(i1_l+i2_l+i3_u,curr_const);
    add_entry(i1_u+i2_l+i3_u,curr_const);
    add_entry(i1_l+i2_u+i3_u,curr_const);
    add_entry(i1_u+i2_u+i3_u,curr_const);

    }
    
    
    // Write it now to disk
    if (msync(map, dbsize, MS_SYNC) == -1) {
        perror("Could not sync the file to disk");
    }
    
    // Don't forget to free the mmapped memory
    if (munmap(map, dbsize) == -1) {
        close(fd);
        perror("Error un-mmapping the file");
        exit(EXIT_FAILURE);
    }

    // Un-mmaping doesn't close the file, so we still need to do that.
    close(fd);
	
}

