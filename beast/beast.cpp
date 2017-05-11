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
#include <assert.h>

#define PI           3.14159265358979323846  /* pi */
#define TWOPI        6.28318530717958647693

namespace beast {
	struct constellation {
		double p;
		int s1;
		int s2;
		int numstars;
		int staridx;
		int last;
		//pad to a multiple of 8 for 32/64 bit compatability
		int pad;
	};
	struct star {
		double x;
		double y;
		double z;
		double mag;
		int starnum;
		int magnum;
		int id;

		double sigma_sq;
		double px;
		double py;
	};
	
	struct  constellation_score {
		double totalscore;
		int oldid1;
		int oldid2;
		unsigned char newid1;
		unsigned char newid2;
		
		//Usage: id_map[newstar]=oldstar
		std::vector<int> id_map;
		std::vector<double> scores;
	};
	
	//SWIG complains about these pointers. They're fine.
	int *map;
	struct constellation *constptr;
	int *db_starids;
	struct star *starptr;
	
	int fd;
	size_t dbsize;
	int mapsize;
	

	int PARAM,NUMCONST,NUMSTARS,STARTABLE;
	
	int IMG_X,IMG_Y,MAX_STARS,MAX_FALSE_STARS;
	double DEG_X,DEG_Y,PIXX_TANGENT,PIXY_TANGENT;
	double ARC_ERR,ARC_ERR_REL,POS_VARIANCE,POS_VARIANCE_REL;
	double IMAGE_VARIANCE,BRIGHT_THRESH,PROB_FALSE_STAR,MATCH_VALUE;
	
	void load_db() {
		//load config
		configuration::data config2;
		std::ifstream cfgfile2("../catalog_gen/calibration/calibration.txt");
		cfgfile2 >> config2;
		cfgfile2.close();
		
		IMG_X=atoi(config2["IMG_X"].c_str());
		IMG_Y=atoi(config2["IMG_Y"].c_str());
		DEG_X=atof(config2["DEG_X"].c_str());
		DEG_Y=atof(config2["DEG_Y"].c_str());
		ARC_ERR=atof(config2["ARC_ERR"].c_str());
		ARC_ERR_REL=atof(config2["ARC_ERR_REL"].c_str());
		POS_VARIANCE=atof(config2["POS_VARIANCE"].c_str());//sigma_r^2
		POS_VARIANCE_REL=atof(config2["POS_VARIANCE_REL"].c_str());//sigma_r^2
		IMAGE_VARIANCE=atof(config2["IMAGE_VARIANCE"].c_str());//lambda
		BRIGHT_THRESH=atof(config2["BRIGHT_THRESH"].c_str());//mmin
		PROB_FALSE_STAR=atof(config2["PROB_FALSE_STAR"].c_str());//pfalse
		//need to do something with this for lost in space
		MAX_FALSE_STARS=atof(config2["MAX_FALSE_STARS"].c_str());//>10 is slow
		MATCH_VALUE=4*log(PROB_FALSE_STAR/(IMG_X*IMG_Y))+log(2*PI);//base
		PIXX_TANGENT=2*tan(DEG_X*PI/(180*2))/IMG_X;
		PIXY_TANGENT=2*tan(DEG_Y*PI/(180*2))/IMG_Y;
		
		configuration::data config1;
		std::ifstream cfgfile1("../catalog_gen/calibration/dbsize.txt");
		cfgfile1 >> config1;
		cfgfile1.close();
		
		PARAM=atoi(config1["PARAM"].c_str());
		
		NUMCONST=atoi(config1["NUMCONST"].c_str());
		NUMSTARS=atoi(config1["NUMSTARS"].c_str());
		STARTABLE=atoi(config1["STARTABLE"].c_str());
		
		mapsize=PARAM;
		int s_offset=mapsize*sizeof(int)+ NUMCONST*sizeof(struct constellation);
		dbsize = s_offset + STARTABLE*sizeof(int);
		
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
		constptr=(struct constellation*)(&map[mapsize]);
		db_starids=(int*)(&map[s_offset/sizeof(int)]);
		
		std::ifstream starline("../catalog_gen/calibration/stars.txt");
		starptr = (star*)malloc(NUMSTARS*sizeof(struct star));
		for(int i=0;i<NUMSTARS;i++){
			starline>>starptr[i].id;
			starptr[i].starnum=i;
			starline>>starptr[i].mag;
			starptr[i].mag=-starptr[i].mag;
			starline>>starptr[i].x;
			starline>>starptr[i].y;
			starline>>starptr[i].z;
		}
		starline.close();
	}
	
