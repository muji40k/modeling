#include "event_model.h"

#include "terminator.h"

EventRequest::EventRequest(size_t index) : index(index) {}

size_t EventRequest::getIndex(void) const
{
    return this->index;
}

void EventRequest::addEvent(std::string modelname, double time, std::string event)
{
    this->events.push_back({modelname, time, event});
}

const std::list<EventRequest::Event> &EventRequest::getEvents(void) const
{
    return this->events;
}

EventRequestModifier::EventRequestModifier(const double &time)
    : time(time), passed(0)
{}

void EventRequestModifier::modify(std::shared_ptr<Request> request,
                                 const Model &modifier,
                                 std::string event)
{
    auto trequest = std::dynamic_pointer_cast<EventRequest>(request);

    if (nullptr == trequest)
        return;

    trequest->addEvent(modifier.getName(), this->time, event);

    try
    {
        (void)dynamic_cast<const Terminator&>(modifier);
        this->passed++;
    }
    catch (std::bad_cast &)
    {}
}

size_t EventRequestModifier::getPassed(void) const
{
    return this->passed;
}

