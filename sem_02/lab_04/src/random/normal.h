#ifndef _NORMAL_H_
#define _NORMAL_H_

#include "random.h"

class NormalRandom : public Random
{
    public:
        NormalRandom(double mean, double sdev);
        virtual ~NormalRandom(void) override = default;
        virtual double generate(void) override;

    private:
        const double mean;
        const double sdev;
};

#endif