	void unload_db() {
		// Don't forget to free the mmapped memory
		if (munmap(map, dbsize) == -1) {
				close(fd);
				perror("Error un-mmapping the file");
				exit(EXIT_FAILURE);
		}
		// Un-mmaping doesn't close the file, so we still need to do that.
		close(fd);
		free(starptr);
	}
	bool compare_mag (const star &s1, const star &s2) {return (s1.mag > s2.mag);}
	bool compare_totalscore (const constellation_score &cs1, const constellation_score &cs2) {return (cs1.totalscore > cs2.totalscore);}
	class star_query {
	public:
		std::vector<star> oldstars;	
		std::vector<star> newstars;	
		std::vector<constellation_score> c_scores;	
		std::vector<double> winner_scores;
		//winner_id_map[new]=old
		std::vector<int>  winner_id_map;
		
		int numoldstars;
		int numnewstars;
		int addedoldstars;
		int addednewstars;
		int numconst_rel;
		size_t mapsize_rel,dbsize_rel;
		int* map_rel;
		
		unsigned char *img_mask;
		struct constellation *constptr_rel;
		//rotation matrix
		double R11,R12,R13;
		double R21,R22,R23;
		double R31,R32,R33;
		
		void __attribute__ ((used)) add_star(double px, double py, double mag) {
			star s;

			double j=PIXX_TANGENT*px; //j=(y/x)
			double k=PIXY_TANGENT*py; //k=z/x
			s.x=1./sqrt(j*j+k*k+1);
			s.y=j*s.x;
			s.z=k*s.x;
			s.mag=mag;
			s.id=-1;
			
			s.sigma_sq=IMAGE_VARIANCE/mag;
			s.px=px;
			s.py=py;
			//insert into list sorted by magnitude
			s.magnum=newstars.size();
			if (s.magnum==0) addednewstars=0;
			s.starnum=addednewstars;
			addednewstars++;
			newstars.resize(s.magnum+1);
			while (s.magnum>0&&compare_mag(s,newstars[s.magnum-1])){
				newstars[s.magnum]=newstars[s.magnum-1];
				newstars[s.magnum].magnum++;
				s.magnum--;
			}
			newstars[s.magnum]=s;
			if(newstars.size()>255) newstars.resize(255);
		}
		void __attribute__ ((used)) flip() {
				addedoldstars=addednewstars;
				oldstars=newstars;
				addednewstars=0;
				newstars.clear();
				c_scores.clear();
		}
		double __attribute__ ((used)) dist3(double x1,double x2,double y1,double y2,double z1,double z2) {
			double a=x1*y2 - x2*y1;
			double b=x1*z2 - x2*z1;
			double c=y1*z2 - y2*z1;
			return sqrt(a*a+b*b+c*c);
		}
		
		
		//see https://en.wikipedia.org/wiki/Triad_method
		//and http://nghiaho.com/?page_id=846
		//returns match results
		
		//Optimization for LIS:
		
		//when compiled, this section contains roughly 430 floating point operations
		//according to https://www.karlrupp.net/2016/02/gemm-and-stream-results-on-intel-edison/
		//we can perform >250 MFLOPS with doubles, and >500 MFLOPS with floats
		//assuming 250 stars per pair * 100 pairs per image ~ .05 seconds
		
