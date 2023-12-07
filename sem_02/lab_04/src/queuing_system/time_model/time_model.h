#ifndef _TIME_MODEL_H_
#define _TIME_MODEL_H_

#include "base.h"

class TimeModel
{
    public:
        virtual ~TimeModel(void) = default;
        virtual size_t priority(void) = 0;
        virtual void tick(double time) = 0;
        virtual void setModifier(std::shared_ptr<RequestModifier> modifier) = 0;
};

class TimeRequestModifier
{
    public:
        virtual ~TimeRequestModifier(void) = default;
        virtual void setTime(const double &time) = 0;
        virtual size_t getPassed(void) = 0;
        virtual std::shared_ptr<RequestModifier> getModifier(void) = 0;
};

#endif

