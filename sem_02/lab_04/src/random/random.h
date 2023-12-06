#ifndef _RANDOM_H_
#define _RANDOM_H_

class Random
{
    public:
        virtual ~Random(void) = default;
        virtual double generate(void) = 0;
};

#endif

