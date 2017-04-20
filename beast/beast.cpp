// lower_bound/upper_bound example
#include <iostream>     // cout
#include <sstream>
#include <fstream>
#include <algorithm>    // lower_bound, upper_bound, sort
#include <vector>       // vector
#include <math.h>       /* sqrt */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>	/* For O_RDWR */
#include <sys/mman.h>
#include "../catalog_gen/configuration.h"

#define PI           3.14159265358979323846  /* pi */

/* //mapping between px,py and x,y,z
 *
 * //px=(x/z)IMG_X/(2*tan(DEG_X*pi/(180*2)))
 * //py=(y/z)IMG_Y/(2*tan(DEG_Y*pi/(180*2)))
 *
 * //px=(x/z)IMG_X/(2*tan(DEG_X*pi/(180*2)))
 * //py=(y/z)IMG_Y/(2*tan(DEG_Y*pi/(180*2)))


 * //px-(IMG_X/2)=(x/z)IMG_X/(2*tan(DEG_X*pi/(180*2)))
 * //py-(IMG_Y/2)=(y/z)IMG_Y/(2*tan(DEG_Y*pi/(180*2)))
 *
 * j=(2*tan(DEG_X*pi/(180*2)))*px/IMG_X; //j=(x/z)
 * k=(y/z)=(2*tan(DEG_Y*pi/(180*2)))*py/IMG_Y; //k=y/z
 *
 * //(j^2+k^2+1)z^2=1
 * z=1/sqrt(j^2+k^2+1);
 * x=j*z;
 * y=k*z;
 */

//using namespace std;

namespace beast {
	struct constellation {
		int s[4];
		double p[6];
		int last;
	};

	struct star {
		double x;
		double y;
		double z;
		double mag;
		int starnum;
		int magnum;
		int hipid;
	};

	int *map,fd;
	struct constellation *starptr;
	int PARAM1,PARAM2,PARAM3,NUMCONST,IMG_X,IMG_Y;
	double DEG_X,DEG_Y,PIXX_TANGENT,PIXY_TANGENT,ARC_ERR;
	int i1_max,i2_max,i3_max;
	size_t mapsize,dbsize;

	void load_db() {
		//load config
		configuration::data config1;
		std::ifstream cfgfile1("../catalog_gen/calibration/dbsize.txt");
		cfgfile1 >> config1;
		cfgfile1.close();

		configuration::data config2;
		std::ifstream cfgfile2("../catalog_gen/calibration/calibration.txt");
		cfgfile2 >> config2;
		cfgfile2.close();


		PARAM1=atoi(config1["PARAM1"].c_str());
		PARAM2=atoi(config1["PARAM2"].c_str());
		PARAM3=atoi(config1["PARAM3"].c_str());
		NUMCONST=atoi(config1["NUMCONST"].c_str());

		IMG_X=atoi(config2["IMG_X"].c_str());
		IMG_Y=atoi(config2["IMG_Y"].c_str());
		DEG_X=atof(config2["DEG_X"].c_str());
		DEG_Y=atof(config2["DEG_Y"].c_str());
		ARC_ERR=atof(config2["ARC_ERR"].c_str());

		i1_max=PARAM1/2;
		i2_max=PARAM2/2;
		i3_max=PARAM3/2;

		mapsize = i1_max*i2_max*i3_max;
		dbsize = mapsize*sizeof(int) + NUMCONST*sizeof(struct constellation);

		/* Open a file for writing.
		 *  - Creating the file if it doesn't exist.
		 *  - Truncating it to 0 size if it already exists. (not really needed)
		 *
		 * Note: "O_WRONLY" mode is not sufficient when mmaping.
		 */

		const char *filepath = "../catalog_gen/beastdb.bin";
		fd = open(filepath, O_RDONLY);
		if (fd == -1) {
			perror("Error opening file for writing");
			exit(EXIT_FAILURE);
		}

		// Now the file is ready to be mmapped.

		map = (int*)mmap(NULL, dbsize, PROT_READ, MAP_SHARED | MAP_POPULATE, fd, 0);
		if (map == MAP_FAILED)
		{
			close(fd);
			perror("Error mmapping the file");
			exit(EXIT_FAILURE);
		}
		starptr=(struct constellation*)(&map[mapsize]);
	}
	void close_db() {
		// Don't forget to free the mmapped memory
		if (munmap(map, dbsize) == -1) {
				close(fd);
				perror("Error un-mmapping the file");
				exit(EXIT_FAILURE);
		}
		// Un-mmaping doesn't close the file, so we still need to do that.
		close(fd);
	}

