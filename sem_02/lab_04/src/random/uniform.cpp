#include "uniform.h"

#include <cstdlib>
#include <ctime>

UniformRandom::UniformRandom(double min, double max)
    : min(min), rng(max - min)
{
    std::srand(std::time(nullptr));
}

double UniformRandom::generate(void)
{
    double val = (double)std::rand() / RAND_MAX;

    return this->min + val * this->rng;
}