		//tips to improve speed: 
		//reduce max stars (x2-4)
		//replace doubles with floats(where 7 digits are enough) (x2-4)
		//Perform triad method using both stars as pilot stars, and 
		//set the rotation matrix to the weighted interpolation of the two
		
		void __attribute__ ((used)) weighted_triad(star &old_s1,star &old_s2,star &new_s1,star &new_s2,double variance){
			//v=A*w
			double wa1=old_s1.x,wa2=old_s1.y,wa3=old_s1.z;
			double wb1=old_s2.x,wb2=old_s2.y,wb3=old_s2.z;
			double va1=new_s1.x,va2=new_s1.y,va3=new_s1.z;
			double vb1=new_s2.x,vb2=new_s2.y,vb3=new_s2.z;
			
			double wc1=wa2*wb3 - wa3*wb2;
			double wc2=wa3*wb1 - wa1*wb3;
			double wc3=wa1*wb2 - wa2*wb1;
			double wcnorm=sqrt(wc1*wc1+wc2*wc2+wc3*wc3);
			wc1/=wcnorm;
			wc2/=wcnorm;
			wc3/=wcnorm;
	
			double vc1=va2*vb3 - va3*vb2;
			double vc2=va3*vb1 - va1*vb3;
			double vc3=va1*vb2 - va2*vb1;
			double vcnorm=sqrt(vc1*vc1+vc2*vc2+vc3*vc3);
			vc1/=vcnorm;
			vc2/=vcnorm;
			vc3/=vcnorm;
			
			double vaXvc1=va2*vc3 - va3*vc2;
			double vaXvc2=va3*vc1 - va1*vc3;
			double vaXvc3=va1*vc2 - va2*vc1;

			double waXwc1=wa2*wc3 - wa3*wc2;
			double waXwc2=wa3*wc1 - wa1*wc3;
			double waXwc3=wa1*wc2 - wa2*wc1;
			
			//some of these are unused
			double A11=va1*wa1 + vaXvc1*waXwc1 + vc1*wc1;
			//double A12=va1*wa2 + vaXvc1*waXwc2 + vc1*wc2;
			//double A13=va1*wa3 + vaXvc1*waXwc3 + vc1*wc3;
			double A21=va2*wa1 + vaXvc2*waXwc1 + vc2*wc1;
			//double A22=va2*wa2 + vaXvc2*waXwc2 + vc2*wc2;
			//double A23=va2*wa3 + vaXvc2*waXwc3 + vc2*wc3;
			double A31=va3*wa1 + vaXvc3*waXwc1 + vc3*wc1;
			double A32=va3*wa2 + vaXvc3*waXwc2 + vc3*wc2;
			double A33=va3*wa3 + vaXvc3*waXwc3 + vc3*wc3;
			
			wc1=-wc1;
			wc2=-wc2;
			wc3=-wc3;
			
			vc1=-vc1;
			vc2=-vc2;
			vc3=-vc3;
			double vbXvc1=vb2*vc3 - vb3*vc2;
			double vbXvc2=vb3*vc1 - vb1*vc3;
			double vbXvc3=vb1*vc2 - vb2*vc1;
			
			double wbXwc1=wb2*wc3 - wb3*wc2;
			double wbXwc2=wb3*wc1 - wb1*wc3;
			double wbXwc3=wb1*wc2 - wb2*wc1;

			//some of these are unused
			double B11=vb1*wb1 + vbXvc1*wbXwc1 + vc1*wc1;
			//double B12=vb1*wb2 + vbXvc1*wbXwc2 + vc1*wc2;
			//double B13=vb1*wb3 + vbXvc1*wbXwc3 + vc1*wc3;
			double B21=vb2*wb1 + vbXvc2*wbXwc1 + vc2*wc1;
			//double B22=vb2*wb2 + vbXvc2*wbXwc2 + vc2*wc2;
			//double B23=vb2*wb3 + vbXvc2*wbXwc3 + vc2*wc3;
			double B31=vb3*wb1 + vbXvc3*wbXwc1 + vc3*wc1;
			double B32=vb3*wb2 + vbXvc3*wbXwc2 + vc3*wc2;
			double B33=vb3*wb3 + vbXvc3*wbXwc3 + vc3*wc3;
			
			//use weights based on magnitude
			//weighted triad
			double weightA=1.0/(variance+IMAGE_VARIANCE/new_s1.mag);
			double weightB=1.0/(variance+IMAGE_VARIANCE/new_s2.mag);

			double sumAB=weightA+weightB;
			weightA/=sumAB;
			weightB/=sumAB;
			
			double cz,sz,mz;
			double cy,sy,my;
			double cx,sx,mx;
			
			cz=weightA*A11+weightB*B11;
			sz=weightA*A21+weightB*B21;
			mz=sqrt(cz*cz+sz*sz);
			cz=cz/mz;
			sz=sz/mz;
			
			cy=weightA*sqrt(A32*A32+A33*A33)+weightB*sqrt(B32*B32+B33*B33);
			sy=-weightA*A31-weightB*B31;
			my=sqrt(cy*cy+sy*sy);
			cy=cy/my;
			sy=sy/my;
		    
			cx=weightA*A33+weightB*B33;
			sx=weightA*A32+weightB*B32;
			mx=sqrt(cx*cx+sx*sx);
			cx=cx/mx;
			sx=sx/mx;
			
			R11=cy*cz;
			R12=cz*sx*sy - cx*sz;
			R13=sx*sz + cx*cz*sy;
			
			R21=cy*sz;
			R22=cx*cz + sx*sy*sz;
			R23=cx*sy*sz - cz*sx;
			
			R31=-sy;
			R32=cy*sx;
			R33=cx*cy;
		}
		void __attribute__ ((used)) set_mask(int x,int y, int id, double score, double variance){
			if (score>0) {
				//has this pixel already been assigned to a different star?
				unsigned char id2=img_mask[(x+IMG_X/2)+(y+IMG_Y/2)*IMG_X];
				if (id2!=255){
					double sigma_sq2=newstars[id2].sigma_sq+variance;
					double maxdist_sq2=-sigma_sq2*(log(sigma_sq2)+MATCH_VALUE);
					double px2=newstars[id2].px;
					double py2=newstars[id2].py;
					double a2=(x+.5-px2);
					double b2=(y+.5-py2);
					double score2 = (maxdist_sq2-(a2*a2+b2*b2))/(2*sigma_sq2);
					if (score>score2){
						img_mask[(x+IMG_X/2)+(y+IMG_Y/2)*IMG_X]=id;
					}
				} else {
					img_mask[(x+IMG_X/2)+(y+IMG_Y/2)*IMG_X]=id;
				}
			}
		}

