#include <iostream>	 // cout
#include <string>
#include <fstream>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>	/* For O_RDWR */
#include <sys/mman.h>
#include "configuration.h"


//using namespace std;
struct constellation {
	int s[4];
	double p[6];
	int last;
};
int *map;
struct constellation *starptr;

void add_entry(int mapidx,int curr_const) {
	int *staridx;
	for (staridx=&map[mapidx];*staridx!=-1;staridx=&(starptr[*staridx].last));
	if (staridx!=&(starptr[curr_const].last)) *staridx=curr_const;
}

int main (int argc, char** argv) {
	std::cout.precision(12);
	//load config
	configuration::data config1;
	std::ifstream cfgfile1("calibration/dbsize.txt");
	cfgfile1 >> config1;
	cfgfile1.close();
	
	configuration::data config2;
	std::ifstream cfgfile2("calibration/calibration.txt");
	cfgfile2 >> config2;
	cfgfile2.close();
	
	std::ifstream starline("info/starline.txt");
	
	int PARAM1=atoi(config1["PARAM1"].c_str());
	int PARAM2=atoi(config1["PARAM2"].c_str());
	int PARAM3=atoi(config1["PARAM3"].c_str());
	int NUMCONST=atoi(config1["NUMCONST"].c_str());
	double ARC_ERR=atof(config2["ARC_ERR"].c_str());

	int i1_max=PARAM1/2;
	int i2_max=PARAM2/2;
	int i3_max=PARAM3/2;

	size_t mapsize = i1_max*i2_max*i3_max;
	size_t dbsize = mapsize*sizeof(int) + NUMCONST*sizeof(struct constellation);
	
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
	if (map == MAP_FAILED)
	{
		close(fd);
		perror("Error mmapping the file");
		exit(EXIT_FAILURE);
	}
	starptr=(struct constellation*)(&map[mapsize]);
	memset(map, -1, dbsize);
	for (int curr_const=0;curr_const<NUMCONST;curr_const++){
		for (int i=0;i<6;i++) starline>>starptr[curr_const].p[i];
		for (int i=0;i<4;i++) starline>>starptr[curr_const].s[i];
		int i1=(int)(starptr[curr_const].p[0]/ARC_ERR+.5)%PARAM1;
		int i2=(int)(starptr[curr_const].p[1]/ARC_ERR+.5)%PARAM2;
		int i3=(int)(starptr[curr_const].p[2]/ARC_ERR+.5)%PARAM3;
		i1=i1/2+(i1&1);
		i2=i2/2+(i2&1);
		i3=i3/2+(i3&1);

		int i1_l=((i1-1)%i1_max);
		int i1_u=((i1)%i1_max);
		if (i1_l<0) i1_l+=i1_max;
		if (i1_u<0) i1_u+=i1_max;
		i1_l*=i2_max*i3_max;
		i1_u*=i2_max*i3_max;
		
		int i2_l=((i2-1)%i2_max);
		int i2_u=((i2)%i2_max);
		if (i2_l<0) i2_l+=i2_max;
		if (i2_u<0) i2_u+=i2_max;
		i2_l*=i3_max;
		i2_u*=i3_max;
		
		int i3_l=((i3-1)%i3_max);
		int i3_u=((i3)%i3_max);
		if (i3_l<0) i3_l+=i3_max;
		if (i3_u<0) i3_u+=i3_max;
		
		//std::cout<<i1_l/(i2_max*i3_max)<<" "<<i2_l/(i3_max)<<" "<<i3_l<<std::endl<<std::flush;
		//std::cout<<i1_u/(i2_max*i3_max)<<" "<<i2_l/(i3_max)<<" "<<i3_l<<std::endl<<std::flush;
		//std::cout<<i1_l/(i2_max*i3_max)<<" "<<i2_u/(i3_max)<<" "<<i3_l<<std::endl<<std::flush;
		//std::cout<<i1_u/(i2_max*i3_max)<<" "<<i2_u/(i3_max)<<" "<<i3_l<<std::endl<<std::flush;
		//std::cout<<i1_l/(i2_max*i3_max)<<" "<<i2_l/(i3_max)<<" "<<i3_u<<std::endl<<std::flush;
		//std::cout<<i1_u/(i2_max*i3_max)<<" "<<i2_l/(i3_max)<<" "<<i3_u<<std::endl<<std::flush;
		//std::cout<<i1_l/(i2_max*i3_max)<<" "<<i2_u/(i3_max)<<" "<<i3_u<<std::endl<<std::flush;
		//std::cout<<i1_u/(i2_max*i3_max)<<" "<<i2_u/(i3_max)<<" "<<i3_u<<std::endl<<std::flush;
		//std::cout<<"--"<<std::endl<<std::flush;
		
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

