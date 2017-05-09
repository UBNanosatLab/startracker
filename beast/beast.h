#include <vector>

namespace beast 
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
		int oldid1;
		int oldid2;
		unsigned char newid1;
		unsigned char newid2;
		
		//Usage: id_map[newstar]=oldstar
		std::vector<int> id_map;
		std::vector<double> scores;
	};
	
	//SWIG complains about these pointers. They're fine.
	extern int *map;
	extern struct constellation *constptr;
	extern int *db_starids;
	extern struct star *starptr;
	
	extern int fd;
	extern size_t dbsize;
	extern int mapsize;

    
	extern int PARAM, NUMCONST, NUMSTARS,STARTABLE;
    
	extern int IMG_X,IMG_Y,MAX_STARS,MAX_FALSE_STARS;
	extern double DEG_X,DEG_Y,PIXX_TANGENT,PIXY_TANGENT;
	extern double ARC_ERR,ARC_ERR_REL,POS_VARIANCE,POS_VARIANCE_REL;
	extern double IMAGE_VARIANCE,BRIGHT_THRESH,PROB_FALSE_STAR,MATCH_VALUE;
	
	void load_db();
	void unload_db();
	
	bool compare_mag (const star &s1, const star &s2);
	bool compare_totalscore (const constellation_score &cs1, const constellation_score &cs2);
	
	class star_query {
	public:
		std::vector<star> oldstars;	
		std::vector<star> newstars;	
		std::vector<constellation_score> c_scores;	
		std::vector<double> winner_scores;
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

		void add_star(double px, double py, double mag);
		void flip();
		double dist3(double x1,double x2,double y1,double y2,double z1,double z2);
		void add_entry_rel(int mapidx,int curr_const);
		void weighted_triad(star &old_s1,star &old_s2,star &new_s1,star &new_s2,double variance);
		void set_mask(int x, int y, int id, double score, double variance);
		void add_score(constellation &db_const,unsigned char newid1,unsigned char newid2);
		void add_score_rel(unsigned char oldid1,unsigned char oldid2,unsigned char newid1,unsigned char newid2);
		double search();
		double search_rel();
	};
}
