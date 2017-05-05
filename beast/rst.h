#include <vector>

namespace rst 
{
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
	
	
	extern int IMG_X,IMG_Y,MAX_STARS,MAX_FALSE_STARS;
	extern double DEG_X,DEG_Y,PIXX_TANGENT,PIXY_TANGENT,ARC_ERR_REL,POS_VARIENCE_REL,IMAGE_VARIANCE,BRIGHT_THRESH,PROB_FALSE_STAR,MATCH_VALUE;
	
	extern void load_db();
	
	extern bool compare_mag (const star &s1, const star &s2);
	extern bool compare_totalscore (const constellation_score &cs1, const constellation_score &cs2);
	extern bool compare_starnum (const star &s1, const star &s2);
	
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
		void add_star(double px, double py, double mag, int newstar);
		double dist3(double x1,double x2,double y1,double y2,double z1,double z2);
		void sort_mag();
		void sort_starnum();
		void add_entry(int mapidx,int curr_const);
		
		double search_rel();
		constellation_score weighted_triad(unsigned char old_s1,unsigned char old_s2,unsigned char new_s1,unsigned char new_s2);
	};
}
