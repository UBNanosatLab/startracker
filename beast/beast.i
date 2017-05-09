%module beast
%{
#include "beast.h"
%}
%include "beast.h"
%include "std_vector.i"

namespace std
{
	%template(VectorStars) vector<beast::star>;
	%template(VectorInts) vector<int>;
	%template(VectorDoubles) vector<double>;
}
