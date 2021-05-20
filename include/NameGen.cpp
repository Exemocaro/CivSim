#include <stdlib.h>
#include <iostream>
#include <stdio.h>
#include <time.h>
#include <ctype.h>
#include <string.h> //Needed for strcat()
// 2240 names

#ifndef NAMEGEN_CPP
#define NAMEGEN_CPP

using namespace std;

char namePrefix[][5] = {
"",
"bel",
"nar",
"xan",
"bell",
"natr",
"ev",
};

const char nameStems[][10] = {
"adur", "aes", "anim", "apoll", "imac",
"educ", "equis", "extr", "guius", "hann",
"equi", "amora", "hum", "iace", "ille",
"inept", "iuv", "obe", "ocul", "orbis"
};

char nameSuffix[][5] = {
"", "us", "ix", "ox", "ith",
"ath", "um", "ator", "or", "axia",
"imus", "ais", "itur", "orex", "o",
"y"
};

string nameGen()
{
    string n = "";
    srand((long)time(NULL)); //Seed the random number generator...
    n += namePrefix[(rand() % 7)];
    n += nameStems[(rand() % 20)];
    n += nameSuffix[(rand() % 16)];
    n[0] = toupper(n[0]);
    return n;
}

#endif