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

namespace rst {
	struct constellation {
		int s1;
		int s2;
		double p;
		int last;
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
		unsigned char old_s1;
		unsigned char old_s2;
		unsigned char new_s1;
		unsigned char new_s2;
		//id=new
		//value=old
		std::vector<int> id_map;
		std::vector<double> scores;
	};
	
	
	int IMG_X,IMG_Y,MAX_STARS,MAX_FALSE_STARS;
	double DEG_X,DEG_Y,PIXX_TANGENT,PIXY_TANGENT,ARC_ERR_REL,POS_VARIENCE_REL,IMAGE_VARIANCE,BRIGHT_THRESH,PROB_FALSE_STAR,MATCH_VALUE;
	
	void load_db() {
		configuration::data config2;
		std::ifstream cfgfile2("../catalog_gen/calibration/calibration.txt");
		cfgfile2 >> config2;
		cfgfile2.close();

		IMG_X=atoi(config2["IMG_X"].c_str());
		IMG_Y=atoi(config2["IMG_Y"].c_str());
		DEG_X=atof(config2["DEG_X"].c_str());
		DEG_Y=atof(config2["DEG_Y"].c_str());
		ARC_ERR_REL=atof(config2["ARC_ERR_REL"].c_str());
		POS_VARIENCE_REL=atof(config2["POS_VARIENCE_REL"].c_str());//sigma_r^2
		IMAGE_VARIANCE=atof(config2["IMAGE_VARIANCE"].c_str());//lambda
		BRIGHT_THRESH=atof(config2["BRIGHT_THRESH"].c_str());//mmin
		PROB_FALSE_STAR=atof(config2["PROB_FALSE_STAR"].c_str());//pfalse
		MAX_FALSE_STARS=atof(config2["MAX_FALSE_STARS"].c_str());//>10 is slow
		MAX_STARS=255;
		//uncomment for lost in space
		//MAX_STARS=std::min(MAX_FALSE_STARS+2,255);
		MATCH_VALUE=4*log(PROB_FALSE_STAR/(IMG_X*IMG_Y))+log(2*PI);//base
		PIXX_TANGENT=2*tan(DEG_X*PI/(180*2))/IMG_X;
		PIXY_TANGENT=2*tan(DEG_Y*PI/(180*2))/IMG_Y;
	}
	bool compare_mag (const star &s1, const star &s2) {return (s1.mag > s2.mag);}
	bool compare_totalscore (const constellation_score &cs1, const constellation_score &cs2) {return (cs1.totalscore > cs2.totalscore);}
	bool compare_starnum (const star &s1, const star &s2) {return (s1.starnum < s2.starnum);}
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
		int numconst;
		size_t mapsize,dbsize;
		int* map;
		
		unsigned char *img_mask;
		struct constellation *starptr;
		void __attribute__ ((used)) add_star(double px, double py, double mag, int newstar) {
			star s;

			double j=PIXX_TANGENT*px; //j=(y/x)
			double k=PIXY_TANGENT*py; //k=z/x
			s.x=1./sqrt(j*j+k*k+1);
			s.y=j*s.x;
			s.z=k*s.x;
			s.mag=mag;
			s.id=0;
			
			s.sigma_sq=POS_VARIENCE_REL+IMAGE_VARIANCE/mag;
			s.px=px;
			s.py=py;
			//insert into list sorted by magnitude
			if (newstar) {
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
				if(newstars.size()>(unsigned int)MAX_STARS) newstars.resize(MAX_STARS);
			} else {
				s.magnum=oldstars.size();
				if (s.magnum==0) addedoldstars=0;
				s.starnum=addedoldstars;
				addedoldstars++;
				oldstars.resize(s.magnum+1);
				while (s.magnum>0&&compare_mag(s,oldstars[s.magnum-1])){
					oldstars[s.magnum]=oldstars[s.magnum-1];
					oldstars[s.magnum].magnum++;
					s.magnum--;
				}
				oldstars[s.magnum]=s;
				if(oldstars.size()>(unsigned int)MAX_STARS) oldstars.resize(MAX_STARS);
			}
		}
		double __attribute__ ((used)) dist3(double x1,double x2,double y1,double y2,double z1,double z2) {
			double a=x1*y2 - x2*y1;
			double b=x1*z2 - x2*z1;
			double c=y1*z2 - y2*z1;
			return sqrt(a*a+b*b+c*c);
		}
		void __attribute__ ((used)) sort_mag() {
			sort(oldstars.begin(), oldstars.end(), compare_mag);
			sort(newstars.begin(), newstars.end(), compare_mag);
		}
		void __attribute__ ((used)) sort_starnum() {
			sort(oldstars.begin(), oldstars.end(), compare_starnum);
			sort(newstars.begin(), newstars.end(), compare_starnum);
		}
		void  __attribute__ ((used)) add_entry(int mapidx,int curr_const) {
			int *staridx;
			for (staridx=&map[mapidx];*staridx!=-1;staridx=&(starptr[*staridx].last));
			if (staridx!=&(starptr[curr_const].last)) *staridx=curr_const;
		}
		
