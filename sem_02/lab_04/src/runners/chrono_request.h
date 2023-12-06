#ifndef _CHRONO_REQUEST_H_
#define _CHRONO_REQUEST_H_

#include "base.h"
#include "generator.h"

class ChronoRequest : public Request
{
    public:
        using Event = struct
        {
            std::string modelname;
            double time;
            std::string event;
        };

    public:
        ChronoRequest(size_t index);
        virtual ~ChronoRequest(void) override = default;

        size_t getIndex(void) const;

        void addEvent(std::string modelname, double time, std::string event);
        const std::list<Event> &getEvents(void) const;

    private:
        const size_t index;
        std::list<Event> events;
};

class ChronoRequestModifier : public RequestModifier
{
    public:
        virtual ~ChronoRequestModifier(void) override = default;
        virtual void modify(std::shared_ptr<Request> request,
                            const Model &modifier,
                            std::string event) override;
        void setTime(const double &time);

    private:
        const double *time = nullptr;
};

class ChronoModelRequestCreator : public RequestCreator
{
    public:
        virtual ~ChronoModelRequestCreator(void) override = default;
        virtual std::shared_ptr<Request> create(void) override;

    private:
        size_t current = 0;
};

#endif

