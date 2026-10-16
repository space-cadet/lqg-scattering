// Classical linear rotors on a periodic ring. I=lambda=1.
#include <cmath>
#include <vector>
#include <random>
#include <algorithm>
using V=std::vector<double>;
static void kick(int n,double*q,double*j,double dt){
 for(int i=0;i<n;i++){
  int a=(i+n-1)%n,b=(i+1)%n;
  double x=q[3*a]+q[3*b],y=q[3*a+1]+q[3*b+1],z=q[3*a+2]+q[3*b+2];
  j[3*i]+=dt*(q[3*i+1]*z-q[3*i+2]*y);
  j[3*i+1]+=dt*(q[3*i+2]*x-q[3*i]*z);
  j[3*i+2]+=dt*(q[3*i]*y-q[3*i+1]*x);
 }
}
static void drift(int n,double*q,double*j,double dt){
 for(int i=0;i<n;i++){
  double *a=q+3*i,*b=j+3*i;
  double r=std::sqrt(b[0]*b[0]+b[1]*b[1]+b[2]*b[2]);
  if(r<1e-30)continue;
  double c=std::cos(r*dt),s=std::sin(r*dt)/r,d=(b[0]*a[0]+b[1]*a[1]+b[2]*a[2])*(1-c)/(r*r);
  double v[3]={c*a[0]+s*(b[1]*a[2]-b[2]*a[1])+d*b[0],c*a[1]+s*(b[2]*a[0]-b[0]*a[2])+d*b[1],c*a[2]+s*(b[0]*a[1]-b[1]*a[0])+d*b[2]};
  std::copy(v,v+3,a);
 }
}
static double potential(int n,const double*q){double e=0;for(int i=0;i<n;i++){int a=(i+1)%n;double d=0;for(int c=0;c<3;c++)d+=q[3*i+c]*q[3*a+c];e+=1-d;}return e;}
static void readout(int n,const double*q,const double*j,double*out){
 double e=potential(n,q),t=0,ss=0,hot=0,spread=0,jn[3]={0,0,0},len=0,tan=0;
 for(int i=0;i<n;i++){
  double ki=0,dp=0,dn=0,dot=0,norm=0;int a=(i+n-1)%n,b=(i+1)%n;
  for(int c=0;c<3;c++){ki+=.5*j[3*i+c]*j[3*i+c];dp+=q[3*i+c]*q[3*a+c];dn+=q[3*i+c]*q[3*b+c];jn[c]+=j[3*i+c];dot+=q[3*i+c]*j[3*i+c];norm+=q[3*i+c]*q[3*i+c];}
  double ei=ki+1-.5*(dp+dn);t+=ki;ss+=ei*ei;if(i<2)hot+=ei;
  int dist=std::min(std::min(i,(n-i)%n),std::min(std::abs(i-1),n-std::abs(i-1)));spread+=ei*dist*dist;
  len=std::max(len,std::abs(norm-1));tan=std::max(tan,std::abs(dot));out[8+i]=ei;
 }
 e+=t;out[0]=e;out[1]=t/e;out[2]=hot/e;out[3]=ss/(e*e);out[4]=spread/e;
 out[5]=std::sqrt(jn[0]*jn[0]+jn[1]*jn[1]+jn[2]*jn[2]);out[6]=len;out[7]=tan;
}
extern "C" void rotor_evolve(int n,double*q,double*j,double dt,int steps,int stride,double*out){
 int row=0;readout(n,q,j,out);row++;
 for(int s=1;s<=steps;s++){kick(n,q,j,dt*.5);drift(n,q,j,dt);kick(n,q,j,dt*.5);if(s%stride==0){readout(n,q,j,out+row*(8+n));row++;}}
}
static bool inverse_b(int n,const double*q,double*inv,double&det){
 double b[9]={0};for(int i=0;i<n;i++)for(int a=0;a<3;a++)for(int c=0;c<3;c++)b[3*a+c]+=(a==c?1.:0.)-q[3*i+a]*q[3*i+c];
 double a=b[0],d=b[1],e=b[2],f=b[4],g=b[5],h=b[8];
 det=a*(f*h-g*g)-d*(d*h-e*g)+e*(d*g-e*f);if(det<=1e-20)return false;
 double z[9]={f*h-g*g,e*g-d*h,d*g-e*f,e*g-d*h,a*h-e*e,d*e-a*g,d*g-e*f,d*e-a*g,a*f-d*d};for(int i=0;i<9;i++)inv[i]=z[i]/det;return true;
}
extern "C" double rotor_microcanonical(int n,double energy,double*q,unsigned long long seed,int burn,int samples,int thin,double*out){
 std::mt19937_64 rng(seed);std::normal_distribution<double> normal;std::uniform_real_distribution<double> uniform;
 double inv[9],det;inverse_b(n,q,inv,det);double v=potential(n,q);double logw=(n-2.5)*std::log(energy-v)-.5*std::log(det);
 double width=.25;long accepted=0,total=0,window_acc=0;int row=0;
 V j(3*n),u(3*n);int sweeps=burn+samples*thin;
 for(int sweep=0;sweep<sweeps;sweep++){
  for(int attempt=0;attempt<n;attempt++){
   int i=rng()%n;double old[3],r=0;for(int c=0;c<3;c++){old[c]=q[3*i+c];q[3*i+c]+=width*normal(rng);r+=q[3*i+c]*q[3*i+c];}r=std::sqrt(r);for(int c=0;c<3;c++)q[3*i+c]/=r;
   double nv=potential(n,q),nd,ni[9];bool valid=energy>nv && inverse_b(n,q,ni,nd);double nl=valid?(n-2.5)*std::log(energy-nv)-.5*std::log(nd):-INFINITY;
   total++;if(std::log(uniform(rng))<nl-logw){logw=nl;v=nv;accepted++;window_acc++;}else for(int c=0;c<3;c++)q[3*i+c]=old[c];
  }
  if(sweep<burn && (sweep+1)%100==0){double rate=window_acc/(100.*n);width*=rate>.5?1.15:(rate<.25?.85:1.);width=std::min(2.,std::max(.001,width));window_acc=0;}
  if(sweep>=burn && (sweep-burn+1)%thin==0){
   inverse_b(n,q,inv,det);double sum[3]={0,0,0};
   for(int i=0;i<n;i++){double d=0;for(int c=0;c<3;c++){u[3*i+c]=normal(rng);d+=u[3*i+c]*q[3*i+c];}for(int c=0;c<3;c++){u[3*i+c]-=d*q[3*i+c];sum[c]+=u[3*i+c];}}
   double a[3]={0,0,0};for(int c=0;c<3;c++)for(int d=0;d<3;d++)a[c]+=inv[3*c+d]*sum[d];double norm=0;
   for(int i=0;i<n;i++){double d=0;for(int c=0;c<3;c++)d+=q[3*i+c]*a[c];for(int c=0;c<3;c++){j[3*i+c]=u[3*i+c]-a[c]+d*q[3*i+c];norm+=j[3*i+c]*j[3*i+c];}}
   double scale=std::sqrt(2*(energy-v)/norm);for(double&x:j)x*=scale;
   readout(n,q,j.data(),out+row*(8+n));row++;
  }
 }
 return accepted/double(total);
}

