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

class TimeRequest : public Request
{
    public:
        using Event = struct
        {
            std::string modelname;
            double time;
            std::string event;
        };

    public:
        TimeRequest(size_t index);
        virtual ~TimeRequest(void) override = default;

        size_t getIndex(void) const;

        void addEvent(std::string modelname, double time, std::string event);
        const std::list<Event> &getEvents(void) const;

    private:
        const size_t index;
        std::list<Event> events;
};

// Misc

class TimeRequestModifier : public RequestModifier
{
    public:
        TimeRequestModifier(const double &time);
        virtual ~TimeRequestModifier(void) override = default;
        virtual void modify(std::shared_ptr<Request> request,
                            const Model &modifier,
                            std::string event) override;

        size_t getPassed(void) const;

    private:
        const double &time;
        size_t passed;
};

#endif

