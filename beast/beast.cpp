// lower_bound/upper_bound example
#include <iostream>     // cout
#include <fstream>
#include <algorithm>    // lower_bound, upper_bound, sort
#include <vector>       // vector
#include "opencv2/imgproc/imgproc.hpp"
#include "opencv2/highgui/highgui.hpp"

using namespace std;
using namespace cv;

struct star {
	double ra;
	double decll;
	double mag;
};

struct starline {
	double dist;
	int s1;
	int s2;
};

struct sort_mag {
    bool operator() (star s1, star s2) { return (s1.mag > s2.mag);}
};
struct sort_dist {
    bool operator() (starline d1, starline d2) { return (dl.dist < d2.dist);}
};

int cat_lines=0;
int dist_lines=0;

vector<star> s, s_mini;
vector<starline> d,d_mini;

void initdb() {
	star s_temp;
	fstream cat_f("cat.txt", ios_base::in);
	while(cat_f>>s_temp.mag>>s_temp.ra>>s_temp.decll) {
		s.push_back(s_temp);
		cat_lines++;
	}
	starline d_temp;
	fstream dist_f("dist.txt", ios_base::in);
	while(dist_f>>d_temp.dist>>d_temp.s1>>d_temp.s2) {
		d.push_back(d_temp);
		dist_lines++;
	}
}
Mat src; Mat src_gray;
int thresh = 100;
int max_thresh = 255;


int main (int argc, char** argv) {
	//load the stardb
	initdb();
	//extract centroids
	/// Load source image and convert it to gray
	src = imread( argv[1], 1 );
	cvtColor( src, src_gray, CV_BGR2GRAY );
    	Mat canny_output;
	vector<vector<Point> > contours;
	vector<Vec4i> hierarchy;

	/// Detect edges using canny
	Canny( src_gray, canny_output, thresh, thresh*2, 3 );
	findContours( canny_output, contours, hierarchy, CV_RETR_TREE, CV_CHAIN_APPROX_SIMPLE, Point(0, 0) );

	/// Get the moments
	vector<Moments> mu(contours.size());
	vector<star> mc;
	mc.reserve(contours.size());
	double ppd=394/9.97;

		/*
		need to implement distortion correction before calculating 
		see http://mathworld.wolfram.com/GnomonicProjection.html
		
		[x,y,z] notation: v = [1,tan(fov_x/2)*(1-2*x/x_res),tan(fov_x/2)*(1-2*y/y_res)]
		v=norm(v)
		*/
	for( int i = 0; i < contours.size(); i++ ) {
		mu[i] = moments( contours[i], false );
		if(mu[i].m00>0.0) mc.push_back(star(mu[i].m10/(mu[i].m00*ppd),mu[i].m01/(mu[i].m00*p,mu[i].m00));
	}
	sort(mc.begin(), mc.end(), sort_mag());

	vector<starlines> mc;
	for( int i = 0; i < mc.size(); i++ ){
		for( int j = 0; j < i; j++ ) {
		}
	}
}
