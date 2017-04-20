%module beast
%{
#include "beast.h"

%}

%include "std_vector.i"

namespace std
{
	%template(VectorStars) vector<beast::star>;
	%template(Line) vector<double>;
		%template(Array) vector < vector < double> >;
}


%include "beast.h"