		double __attribute__ ((used)) search_rel() {


			numoldstars=oldstars.size();
			numnewstars=newstars.size();
			numconst=(numoldstars*(numoldstars-1))/2;
			mapsize=((3600*(sqrt(DEG_X*DEG_X+DEG_Y*DEG_Y))/ARC_ERR_REL)+1);
			dbsize = mapsize*sizeof(int) + numconst*sizeof(struct constellation);
			
			//allocate space for constellations
			map = (int*)malloc(dbsize);
			memset(map, -1, dbsize);
			starptr=(struct constellation*)(&map[mapsize]);
			
			//generate constellations
			int mmi_l,mmi_m,mmi_h;
			int curr_const=0;
			for (int i=1;i<numoldstars;i++){
				for (int j=0;j<i;j++){
					starptr[curr_const].s1=j;
					starptr[curr_const].s2=i;
					starptr[curr_const].p=(3600*180.0/PI)*asin(dist3(oldstars[i].x,oldstars[j].x,oldstars[i].y,oldstars[j].y,oldstars[i].z,oldstars[j].z));
					mmi_l=(int)(starptr[curr_const].p/ARC_ERR_REL-1)%mapsize;
					mmi_m=(int)(starptr[curr_const].p/ARC_ERR_REL)%mapsize;
					mmi_h=(int)(starptr[curr_const].p/ARC_ERR_REL+1)%mapsize;
					if (mmi_l<0) mmi_l+=mapsize;
					if (mmi_m<0) mmi_m+=mapsize;
					if (mmi_h<0) mmi_h+=mapsize;
					
					add_entry(mmi_l,curr_const);
					add_entry(mmi_m,curr_const);
					add_entry(mmi_h,curr_const);
					curr_const++;
				}
			}
			
			//allocate space for image mask 
			img_mask = (unsigned char*)malloc(IMG_X*IMG_Y);
			memset(img_mask, 255, IMG_X*IMG_Y);
			
			//generate image mask
			for (int i=0;i<numnewstars;i++){
				//assume the dimmest possible star since we dont know the brightness of the other image
				double sigma_sq=newstars[i].sigma_sq+IMAGE_VARIANCE/BRIGHT_THRESH;//change for lost in space.
				double maxdist_sq=-sigma_sq*(log(sigma_sq)+MATCH_VALUE);
				double maxdist=sqrt(maxdist_sq);
				double px=newstars[i].px;
				double py=newstars[i].py;
				int xmin=std::max(-IMG_X/2.0,(px-maxdist));
				int xmax=std::min(IMG_X/2.0,px+maxdist+1);
				int ymin=std::max(-IMG_Y/2.0,(py-maxdist));
				int ymax=std::min(IMG_Y/2.0,(py+maxdist+1));
				for(int x=xmin;x<xmax;x++){
					for (int y=ymin;y<ymax;y++) {
						double a=(x+.5-px);
						double b=(y+.5-py);
						double score = (maxdist_sq-(a*a+b*b))/(2*sigma_sq);
						if (score>0) {
							unsigned char id=img_mask[(x+IMG_X/2)+(y+IMG_Y/2)*IMG_X];
							if (id!=255){
								double sigma_sq2=newstars[id].sigma_sq+IMAGE_VARIANCE/BRIGHT_THRESH;//change for lost in space.
								double maxdist_sq2=-sigma_sq2*(log(sigma_sq2)+MATCH_VALUE);
								double px2=newstars[id].px;
								double py2=newstars[id].py;
								double a2=(x+.5-px2);
								double b2=(y+.5-py2);
								double score2 = (maxdist_sq2-(a2*a2+b2*b2))/(2*sigma_sq2);
								if (score>score2) img_mask[(x+IMG_X/2)+(y+IMG_Y/2)*IMG_X]=i;
							} else {
								img_mask[(x+IMG_X/2)+(y+IMG_Y/2)*IMG_X]=i;
							}
						}
					}
				}
			}
			//use weighted triad
			double p;
			int mmi;
			c_scores.clear();
			for (int i=1;i<numnewstars;i++){
				for (int j=0;j<i;j++){
					p=(3600*180.0/PI)*asin(dist3(newstars[i].x,newstars[j].x,newstars[i].y,newstars[j].y,newstars[i].z,newstars[j].z));
					mmi=(int)(p/ARC_ERR_REL)%mapsize;
					if (mmi<0) mmi+=mapsize;
					for (int staridx=map[mmi];staridx!=-1;staridx=starptr[staridx].last) {
						if (fabs(starptr[staridx].p-p)<ARC_ERR_REL){
							c_scores.push_back(weighted_triad(starptr[staridx].s1,starptr[staridx].s2,j,i));
							c_scores.push_back(weighted_triad(starptr[staridx].s1,starptr[staridx].s2,i,j));
						}
					}
				}
			}
			
			sort(c_scores.begin(), c_scores.end(), compare_totalscore);
			//add up probabilities of all matches, excluding those which
			//are equivalent to the best match (S1==s1,S2=s2)
			double p_match=1.0;
			if (c_scores.size()>0) {
				//there is a horrifying bug here
				//allocating the vectors like this makes it go away somehow :-(
				for (int i=0;i<addednewstars;i++){
					winner_id_map.push_back(-1);
					winner_scores.push_back(0.0);
				}
				for(int n=0;n<numnewstars;n++) {
					int o=c_scores[0].id_map[n];
					if (o!=-1){
						winner_scores[newstars[n].starnum]=c_scores[0].scores[n];
						winner_id_map[newstars[n].starnum]=oldstars[o].starnum;
					}
					
				}
				
				double bestscore=c_scores[0].totalscore;
				unsigned char old_s1=c_scores[0].old_s1;
				unsigned char old_s2=c_scores[0].old_s2;
				unsigned char new_s1=c_scores[0].new_s1;
				unsigned char new_s2=c_scores[0].new_s2;
				
				for(unsigned int i=1;i<c_scores.size();i++) {
					if (c_scores[i].id_map[new_s1]!=old_s1&&c_scores[i].id_map[new_s2]!=old_s2){
						p_match+=exp(c_scores[i].totalscore-bestscore);
					}
				}
				p_match=1.0/p_match;

			} else {
				p_match=0.0;
			}
			free(img_mask);
			free(map);
			return p_match;
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
		//Perform triad method using both stars as pilot stars, and return the better of the two
		
		constellation_score __attribute__ ((used)) weighted_triad(unsigned char old_s1,unsigned char old_s2,unsigned char new_s1,unsigned char new_s2){
			//v=A*w
			double wa1=oldstars[old_s1].x,wa2=oldstars[old_s1].y,wa3=oldstars[old_s1].z;
			double wb1=oldstars[old_s2].x,wb2=oldstars[old_s2].y,wb3=oldstars[old_s2].z;
			double va1=newstars[new_s1].x,va2=newstars[new_s1].y,va3=newstars[new_s1].z;
			double vb1=newstars[new_s2].x,vb2=newstars[new_s2].y,vb3=newstars[new_s2].z;
			
			double wa=sqrt(wa1*wa1+wa2*wa2+wa3*wa3);
			double wb=sqrt(wb1*wb1+wb2*wb2+wb3*wb3);
			double va=sqrt(va1*va1+va2*va2+va3*va3);
			double vb=sqrt(vb1*vb1+vb2*vb2+vb3*vb3);
			
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
			
			//some of these are unused, but the compiler will remove them
			double A11=va1*wa1 + vaXvc1*waXwc1 + vc1*wc1;
			double A12=va1*wa2 + vaXvc1*waXwc2 + vc1*wc2;
			double A13=va1*wa3 + vaXvc1*waXwc3 + vc1*wc3;
			double A21=va2*wa1 + vaXvc2*waXwc1 + vc2*wc1;
			double A22=va2*wa2 + vaXvc2*waXwc2 + vc2*wc2;
			double A23=va2*wa3 + vaXvc2*waXwc3 + vc2*wc3;
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

			//some of these are unused, but the compiler will remove them
			double B11=vb1*wb1 + vbXvc1*wbXwc1 + vc1*wc1;
			double B12=vb1*wb2 + vbXvc1*wbXwc2 + vc1*wc2;
			double B13=vb1*wb3 + vbXvc1*wbXwc3 + vc1*wc3;
			double B21=vb2*wb1 + vbXvc2*wbXwc1 + vc2*wc1;
			double B22=vb2*wb2 + vbXvc2*wbXwc2 + vc2*wc2;
			double B23=vb2*wb3 + vbXvc2*wbXwc3 + vc2*wc3;
			double B31=vb3*wb1 + vbXvc3*wbXwc1 + vc3*wc1;
			double B32=vb3*wb2 + vbXvc3*wbXwc2 + vc3*wc2;
			double B33=vb3*wb3 + vbXvc3*wbXwc3 + vc3*wc3;
			
			//use weights based on magnitude
			//weighted triad
			double weightA=1.0/(POS_VARIENCE_REL+IMAGE_VARIANCE/oldstars[old_s1].mag+IMAGE_VARIANCE/newstars[new_s1].mag);
			double weightB=1.0/(POS_VARIENCE_REL+IMAGE_VARIANCE/oldstars[old_s2].mag+IMAGE_VARIANCE/newstars[new_s2].mag);
			//weightA=0;
			//weightB=1.0-weightA;
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
			
			double R11,R12,R13;
			double R21,R22,R23;
			double R31,R32,R33;
			
			R11=cy*cz;
			R12=cz*sx*sy - cx*sz;
			R13=sx*sz + cx*cz*sy;
			
			R21=cy*sz;
			R22=cx*cz + sx*sy*sz;
			R23=cx*sy*sz - cz*sx;
			
			R31=-sy;
			R32=cy*sx;
			R33=cx*cy;


			constellation_score cs;
			cs.old_s1=old_s1;
			cs.old_s2=old_s2;
			cs.new_s1=new_s1;
			cs.new_s2=new_s2;
			
			//cargo cult vector allocation (it makes valgrind shut up, don't question it)
			for (int i=0;i<numnewstars;i++){
				cs.id_map.push_back(-1);
				cs.scores.push_back(0.0);
			}

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
					double sigma_sq=newstars[n].sigma_sq+IMAGE_VARIANCE/oldstars[o].mag;
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
			return cs;
		}
	};
}
int main (int argc, char** argv) {
	std::cout.precision(12);
	if (argc!=3){
		std::cout<<"Usage: ./rst xy_mag_old.txt xy_mag_new.txt"<<std::endl<<std::flush;
		exit(0);
	}
	rst::load_db();
	rst::star_query sq;
	double px,py,mag;
	std::string line;

	std::ifstream xy_mag_old(argv[1]);
	while (!xy_mag_old.eof()) {
		std::getline(xy_mag_old, line);
		if (line.empty()) continue;
		std::istringstream tmp(line);
		tmp>>px>>py>>mag;
		sq.add_star(px,py,mag,0);	}

	std::ifstream xy_mag_new(argv[2]);
	while (!xy_mag_new.eof()) {
		std::getline(xy_mag_new, line);
		if (line.empty()) continue;
		std::istringstream tmp(line);
		tmp>>px>>py>>mag;
		sq.add_star(px,py,mag,1);
	}
	double p_match = sq.search_rel();
	std::cout<<"Best score: "<<sq.c_scores[0].totalscore<<std::endl;
	std::cout << "P match: " << p_match <<std::endl;
	for (int n=0;n<sq.winner_id_map.size();n++){
		std::cout << "Old id: " << sq.winner_id_map[n];
		std::cout << " New id: " << n;
		std::cout << " Score: " << sq.winner_scores[n] <<std::endl;
	}
}