	bool compare_mag (const star &s1, const star &s2) {return (s1.mag > s2.mag);}
	bool compare_starnum (const star &s1, const star &s2) {return (s1.starnum < s2.starnum);}
	class star_query {
	public:
		std::vector<star> stars;
		bool stars_found;
		long im_0,im_1,im_2,im_3;//ids of stars from image
		long db_0,db_1,db_2,db_3;//ids of stars from db
		long pilot;
		void __attribute__ ((used)) add_star(double px, double py, double mag) {
			star s;

			double j=2*tan(DEG_X*PI/(180*2))*px/IMG_X; //j=(x/z)
			double k=2*tan(DEG_Y*PI/(180*2))*py/IMG_Y; //k=y/z
			s.x=1./sqrt(j*j+k*k+1);
			s.y=j*s.x;
			s.z=k*s.x;
			s.mag=mag;
			s.starnum=stars.size();
			s.magnum=s.starnum;
			s.hipid=0;
			px=j*IMG_X/(2*tan(DEG_X*PI/(180*2)));
			py=k*IMG_Y/(2*tan(DEG_Y*PI/(180*2)));

			//insert into list sorted by magnitude
			for (;s.magnum>0&&compare_mag(s,stars[s.magnum-1]);s.magnum--);
			if (s.starnum==0) pilot=0;
			else if (s.magnum<=pilot) pilot++;
			stars.insert(stars.begin()+s.magnum,s);
		}
		void __attribute__ ((used)) sort_mag() {sort(stars.begin(), stars.end(), compare_mag);}
		void __attribute__ ((used)) sort_starnum() {sort(stars.begin(), stars.end(), compare_starnum);}
		bool __attribute__ ((used)) querydb(int a, int b, int c, int d) {
			im_0=-1;im_1=-1;im_2=-1;im_3=-1;
			db_0=-1;db_1=-1;db_2=-1;db_3=-1;
			double p0,p1,p2,p3,p4,p5;
			p0=(3600*180.0/PI)*acos(stars[a].x*stars[b].x+stars[a].y*stars[b].y+stars[a].z*stars[b].z);
			p1=(3600*180.0/PI)*acos(stars[a].x*stars[c].x+stars[a].y*stars[c].y+stars[a].z*stars[c].z);
			p2=(3600*180.0/PI)*acos(stars[a].x*stars[d].x+stars[a].y*stars[d].y+stars[a].z*stars[d].z);
			p3=(3600*180.0/PI)*acos(stars[b].x*stars[c].x+stars[b].y*stars[c].y+stars[b].z*stars[c].z);
			p4=(3600*180.0/PI)*acos(stars[b].x*stars[d].x+stars[b].y*stars[d].y+stars[b].z*stars[d].z);
			p5=(3600*180.0/PI)*acos(stars[c].x*stars[d].x+stars[c].y*stars[d].y+stars[c].z*stars[d].z);
			int i1=(int)(p0/ARC_ERR+.5)%PARAM1;i1=(i1/2)%i1_max;
			int i2=(int)(p1/ARC_ERR+.5)%PARAM2;i2=(i2/2)%i2_max;
			int i3=(int)(p2/ARC_ERR+.5)%PARAM3;i3=(i3/2)%i3_max;
			if (i1<0) i1+=i1_max;
			if (i2<0) i2+=i2_max;
			if (i3<0) i3+=i3_max;

			//check for matches
			for (int staridx=map[i1*i2_max*i3_max+i2*i3_max+i3];staridx!=-1;staridx=starptr[staridx].last) {
				if (starptr[staridx].p[0]<p0+ARC_ERR &&
					starptr[staridx].p[0]>p0-ARC_ERR &&
					starptr[staridx].p[1]<p1+ARC_ERR &&
					starptr[staridx].p[1]>p1-ARC_ERR &&
					starptr[staridx].p[2]<p2+ARC_ERR &&
					starptr[staridx].p[2]>p2-ARC_ERR &&
					starptr[staridx].p[3]<p3+ARC_ERR &&
					starptr[staridx].p[3]>p3-ARC_ERR &&
					starptr[staridx].p[4]<p4+ARC_ERR &&
					starptr[staridx].p[4]>p4-ARC_ERR &&
					starptr[staridx].p[5]<p5+ARC_ERR &&
					starptr[staridx].p[5]>p5-ARC_ERR) {
					im_0=stars[a].starnum;
					im_1=stars[b].starnum;
					im_2=stars[c].starnum;
					im_3=stars[d].starnum;
					db_0=starptr[staridx].s[0];
					db_1=starptr[staridx].s[1];
					db_2=starptr[staridx].s[2];
					db_3=starptr[staridx].s[3];
					stars_found = true;
					return true;
				}
			}
			return false;
		}
		void __attribute__ ((used)) search_all() {
			//search every possible combination of four stars in the list given
			for (int d=3;d<stars.size();d++)
			for (int c=2;c<d;c++)
			for (int b=1;b<c;b++)
			for (int a=0;a<b;a++) querydb(a,b,c,d);
		}
		bool __attribute__ ((used)) search_pilot() {
			//search only those combinations which contain the first star that was added
			int i,j,k,l;
			int max=stars.size();
			for (l=pilot+3; l<max;l++)
				for (k=pilot+2; k<l;k++)
					for (j=pilot+1;j<k;j++)
						if (querydb(pilot,j,k,l)) return true;
			if (pilot==0) return false;

			for (l=pilot+2; l<max;l++)
				for (k=pilot+1; k<l;k++)
					for (i=0;i<pilot;i++)
						if (querydb(i,pilot,k,l)) return true;
			if (pilot==1) return false;

			for (l=pilot+1; l<max;l++)
				for (j=1;j<pilot;j++)
					for (i=0;i<j;i++)
						if (querydb(i,j,pilot,l)) return true;
			if (pilot==2) return false;

			for (k=2; k<pilot;k++)
				for (j=1;j<k;j++)
					for (i=0;i<j;i++)
						if (querydb(i,j,k,pilot)) return true;
			return false;
		}
	};
}
int main (int argc, char** argv) {
	std::cout.precision(12);
	if (argc!=2){
		std::cout<<"Usage: ./beast xy_mag.txt"<<std::endl<<std::flush;
		exit(0);
	}
	beast::load_db();

	std::ifstream xy_mag(argv[1]);
	beast::star_query sq;
	while (!xy_mag.eof()) {
		double px,py,mag;
		std::string line;
		std::getline(xy_mag, line);
		if (line.empty()) continue;
		std::istringstream tmp(line);
		tmp>>px>>py>>mag;
		sq.add_star(px,py,mag);
	}
	//for (int i=0;i<stars.size();i++) std::cout<<stars[i].x<<" "<<stars[i].y<<" "<<stars[i].z<<" "<<stars[i].mag<<std::endl<<std::flush;
	//calculate constellations
	sq.search_all();

	//sq.search_pilot();
	beast::close_db();
}
