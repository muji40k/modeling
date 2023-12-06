#ifndef _UNIFORM_H_
#define _UNIFORM_H_

#include "random.h"

class UniformRandom : public Random
{
    public:
        UniformRandom(double min, double max);
        virtual ~UniformRandom(void) override = default;
        virtual double generate(void) override;

    private:
        const double min;
        const double rng;
};

#endif

