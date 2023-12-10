#include "normal.h"

#include <cstdlib>
#include <ctime>
#include <stdexcept>

NormalRandom::NormalRandom(double mean, double sdev)
    : mean(mean), sdev(sdev)
{
    if (0 > sdev)
        throw std::logic_error("Negative standard deviation");

    std::srand(std::time(nullptr));
}

double NormalRandom::generate(void)
{
    double sum = 0;

    for (size_t i = 0;
         12 > i;
         i++, sum += (double)std::rand() / RAND_MAX);

    return this->mean + this->sdev * (sum - 6);
}