		void __attribute__ ((used)) add_score(constellation &db_const,unsigned char newid1,unsigned char newid2){
			constellation_score cs;
			cs.oldid1=db_const.s1;
			cs.oldid2=db_const.s2;
			cs.newid1=newid1;
			cs.newid2=newid2;
			
			cs.id_map.clear();
			cs.id_map.assign(numnewstars,-1);
			cs.scores.clear();
			cs.scores.assign(numnewstars,0.0);

			cs.totalscore=log(PROB_FALSE_STAR/(IMG_X*IMG_Y))*(2*numnewstars);
			int smax=db_const.staridx+db_const.numstars;
			for(int i=db_const.staridx;i<smax;i++){
				int o=db_starids[i];
				double x=starptr[o].x*R11+starptr[o].y*R12+starptr[o].z*R13;
				double y=starptr[o].x*R21+starptr[o].y*R22+starptr[o].z*R23;
				double z=starptr[o].x*R31+starptr[o].y*R32+starptr[o].z*R33;
				double px=y/(x*PIXX_TANGENT);
				double py=z/(x*PIXY_TANGENT);
				unsigned char n=255;
				
				if (fabs(2*px)<IMG_X && fabs(2*py)<IMG_Y)
					n=img_mask[(int)(px+IMG_X/2.0)+(int)(py+IMG_Y/2.0)*IMG_X];
				if (n!=255) {
					double sigma_sq=newstars[n].sigma_sq+POS_VARIANCE;
					double maxdist_sq=-sigma_sq*(log(sigma_sq)+MATCH_VALUE);
					double a=(px-newstars[n].px);
					double b=(py-newstars[n].py);
					double score = (maxdist_sq-(a*a+b*b))/(2*sigma_sq);
					//only match the closest star
					if (score>cs.scores[n]){
						cs.id_map[n]=o;
						cs.scores[n]=score;
					}
				}
			}
			for(int n=0;n<numnewstars;n++) cs.totalscore+=cs.scores[n];
			c_scores.push_back(cs);
		}
		void __attribute__ ((used)) add_score_rel(constellation &old_const,unsigned char newid1,unsigned char newid2){
			constellation_score cs;
			cs.oldid1=old_const.s1;
			cs.oldid2=old_const.s1;
			cs.newid1=newid1;
			cs.newid2=newid2;
			
			cs.id_map.clear();
			cs.id_map.assign(numnewstars,-1);
			cs.scores.clear();
			cs.scores.assign(numnewstars,0.0);

			cs.totalscore=log(PROB_FALSE_STAR/(IMG_X*IMG_Y))*(numoldstars+numnewstars);
			for(int o=0;o<numoldstars;o++){
				double x=oldstars[o].x*R11+oldstars[o].y*R12+oldstars[o].z*R13;
				double y=oldstars[o].x*R21+oldstars[o].y*R22+oldstars[o].z*R23;
				double z=oldstars[o].x*R31+oldstars[o].y*R32+oldstars[o].z*R33;
				double px=y/(x*PIXX_TANGENT);
				double py=z/(x*PIXY_TANGENT);
				unsigned char n=255;
				
				if (fabs(2*px)<IMG_X && fabs(2*py)<IMG_Y)
					n=img_mask[(int)(px+IMG_X/2.0)+(int)(py+IMG_Y/2.0)*IMG_X];
				if (n!=255) {
					double sigma_sq=newstars[n].sigma_sq+POS_VARIANCE_REL+IMAGE_VARIANCE/oldstars[o].mag;
					double maxdist_sq=-sigma_sq*(log(sigma_sq)+MATCH_VALUE);
					double a=(px-newstars[n].px);
					double b=(py-newstars[n].py);
					double score = (maxdist_sq-(a*a+b*b))/(2*sigma_sq);
					//only match the closest star
					if (score>cs.scores[n]){
						cs.id_map[n]=o;
						cs.scores[n]=score;
					}
				}
			}
			for(int n=0;n<numnewstars;n++) cs.totalscore+=cs.scores[n];
			c_scores.push_back(cs);
		}
		void  __attribute__ ((used)) add_entry_rel(int mapidx,int curr_const) {
			int *staridx;
			for (staridx=&map_rel[mapidx];*staridx!=-1;staridx=&(constptr_rel[*staridx].last));
			if (staridx!=&(constptr_rel[curr_const].last)) *staridx=curr_const;
		}

