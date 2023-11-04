#include <iostream>
#include <filesystem>
#include <vector>
#include <string>
#include <sstream>
#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include <gsl/gsl_sf_legendre.h>

#define N       10000
//#define tol     0.002
#define PI      3.1415924

namespace fs = std::filesystem;

// Función que obtiene una lista de archivos con la extensión ".xy" en un directorio específico
std::vector<std::string> get_xy_files(const std::string& directorio) {
    std::vector<std::string> xy_files;

    for (const auto& entry : fs::directory_iterator(directorio)) {
        if (entry.is_regular_file() && entry.path().extension() == ".xy") {
            xy_files.push_back(entry.path().filename());
        }
    }

    return xy_files;
}

std::string fout_name(const std::string& name) {
    std::stringstream test(name);
    std::string fname, tmp;
    std::getline(test, fname, '.');
    tmp = "q6_" + fname + ".dat";
    return tmp;
}

void make_q6_file(const std::string& file_name, const double tol) {
    FILE        *pf, *qf;
    float       r[N][2], rad[N], dist, f, delta;
    float       flo1, count;
    int         conf, ent1, ent2, nn;
    char        let1, let2;
    double      P0, P1, P2, P3, P4, P5, P6, Q, x, y, phi;
    double      Q0r,Q0i,Q1r,Q1i,Q2r,Q2i,Q3r,Q3i,Q4r,Q4i,Q5r,Q5i,Q6r,Q6i;
    double      zero=0.0;

    P0=gsl_sf_legendre_sphPlm(6, 0, zero);
    P1=gsl_sf_legendre_sphPlm(6, 1, zero);
    P2=gsl_sf_legendre_sphPlm(6, 2, zero);
    P3=gsl_sf_legendre_sphPlm(6, 3, zero);
    P4=gsl_sf_legendre_sphPlm(6, 4, zero);
    P5=gsl_sf_legendre_sphPlm(6, 5, zero);
    P6=gsl_sf_legendre_sphPlm(6, 6, zero);

    std::string fout = fout_name(file_name);
    pf = fopen(file_name.c_str(), "rb");
    qf = fopen(fout.c_str(), "wb");

    for(int n = 0; n < N; n++){
        fscanf(pf, "%d %d %f %f %f %d\n", &ent1, &ent2, &r[n][0], &r[n][1], &rad[n], &ent1);
    }

    for(int i = 0; i < N; i++){
        Q0r=0.0;Q0i=0.0;Q1r=0.0;Q1i=0.0;Q2r=0.0;Q2i=0.0;
        Q3r=0.0;Q3i=0.0;Q4r=0.0;Q4i=0.0;Q5r=0.0;Q5i=0.0;Q6r=0.0;Q6i=0.0;
        nn=0;
        for(int j=0; j < N; j++){
             if (i!=j){
                   x=r[j][0]-r[i][0];
                   y=r[j][1]-r[i][1];
                   dist=sqrt(x*x+y*y);
                   delta = rad[i]+rad[j] - dist;  
                   if(delta >= -tol) {
                    nn=nn+1;
                    phi=atan2(y,x);
                    Q0r=Q0r+cos(0.0*phi); Q0i=Q0i+sin(0.0*phi);
                    Q1r=Q1r+cos(1.0*phi); Q1i=Q1i+sin(1.0*phi);
                    Q2r=Q2r+cos(2.0*phi); Q2i=Q2i+sin(2.0*phi);
                    Q3r=Q3r+cos(3.0*phi); Q3i=Q3i+sin(3.0*phi);
                    Q4r=Q4r+cos(4.0*phi); Q4i=Q4i+sin(4.0*phi);
                    Q5r=Q5r+cos(5.0*phi); Q5i=Q5i+sin(5.0*phi);
                    Q6r=Q6r+cos(6.0*phi); Q6i=Q6i+sin(6.0*phi);
                   }
             }
        }
        if (nn>0) {
             nn=nn*nn;
             Q=P0*P0*(Q0r*Q0r+Q0i*Q0i)/nn +
               2.0*P1*P1*(Q1r*Q1r+Q1i*Q1i)/nn +
               2.0*P2*P2*(Q2r*Q2r+Q2i*Q2i)/nn +
               2.0*P3*P3*(Q3r*Q3r+Q3i*Q3i)/nn +
               2.0*P4*P4*(Q4r*Q4r+Q4i*Q4i)/nn +
               2.0*P5*P5*(Q5r*Q5r+Q5i*Q5i)/nn +
               2.0*P6*P6*(Q6r*Q6r+Q6i*Q6i)/nn;
             Q=sqrt(4.0*PI*Q/13);
             fprintf(qf,"%d %f %f %f %f\n", N-i, r[i][0], r[i][1], rad[i], Q);
        }
    }
}



int main(int argc, char* argv[]) {
    if (argc == 1) {
        std::cout << "\nUso: \n" << "\t./do_q6_files x.x\n" 
            << "\tx.x: tolerancia en el contacto (en m)\n" << std::endl; 
        return 0;
    }
    double tol;
    if (argc >= 2) {
        tol = std::stod(argv[1]);        
    }
    std::string directorio = "."; // Directorio local

    std::vector<std::string> xy_files = get_xy_files(directorio);

    if (xy_files.empty()) {
        std::cout << "No se encontraron archivos con la extensión \".xy\" en el directorio." << std::endl;
    } else {
        std::cout << "Archivos con la extensión \".xy\": " << xy_files.size() << std::endl;
        for (const std::string& archivo : xy_files) {
            std::cout << archivo << std::endl;
            make_q6_file(archivo, tol);
        }
    }
    
    return 0;
}

