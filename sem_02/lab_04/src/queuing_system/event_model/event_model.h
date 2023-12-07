#ifndef _EVENT_MODEL_H_
#define _EVENT_MODEL_H_

#include "base.h"

class EventModel
{
    public:
        virtual ~EventModel(void) = default;
        virtual void event(void) = 0;
        virtual double nextEvent(void) const = 0;
        virtual void generateNextEvent(void) = 0;
        virtual void setModifier(std::shared_ptr<RequestModifier> modifier) = 0;
};

class EventRequestModifier
{
    public:
        virtual ~EventRequestModifier(void) = default;
        virtual void setTime(const double &time) = 0;
        virtual size_t getPassed(void) = 0;
        virtual std::shared_ptr<RequestModifier> getModifier(void) = 0;
};

#endif