// General graph evolution for few-rotor mechanisms. Each undirected edge occurs once.
static void graph_kick(int m,const int*edges,const double*w,double*q,double*j,double dt){
 for(int e=0;e<m;e++){
  int i=edges[2*e],k=edges[2*e+1];double *a=q+3*i,*b=q+3*k;
  double torque[3]={a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]};
  for(int c=0;c<3;c++){j[3*i+c]+=dt*w[e]*torque[c];j[3*k+c]-=dt*w[e]*torque[c];}
 }
}
extern "C" void rotor_graph_evolve(int n,int m,const int*edges,const double*w,double*q,double*j,double inertia,double dt,int steps,int stride,double*out){
 int row=0;
 auto save=[&](){std::copy(q,q+3*n,out+row*6*n);std::copy(j,j+3*n,out+row*6*n+3*n);row++;};save();
 for(int s=1;s<=steps;s++){graph_kick(m,edges,w,q,j,dt*.5);drift(n,q,j,dt/inertia);graph_kick(m,edges,w,q,j,dt*.5);if(s%stride==0)save();}
}

// Ring transfer readouts in physical units, with explicit coupling and inertia.
extern "C" void rotor_ring_transfer(int n,double*q,double*j,double coupling,double inertia,double dt,int steps,int stride,double*out){
 int row=0;
 auto save=[&](){
  double*o=out+row*(8+2*n);readout(n,q,j,o);
  // Reconstruct physical local energies; existing readout's geometric checks remain valid.
  double energy=0,kin=0,hot=0,ss=0;
  for(int i=0;i<n;i++){
   int a=(i+n-1)%n,b=(i+1)%n;double k=0,dp=0,dn=0;
   for(int c=0;c<3;c++){k+=j[3*i+c]*j[3*i+c]/(2*inertia);dp+=q[3*i+c]*q[3*a+c];dn+=q[3*i+c]*q[3*b+c];}
   double e=k+coupling*(1-.5*(dp+dn));o[8+i]=e;o[8+n+i]=k;energy+=e;kin+=k;ss+=e*e;if(i<2)hot+=e;
  }
  o[0]=energy;o[1]=kin/energy;o[2]=hot/energy;o[3]=ss/(energy*energy);
  // Column 4 is the kinetic energy outside the original pair, in physical units.
  o[4]=kin-o[8+n]-o[8+n+1];row++;
 };
 save();for(int s=1;s<=steps;s++){kick(n,q,j,dt*coupling*.5);drift(n,q,j,dt/inertia);kick(n,q,j,dt*coupling*.5);if(s%stride==0)save();}
}
