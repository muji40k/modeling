#ifndef _CONSTANT_H_
#define _CONSTANT_H_

#include "random.h"

class ConstantRandom : public Random
{
    public:
        ConstantRandom(double value);
        virtual ~ConstantRandom(void) override = default;
        virtual double generate(void) override;

    private:
        const double value;
};

#endif

