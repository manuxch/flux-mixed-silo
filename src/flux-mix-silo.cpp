/** \mainpage flux-mix-silo.cpp
 * \brief Simulación de descarga de un silo simple.
 * 
 * Programa que implementa la biblioteca Box2D para simular la
 * descarga de un silo simple conteniendo una mezcla dematerial 
 * granular de diferentes tamañpos.
 *
 * \author Manuel Carlevaro <manuel@iflysib.unlp.edu.ar>
 *
 * \version 1.3 
 *
 * \date 2023.06.23
 *
 * */


#include <iostream>
using namespace std;
#include <box2d/box2d.h>
#include "globalSetup.hpp"
#include <string>
#include <cmath>
#include <vector>
using std::sin; using std::cos; using std::fabs; using std::sqrt;
#include <iomanip>
#include <sstream>
#include <cstdlib>
using std::exit;
#include "siloAux.hpp"
#include "random.hpp"

#define PI 3.1415926
int32 rayCastHit;

class MyRayCastCallback : public b2RayCastCallback {
    float ReportFixture(b2Fixture* fixture, const b2Vec2& point, 
            const b2Vec2& normal, float fraction) {
        rayCastHit = 1;
        return 0;
    }
};

int main(int argc, char *argv[])
{
    cout << "# flux-mix-silo" << endl;
    cout << "# v1.3 [2023.08.20]" << endl;
    string inputParFile(argv[1]);
    GlobalSetup *globalSetup = new GlobalSetup(inputParFile);
    RandomGenerator rng(globalSetup->randomSeed);
    string folder_cmd = "mkdir -p frames_"+globalSetup->dirID;
    int sysret = system(folder_cmd.c_str());
    cout << "# Creación de directorio de frames: " << (sysret ? "NOK." : "OK.") 
        << endl;
    cout << "# Creación del sistema ..." << endl;

    // Para encontrar el arco que forma el atasco:
    MyRayCastCallback* callback = new MyRayCastCallback;

    // Definición del mundo
    b2Vec2 gravedad(0.0f, globalSetup->g);
    b2World world(gravedad); // Llenado con el silo vertical
    cout << "#\t- Objeto mundo creado." << endl;
    
    // Definición del contenedor
    b2BodyDef bd;
    bd.position.Set(0.0f, 0.0f);
    bd.type = b2_staticBody;
    BodyData *siloD = new BodyData;
    siloD->isGrain = false;
    siloD->nLados = 5;
    siloD->gID = -100;
    bd.userData.pointer = uintptr_t(siloD);
    b2Body *silo = world.CreateBody(&bd);
    b2Vec2 wall_poly[6];
    wall_poly[0].Set(-globalSetup->caja.r, 0.0f);
    wall_poly[1].Set(-globalSetup->caja.R, 0.0f);
    wall_poly[2].Set(-globalSetup->caja.R, globalSetup->caja.H); 
    wall_poly[3].Set(globalSetup->caja.R, globalSetup->caja.H);
    wall_poly[4].Set(globalSetup->caja.R, 0.0);
    wall_poly[5].Set(globalSetup->caja.r, 0.0);

    b2ChainShape siloShape_poly;
    siloShape_poly.CreateChain(wall_poly, 6, wall_poly[0], wall_poly[5]);
    b2FixtureDef silo_fix;
    silo_fix.shape = &siloShape_poly;
    silo_fix.density = 0.0f;
    silo_fix.friction = globalSetup->caja.fric;
    silo->CreateFixture(&silo_fix);

    cout << "#\t- Silo creado." << endl;

    // Tapa	
    b2BodyDef tapa_piso;
    tapa_piso.position.Set(0.0f, 0.0f);
    tapa_piso.type = b2_staticBody;
    BodyData *tapaP = new BodyData;
    tapaP->isGrain = false;
    tapaP->nLados = 1;
    tapaP->gID = -110;
    tapa_piso.userData.pointer = uintptr_t(tapaP);
    b2Body *tapa_P = world.CreateBody(&tapa_piso);
    b2Vec2 v1(-globalSetup->caja.r, 0.0f);
    b2Vec2 v2(globalSetup->caja.r, 0.0f); 
    b2EdgeShape tapa_p_f;
    tapa_p_f.SetTwoSided(v1, v2);
    b2FixtureDef tapa_p_Fix;
    tapa_p_Fix.shape = &tapa_p_f;
    tapa_p_Fix.density = 0.0f;
    tapa_p_Fix.friction = globalSetup->caja.fric;
    tapa_P->CreateFixture(&tapa_p_Fix);
    cout << "#\t- Tapa piso creada." << endl;
   
    // Generación de granos.
    float siloInf,siloSup,siloIzq,siloDer,x,y;
    float maxRadio = 0.0f;
    for (int i = 0; i < globalSetup->noTipoGranos; ++i) {
        if (globalSetup->granos[i]->radio > maxRadio) 
            maxRadio = globalSetup->granos[i]->radio;
    }
    float mg = 0.0;
    int noTotGranos = 0;
    siloInf = 2.7f * maxRadio;
    siloSup = globalSetup->caja.H - 2.1f * maxRadio;
    siloIzq = -globalSetup->caja.R + 2.1f * maxRadio;
    siloDer = globalSetup->caja.R - 2.1f * maxRadio;

    BodyData **gInfo;
    gInfo = new BodyData*[globalSetup->noTipoGranos];
    
    int contGid = 1;
    int *sumaTipo = new int[globalSetup->noTipoGranos] {};

    for (int i = 0; i < globalSetup->noTipoGranos; i++) { // Loop sobre tipos 
        gInfo[i] = new BodyData[globalSetup->granos[i]->noGranos]; // de granos
        for (int j = 0; j < globalSetup->granos[i]->noGranos; j++) { // Loop 
            // sobre el número de granos de cada tipo.
            x = rng.getAB(siloIzq, siloDer);
            y = rng.getAB(siloInf,siloSup);
            gInfo[i][j].tipo = i;
            gInfo[i][j].isGrain = true;
            gInfo[i][j].isIn = true;
            gInfo[i][j].nLados = globalSetup->granos[i]->nLados;
            gInfo[i][j].gID = contGid++;
            b2BodyDef bd;
            bd.type = b2_dynamicBody;
            bd.allowSleep = true;
            bd.bullet = globalSetup->isBullet;
            bd.position.Set(x,y);
            bd.angle = rng.getAB(-b2_pi,b2_pi);
            bd.userData.pointer = uintptr_t(&gInfo[i][j]);
            b2Body* grain = world.CreateBody(&bd);
            if (globalSetup->granos[i]->nLados == 1) {
                b2CircleShape circle;
                circle.m_radius = globalSetup->granos[i]->radio;
                b2FixtureDef fixDef;
                fixDef.shape = &circle;
                fixDef.density = globalSetup->granos[i]->dens;
                fixDef.friction = globalSetup->granos[i]->fric;
                fixDef.restitution = globalSetup->granos[i]->rest;
                grain->CreateFixture(&fixDef);
                mg += grain->GetMass();
                if (j == 0) cout << "#\t- Grano de tipo " << i 
                    << " creado con masa " << grain->GetMass() 
                        << " kg." << endl;
            }
            else {
                b2PolygonShape poly;
                int32 vertexCount = globalSetup->granos[i]->nLados;
                b2Vec2 vertices[8];
                for (int k = 0; k < globalSetup->granos[i]->nLados; k++) 
                    vertices[k].Set(globalSetup->granos[i]->vertices[k][0],
                            globalSetup->granos[i]->vertices[k][1]);
                poly.Set(vertices,vertexCount);
                b2FixtureDef fixDef;
                fixDef.shape = &poly;
                fixDef.density = globalSetup->granos[i]->dens;
                fixDef.friction = globalSetup->granos[i]->fric;
                fixDef.restitution = globalSetup->granos[i]->rest;
                grain->CreateFixture(&fixDef);
                mg += grain->GetMass();
                if (j == 0) cout << "#\t- Grano de tipo " << i + 1 
                    << " creado con masa " << grain->GetMass() 
                        << " kg." << endl;
            }
            noTotGranos++;
        } // Fin loop sobre el número de granos de cada tipo.
    } // Fin loop sobre tipo de granos	
    cout << "#\t- Número total de granos = " << noTotGranos << endl;
    cout << "#\t- Masa total de granos = " << mg << " kg."<< endl;
    float maxDistReiny = globalSetup->caja.r + 4.0f * maxRadio * 2.0f; // r + 4 diámetros de granos
    cout << "#\t- Límite de reinyección/eliminación = " << maxDistReiny << " m." << endl;
    float maxDistReiny_2 = maxDistReiny * maxDistReiny;

    // Preparamos los parámetros de la simulación. 
    float timeStep = globalSetup->tStep;
    float timeS = 0.0;
    int32 pIterations = globalSetup->pIter;
    int32 vIterations = globalSetup->vIter;

    cout << "# Inicio de la simulación..." << endl;
    b2Vec2 pos; 
    float angle = 0.0, dist_out_2;
    int nGranosDesc = 0;
    BodyData *infGr;
    int deltaG = 0;

    // Llenado del silo y decantación
    bool saveFrm = (globalSetup->saveFrameFreq > 0 ? true : false);
    bool saveFlux = (globalSetup->fluxFreq > 0 ? true : false);
    bool save_Q6 = (globalSetup->q6_freq > 0 ? true : false);
    bool saveForces = (globalSetup->saveContactFreq > 0 ? true : false);
    bool saveVE = (globalSetup->veFreq > 0 ? true : false);
    bool saveCF;
    int paso = 0;
    bool t_fill = (globalSetup->tFill > globalSetup->tStep ? true : false);
    // El tiempo de llenado funciona si los granos no son bullets
    cout << "# Llenado del silo y decantación... ";
    if (t_fill) cout << "(tiempo de espera " << globalSetup->tFill << " s.)" << endl;
    else cout << "(hasta el reposo)." << endl;
    do {
        world.Step(timeStep, pIterations, vIterations);
        timeS += timeStep;
        // Si es necesario, guardo el frame para graficar
         if (saveFrm && !(paso % globalSetup->saveFrameFreq)) {
             saveFrame(&world, paso, globalSetup);
         }
        paso++;
        if(t_fill && timeS > globalSetup->tFill) break;
        if(!t_fill && timeS > globalSetup->tMax) {
            cout << "Tiempo de llenado mayor que tiempo máximo de simulación. Fin." << endl;
            exit(1);
        }
    } while(isActive(&world));

    cout << "# ... tiempo de llenado (" << timeS << " s) finalizado en " << paso << " pasos." << endl;
    //saveFrame(&world, paso, globalSetup);

    for (b2Body *bd = world.GetBodyList(); bd; bd = bd->GetNext()) {
        bd->SetAwake(true);
    }
                                
    //paso = 0;
    //saveFrame(&world, paso, globalSetup);
    float x_salida = 0.0f;
    float y_salida = 0.0f;
    world.DestroyBody(tapa_P);
    tapa_P = NULL;

    cout << "# Tapa removida, inicio de la descarga." << endl; 
    timeS = 0.0f;
    paso++;
    
    std::ofstream fileFlux, fileVE;
    if (saveFlux) {
        fileFlux.open((globalSetup->fluxFile).c_str());
        fileFlux << "#grainDesc type time ";
        for (int i = 0; i < globalSetup->noTipoGranos; ++i) {
            fileFlux << "totalType_" << i + 1 << " ";
        }
        fileFlux << " Total" << endl;
    }
    // Guardo configuración inicial
    saveFrame(&world, paso, globalSetup);
    cout << "# Frame inicial " << paso << " guardado en " << timeS << endl;

    int forceFrame = 0; /*!< Contador de frames de fuerzas de contacto */

    // Inicio el avance del tiempo en la simulación
    bool tMax_restrain = true;
    if (!globalSetup->reinyect) 
        tMax_restrain = (globalSetup->tMax > globalSetup->tStep ? true : false);

    do {
        // Si hay reinyección controlo no superar el tiempo máximo de 
        // simulación
        if (tMax_restrain && timeS > globalSetup->tMax) {
            cout << "# Máximo tiempo de simulación alcanzado." << endl;
            break;
            // tMax_reached = true;
        }

        // Si es el momento guardo las fuerzas de contacto
        if (saveForces && timeS >= globalSetup->tStartCF && timeS <= globalSetup->tEndCF) {
            saveCF = true;
        }
        else saveCF = false;

        // Guardado de información de contacto
        if (saveCF && !(paso % globalSetup->saveContactFreq)) {
            forceFrame++;
            // Guardo info de las fuerzas de contacto
            saveContacts(&world, globalSetup->tStep, forceFrame, globalSetup);
            // Guardo info de los granos
            savePart(&world, forceFrame, globalSetup);
        }
        
        // Cálculo y guardado de Q6
        if (save_Q6 && !(paso % globalSetup->q6_freq)) {
            saveQ6(&world, paso, globalSetup);
        }

        // Cálculo y guardado de velocidades y energías
        if (saveVE && !(paso % globalSetup->veFreq)) {
            printVE(paso, timeS, &world, globalSetup);
        }
        // Cálculo de descarga y reinyección
        deltaG = countDesc(&world, sumaTipo, paso, fileFlux, globalSetup);
        nGranosDesc += deltaG;

        b2Body* bd = world.GetBodyList();
        //bd = world.GetBodyList();
        while(bd){
            b2Body* b = bd;
            bd = bd->GetNext();
            infGr = (BodyData*)b->GetUserData().pointer;
            if(!infGr->isGrain) continue;
            if(infGr->isIn) continue;
            pos = b->GetPosition();
            dist_out_2 = (pos.x - x_salida) * (pos.x - x_salida) + 
                       (pos.y - y_salida) * (pos.y - y_salida);
            if (dist_out_2 < maxDistReiny_2) continue;
            if(globalSetup->reinyect) {
                angle = b->GetAngle();
                b2Fixture* f = b->GetFixtureList();
                b2Shape* bs = (b2Shape*) f->GetShape();
                float radio = bs->m_radius;
                x = rng.getAB(siloIzq + radio, siloDer - radio);
                y = rng.getAB(0.75 * globalSetup->caja.H, 
                              0.95 * globalSetup->caja.H);
                b2Vec2 newPos(x,y);
                b->SetTransform(newPos, angle);
                infGr->isIn = true;
            }
            else {
                world.DestroyBody(b);
            }
        }

        world.Step(timeStep,pIterations,vIterations);
        paso++;
        timeS += timeStep;
        //cout << "paso: " << paso << " time: " << timeS << endl;

        // Si es necesario, guardo el frame para graficar
        if (saveFrm && !(paso % globalSetup->saveFrameFreq)) {
            saveFrame(&world, paso, globalSetup);
        }
    }
    while (paso < 10 || isActive(&world));

    cout << "Descarga final: " << nGranosDesc << endl;
    for (int i = 0; i < globalSetup->noTipoGranos; ++i){
        cout << "Granos de tipo " << i + 1 << ": " << sumaTipo[i] << endl;
    }
    cout << "Simulación finalizada." << endl;

    
    // Clean up
    if (saveFlux) fileFlux.close();
    delete globalSetup;
    delete siloD;
    delete [] gInfo;
    delete [] sumaTipo;
    delete callback;

    return 0;
}	

