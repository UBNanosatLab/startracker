%module beast
%typemap(out) double *perform_search %{
  $result = PyList_New(8); // use however you know the size here
  for (int i = 0; i < 8; ++i) {
    PyList_SetItem($result, i, PyFloat_FromDouble($1[i]));
  }
  delete $1; // Important to avoid a leak since you called new
%}

%{
#include <vector>

namespace beast
{
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

	extern int *map, fd;
	extern struct constellation* starptr;
	extern int PARAM1,PARAM2,PARAM3,NUMCONST,IMG_X,IMG_Y;
	extern double DEG_X,DEG_Y,ARC_ERR;
	extern int i1_max,i2_max,i3_max;
	extern size_t mapsize,dbsize;

	extern void load_db();
	extern void close_db();

	extern bool compare_mag (const star &s1, const star &s2);
	extern bool compare_starnum (const star &s1, const star &s2);

	class star_query {
	public:
		std::vector<star> stars;
		int pilot;

		void add_star(double px, double py, double mag);
		void sort_mag();
		void sort_starnum();
		bool querydb(int a, int b, int c, int d);
		void search_all();
		bool search_pilot();
	};
	extern double* perform_search(std::vector<std::vector< double > >);
}

%}

%include "std_vector.i"

namespace std
{
	%template(VectorStars) vector<beast::star>;
	%template(Line) vector<double>;
		%template(Array) vector < vector < double> >;
}

namespace beast
{
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

	extern int *map, fd;
	extern struct constellation* starptr;
	extern int PARAM1,PARAM2,PARAM3,NUMCONST,IMG_X,IMG_Y;
	extern double DEG_X,DEG_Y,ARC_ERR;
	extern int i1_max,i2_max,i3_max;
	extern size_t mapsize,dbsize;

	extern void load_db();
	extern void close_db();

	extern bool compare_mag (const star &s1, const star &s2);
	extern bool compare_starnum (const star &s1, const star &s2);

	class star_query {
	public:
		std::vector<star> stars;
		int pilot;

		void add_star(double px, double py, double mag);
		void sort_mag();
		void sort_starnum();
		bool querydb(int a, int b, int c, int d);
		void search_all();
		bool search_pilot();
	};
	extern double* perform_search(std::vector<std::vector< double > >);
}
