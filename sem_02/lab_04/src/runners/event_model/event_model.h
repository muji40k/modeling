#ifndef _EVENT_MODEL_H_
#define _EVENT_MODEL_H_

#include "base.h"

class EventModel
{
    public:
        virtual ~EventModel(void) = default;
        virtual bool isActive(void) const = 0;
        virtual void event(void) = 0;
        virtual double nextEvent(void) const = 0;
        virtual void generateNextEvent(void) = 0;
        virtual void setModifier(std::shared_ptr<RequestModifier> modifier) = 0;
};

class EventRequest : public Request
{
    public:
        using Event = struct
        {
            std::string modelname;
            double time;
            std::string event;
        };

    public:
        EventRequest(size_t index);
        virtual ~EventRequest(void) override = default;

        size_t getIndex(void) const;

        void addEvent(std::string modelname, double time, std::string event);
        const std::list<Event> &getEvents(void) const;

    private:
        const size_t index;
        std::list<Event> events;
};

// Misc

class EventRequestModifier : public RequestModifier
{
    public:
        EventRequestModifier(const double &time);
        virtual ~EventRequestModifier(void) override = default;
        virtual void modify(std::shared_ptr<Request> request,
                            const Model &modifier,
                            std::string event) override;

        size_t getPassed(void) const;

    private:
        const double &time;
        size_t passed;
};

#endif

