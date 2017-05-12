#include <iostream>
#include <complex>
#include <vector>       // vector
#include <stdlib.h>


class discrete_pdf {
	private:
		unsigned int sz;
		double mass;
		std::vector<std::complex<double> > f;
		//quick and dirty fft/ifft. 
		void FFT(bool ifft) {
			int N=f.size();
			//the log2(.) of N
			int log2n = 0; for(int k=N;k>>=1;log2n++);
			//r is i with the bit ordering reversed 
			std::complex<double> temp;
			for(int i = 0; i < N/2; i++) {
				int r = 0;
				for(int j = 0; j < log2n; j++) if(i & (1 << (log2n - (j+1)))) r |= 1 << j;
				//swap element r with element i
				temp=f[i];
				f[i]=f[r];
				f[r]=temp;
			}
			std::complex<double>* W = new std::complex<double>[N/2];
			W[0] = 1;
			
			//check if we are doing an inverse fft
			if(ifft) {
				W[1] = std::polar(1., 6.28318530717958647692 / N);
				for(int i = 0; i < N; i++) f[i]/=N;
			} else {
				W[1] = std::polar(1., -6.28318530717958647692 / N);
			}
			
			for(int i = 2; i < N / 2; i++) W[i] = W[i-1]*W[1];
			int n = 1;
			int a = N / 2;
			for(int j = 0; j < log2n; j++) {
				for(int i = 0; i < N; i++) {
					if(!(i & n)) {
						temp = W[(i * a) % (n * a)] * f[i + n];
						f[i + n] = f[i] - temp;
						f[i] += temp;
					}
				}
				n *= 2;
				a = a / 2;
			}
			delete [] W;
		}
	public:
		discrete_pdf() : sz(0),mass(0.0) {};
		unsigned int size() {return sz;}
		//Initializes the extra elements to zero
		void reserve(unsigned int i) {
			unsigned int power=(f.size()>1)?f.size():1;
			while(power < i) power*=2;
			f.resize(power,0.0);
		}
		void add(unsigned int i, double val) {
			if (i>=sz) {
				sz=i+1;
				reserve(sz);
			}
			mass+=val;
			f[i]+=val;
		}
		double lt(unsigned int i) {
			double sum=0;
			do {i--; sum+=f[i].real();} while(i>0);
			return sum;
		}
		double ge(unsigned int i) {
			double sum=0;
			while (i<sz) {sum+=f[i].real();i++;};
			return sum;
		}
		void normalize() {
			for (unsigned int i=0;i<sz;i++) f[i]/=mass;
			mass=1;
		}
		void operator*= (int x) {
			if (x>1) {
				mass=std::pow(mass,x);
				sz+=(sz-1)*(x-1);
				reserve(sz);
				FFT(false);
				unsigned int s=f.size();
				for (unsigned int i=0;i<s;i++) f[i]=std::pow(f[i],x);
				FFT(true);
				double sum=0;
				for(unsigned int i=0;i<s;i++) sum+=f[i].real();
				for(unsigned int i=0;i<s;i++) f[i]=f[i].real()*mass/sum;
			}
		}
		void operator+= (discrete_pdf& x) {
			mass*=x.mass;
			sz+=(x.sz-1);
			reserve(sz);
			discrete_pdf temp;
			temp=x;
			temp.reserve(sz);
			temp.FFT(false);
			FFT(false);
			unsigned int s=f.size();
			for(unsigned int i=0;i<s;i++) f[i]*=temp.f[i];
			FFT(true);
			double sum=0;
			for(unsigned int i=0;i<s;i++) sum+=f[i].real();
			for(unsigned int i=0;i<s;i++) f[i]=f[i].real()*mass/sum;
			
		}
		void operator= (discrete_pdf& x) {
			if (this!=&x) {
				mass=x.mass;
				sz=x.sz;
				f=x.f;
			}
		}
		void print() {
			for (unsigned int i=0;i<f.size();i++) std::cout<<f[i]<<" ";
			std::cout<<std::endl;
		}
};

int main() {
	discrete_pdf x,y;
	y.add(0,2);
	y.add(1,2);
	x.add(0,.5);
	x.add(1,.5);
	x*=2;
	x.print();std::cout<<x.lt(x.size())<<std::endl;
	x+=x;
	x.print();std::cout<<x.lt(x.size())<<std::endl;
	x*=2;
	x.print();std::cout<<x.lt(x.size())<<std::endl;
	x+=x;
	x.print();std::cout<<x.lt(x.size())<<std::endl;
	//x*=2;
	//x+=y;
	//x.print();
	//x.normalize();
	//x.print();
	//y=x;
	//y.print();
	//y+=x;
	//y+=x;
	//y.print();
	return 0;
}
