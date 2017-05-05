%module rst
%{
#include "rst.h"
%}
%include "rst.h"
%include "std_vector.i"

namespace std
{
	%template(VectorStars) vector<rst::star>;
	%template(VectorInts) vector<int>;
	%template(VectorDoubles) vector<double>;
}