		double __attribute__ ((used)) search() {
			numnewstars=newstars.size();
			winner_id_map.clear();
			winner_id_map.assign(addednewstars,-1);
			winner_scores.clear();
			winner_scores.assign(addednewstars,0.0);
			
			//Do we have enough stars?
			if (NUMSTARS<2||numnewstars<2) return 0.0;

			//allocate space for image mask 
			img_mask = (unsigned char*)malloc(IMG_X*IMG_Y);
			memset(img_mask, 255, IMG_X*IMG_Y);
			
			//generate image mask
			for (int id=0;id<numnewstars;id++){
				//assume the dimmest possible star since we dont know the brightness of the other image
				double sigma_sq=newstars[id].sigma_sq+POS_VARIANCE;
				double maxdist_sq=-sigma_sq*(log(sigma_sq)+MATCH_VALUE);
				double maxdist=sqrt(maxdist_sq);
				int xmin=std::max(-IMG_X/2.0,(newstars[id].px-maxdist));
				int xmax=std::min(IMG_X/2.0,newstars[id].px+maxdist+1);
				int ymin=std::max(-IMG_Y/2.0,(newstars[id].py-maxdist));
				int ymax=std::min(IMG_Y/2.0,(newstars[id].py+maxdist+1));
				for(int x=xmin;x<xmax;x++) for (int y=ymin;y<ymax;y++) {
					double a=(x+.5-newstars[id].px);
					double b=(y+.5-newstars[id].py);
					set_mask(x,y,id,(maxdist_sq-(a*a+b*b))/(2*sigma_sq),POS_VARIANCE);
				}
			}
			//use weighted triad
			c_scores.clear();
			for (int i=1;i<numnewstars&&i<MAX_FALSE_STARS+2;i++) {
				for (int j=0;j<i;j++) {
					double p=(3600*180.0/PI)*asin(dist3(newstars[i].x,newstars[j].x,newstars[i].y,newstars[j].y,newstars[i].z,newstars[j].z));
					int mmi=(int)(p/ARC_ERR)%mapsize;
					if (mmi<0) mmi+=mapsize;
					for (int constidx=map[mmi];constidx!=-1;constidx=constptr[constidx].last) {
						if (fabs(constptr[constidx].p-p)<ARC_ERR){
							weighted_triad(starptr[constptr[constidx].s1],starptr[constptr[constidx].s2],newstars[j],newstars[i],POS_VARIANCE);
							add_score(constptr[constidx],j,i);
							weighted_triad(starptr[constptr[constidx].s1],starptr[constptr[constidx].s2],newstars[i],newstars[j],POS_VARIANCE);
							add_score(constptr[constidx],i,j);
						}
					}
				}
			}
			
			sort(c_scores.begin(), c_scores.end(), compare_totalscore);
			//add up probabilities of all matches, excluding those which
			//are equivalent to the best match (S1==s1,S2=s2)
			double p_match=1.0;
			if (c_scores.size()>0) {
				for(int n=0;n<numnewstars;n++) {
					int o=c_scores[0].id_map[n];
					if (o!=-1){
						winner_scores[newstars[n].starnum]=c_scores[0].scores[n];
						winner_id_map[newstars[n].starnum]=starptr[o].id;
					}
				}
				
				double bestscore=c_scores[0].totalscore;
				int oldid1=c_scores[0].oldid1;
				int oldid2=c_scores[0].oldid2;
				unsigned char newid1=c_scores[0].newid1;
				unsigned char newid2=c_scores[0].newid2;
				//set attitude matrix to best match
				weighted_triad(starptr[oldid1],starptr[oldid2],newstars[newid1],newstars[newid2],POS_VARIANCE);
				for(unsigned int i=1;i<c_scores.size();i++) {
					if (c_scores[i].id_map[newid1]!=oldid1&&c_scores[i].id_map[newid2]!=oldid2){
						p_match+=exp(c_scores[i].totalscore-bestscore);
					}
				}
				p_match=1.0/p_match;

			} else {
				p_match=0.0;
			}
			free(img_mask);
			return p_match;
		}
		double __attribute__ ((used)) search_rel() {
			numoldstars=oldstars.size();
			numnewstars=newstars.size();
			
			winner_id_map.clear();
			winner_id_map.assign(addednewstars,-1);
			winner_scores.clear();
			winner_scores.assign(addednewstars,0.0);
			
			//do we have enough stars?
			if (numoldstars<2||numnewstars<2) return 0.0;
			
			numconst_rel=(numoldstars*(numoldstars-1))/2;
			mapsize_rel=((3600*(sqrt(DEG_X*DEG_X+DEG_Y*DEG_Y))/ARC_ERR_REL)+1);
			dbsize_rel = mapsize_rel*sizeof(int) + numconst_rel*sizeof(struct constellation);
			
			//allocate space for constellations
			map_rel = (int*)malloc(dbsize_rel);
			memset(map_rel, -1, dbsize_rel);
			constptr_rel=(struct constellation*)(&map_rel[mapsize_rel]);
			
			//generate constellations
			int mmi_l,mmi_m,mmi_h;
			int curr_const=0;
			for (int i=1;i<numoldstars;i++){
				for (int j=0;j<i;j++){
					constptr_rel[curr_const].s1=j;
					constptr_rel[curr_const].s2=i;
					constptr_rel[curr_const].p=(3600*180.0/PI)*asin(dist3(oldstars[i].x,oldstars[j].x,oldstars[i].y,oldstars[j].y,oldstars[i].z,oldstars[j].z));
					mmi_l=(int)(constptr_rel[curr_const].p/ARC_ERR_REL-1)%mapsize_rel;
					mmi_m=(int)(constptr_rel[curr_const].p/ARC_ERR_REL)%mapsize_rel;
					mmi_h=(int)(constptr_rel[curr_const].p/ARC_ERR_REL+1)%mapsize_rel;
					if (mmi_l<0) mmi_l+=mapsize_rel;
					if (mmi_m<0) mmi_m+=mapsize_rel;
					if (mmi_h<0) mmi_h+=mapsize_rel;
					
					add_entry_rel(mmi_l,curr_const);
					add_entry_rel(mmi_m,curr_const);
					add_entry_rel(mmi_h,curr_const);
					curr_const++;
				}
			}
			
			//allocate space for image mask 
			img_mask = (unsigned char*)malloc(IMG_X*IMG_Y);
			memset(img_mask, 255, IMG_X*IMG_Y);
			
			//generate image mask
			for (int id=0;id<numnewstars;id++){
				//assume the dimmest possible star since we dont know the brightness of the other image
				double sigma_sq=newstars[id].sigma_sq+POS_VARIANCE_REL+IMAGE_VARIANCE/BRIGHT_THRESH;
				double maxdist_sq=-sigma_sq*(log(sigma_sq)+MATCH_VALUE);
				double maxdist=sqrt(maxdist_sq);
				int xmin=std::max(-IMG_X/2.0,(newstars[id].px-maxdist));
				int xmax=std::min(IMG_X/2.0,newstars[id].px+maxdist+1);
				int ymin=std::max(-IMG_Y/2.0,(newstars[id].py-maxdist));
				int ymax=std::min(IMG_Y/2.0,(newstars[id].py+maxdist+1));
				for(int x=xmin;x<xmax;x++) for (int y=ymin;y<ymax;y++) {
					double a=(x+.5-newstars[id].px);
					double b=(y+.5-newstars[id].py);
					set_mask(x,y,id,(maxdist_sq-(a*a+b*b))/(2*sigma_sq),POS_VARIANCE_REL+IMAGE_VARIANCE/BRIGHT_THRESH);
				}
			}
			//use weighted triad
			c_scores.clear();
			for (int i=1;i<numnewstars&&i<MAX_FALSE_STARS+2;i++){
				for (int j=0;j<i;j++){
					double p=(3600*180.0/PI)*asin(dist3(newstars[i].x,newstars[j].x,newstars[i].y,newstars[j].y,newstars[i].z,newstars[j].z));
					int mmi=(int)(p/ARC_ERR_REL)%mapsize_rel;
					if (mmi<0) mmi+=mapsize_rel;
					for (int constidx=map_rel[mmi];constidx!=-1;constidx=constptr_rel[constidx].last) {
						if (fabs(constptr_rel[constidx].p-p)<ARC_ERR_REL){
							weighted_triad(oldstars[constptr_rel[constidx].s1],oldstars[constptr_rel[constidx].s2],newstars[j],newstars[i],POS_VARIANCE_REL);
							add_score_rel(constptr_rel[constidx],j,i);
							weighted_triad(oldstars[constptr_rel[constidx].s1],oldstars[constptr_rel[constidx].s2],newstars[i],newstars[j],POS_VARIANCE_REL);
							add_score_rel(constptr_rel[constidx],i,j);
						}
					}
				}
			}
			
			sort(c_scores.begin(), c_scores.end(), compare_totalscore);
			//add up probabilities of all matches, excluding those which
			//are equivalent to the best match (S1==s1,S2=s2)
			double p_match=1.0;
			if (c_scores.size()>0) {
				for(int n=0;n<numnewstars;n++) {
					int o=c_scores[0].id_map[n];
					if (o!=-1){
						winner_scores[newstars[n].starnum]=c_scores[0].scores[n];
						winner_id_map[newstars[n].starnum]=oldstars[o].starnum;
					}
				}
				
				double bestscore=c_scores[0].totalscore;
				int oldid1=c_scores[0].oldid1;
				int oldid2=c_scores[0].oldid2;
				unsigned char newid1=c_scores[0].newid1;
				unsigned char newid2=c_scores[0].newid2;
				//set attitude matrix to best match
				weighted_triad(starptr[oldid1],starptr[oldid2],newstars[newid1],newstars[newid2],POS_VARIANCE);
				
				for(unsigned int i=1;i<c_scores.size();i++) {
					if (c_scores[i].id_map[newid1]!=oldid1&&c_scores[i].id_map[newid2]!=oldid2){
						p_match+=exp(c_scores[i].totalscore-bestscore);
					}
				}
				p_match=1.0/p_match;

			} else {
				p_match=0.0;
			}
			free(img_mask);
			free(map_rel);
			return p_match;
		}
	};
}
int main (int argc, char** argv) {
	std::cout.precision(12);
	if (argc<4){
		std::cout<<"Usage: ./beast xy_mag_*.txt"<<std::endl<<std::flush;
		exit(0);
	}
	beast::load_db();
	beast::star_query sq;
	double px,py,mag;
	std::string line;
	
	std::ifstream xy_mag;
	for (int i=1;i<argc;i++){
		sq.flip();
		xy_mag.open(argv[i]);
		while (!xy_mag.eof()) {
			std::getline(xy_mag, line);
			if (line.empty()) continue;
			std::istringstream tmp(line);
			tmp>>px>>py>>mag;
			sq.add_star(px,py,mag);	
		}
		xy_mag.close();
		double p_match = sq.search();
		std::cout<<"New image: "<<argv[i]<<std::endl;
		if (sq.c_scores.size()>0) {
			std::cout<<"Best score: "<<sq.c_scores[0].totalscore<<std::endl;
		}
		std::cout << "P match: " << p_match <<std::endl;
		for (unsigned int n=0;n<sq.winner_id_map.size();n++){
			std::cout << "Old id: " << sq.winner_id_map[n];
			std::cout << " New id: " << n;
			std::cout << " Score: " << sq.winner_scores[n] <<std::endl;
		}
		p_match = sq.search_rel();
		std::cout<<"New image: "<<argv[i]<<std::endl;
		if (sq.c_scores.size()>0) {
			std::cout<<"Best score: "<<sq.c_scores[0].totalscore<<std::endl;
		}
		std::cout << "P match: " << p_match <<std::endl;
		for (unsigned int n=0;n<sq.winner_id_map.size();n++){
			std::cout << "Old id: " << sq.winner_id_map[n];
			std::cout << " New id: " << n;
			std::cout << " Score: " << sq.winner_scores[n] <<std::endl;
		}
	}
	beast::unload_db();
}
