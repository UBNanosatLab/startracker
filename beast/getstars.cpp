// lower_bound/upper_bound example
#include <iostream>     // cout
#include <fstream>
#include <algorithm>    // lower_bound, upper_bound, sort
#include <vector>
#include <stdlib.h>
#include "opencv2/imgproc/imgproc.hpp"
#include "opencv2/highgui/highgui.hpp"
#include "../catalog_gen/configuration.h"

using namespace cv;

Mat src; Mat src_gray;
int center_x, center_y;
bool compare_center (const Point3f &s1, const Point3f &s2) {
	int s1x=(s1.x-center_x);
	int s1y=(s1.y-center_y);
	int s2x=(s2.x-center_x);
	int s2y=(s2.y-center_y);
	return (s1x*s1x+s1y*s1y) < (s2x*s2x+s2y*s2y);
}

int main (int argc, char** argv) {
	
	configuration::data config2;
	std::ifstream cfgfile2("../catalog_gen/calibration/calibration.txt");
	cfgfile2 >> config2;
	cfgfile2.close();

	center_x=atoi(config2["IMG_X"].c_str())/2;
	center_y=atoi(config2["IMG_Y"].c_str())/2;

	//extract centroids
	/// Load source image and convert it to gray
	if (argc!=3){
		std::cout<<"Usage: ./getstars stars.bmp [threshold<255]"<<std::endl<<std::flush;
		exit(0);
	}
	src = imread( argv[1], 1 );
	int thresh = atoi(argv[2]);
	cvtColor( src, src_gray, CV_BGR2GRAY );
    Mat canny_output;
	vector<vector<Point> > contours;
	vector<Vec4i> hierarchy;

	/// Detect edges using canny
	Canny( src_gray, canny_output, thresh, thresh*2, 3 );
	findContours( canny_output, contours, hierarchy, CV_RETR_TREE, CV_CHAIN_APPROX_SIMPLE, Point(0, 0) );

	/// Get the moments
	vector<Moments> mu(contours.size());
	vector<Point3f> mc;
	for( int i = 0; i < contours.size(); i++ ) {
		mu[i] = moments( contours[i], false );
		if (mu[i].m00>0) mc.push_back(Point3f(mu[i].m10/mu[i].m00,mu[i].m01/mu[i].m00,mu[i].m00));
	}
	sort(mc.begin(), mc.end(), compare_center);
	for (int i = 0;i<mc.size();i++) std::cout <<mc[i].x<<" "<<mc[i].y<<" "<<mc[i].z<<std::endl<<std::flush;
}

