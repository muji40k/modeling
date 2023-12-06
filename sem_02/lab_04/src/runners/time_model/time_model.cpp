#include "time_model.h"

#include "terminator.h"

TimeRequest::TimeRequest(size_t index) : index(index) {}

size_t TimeRequest::getIndex(void) const
{
    return this->index;
}

void TimeRequest::addEvent(std::string modelname, double time, std::string event)
{
    this->events.push_back({modelname, time, event});
}

const std::list<TimeRequest::Event> &TimeRequest::getEvents(void) const
{
    return this->events;
}

TimeRequestModifier::TimeRequestModifier(const double &time)
    : time(time), passed(0)
{}

void TimeRequestModifier::modify(std::shared_ptr<Request> request,
                                 const Model &modifier,
                                 std::string event)
{
    auto trequest = std::dynamic_pointer_cast<TimeRequest>(request);

    if (nullptr == trequest)
        return;

    trequest->addEvent(modifier.getName(), this->time, event);

    // std::cout << "[ "
    //           << std::setprecision(9) << std::setw(10)  << this->time
    //           << " ][ "
    //           << std::setw(12) << modifier.getName()
    //           << " ] id: "
    //           << std::setw(6) << trequest->getIndex()
    //           << ", event: " << event << std::endl;

    try
    {
        (void)dynamic_cast<const Terminator&>(modifier);
        this->passed++;
    }
    catch (std::bad_cast &)
    {}
}

size_t TimeRequestModifier::getPassed(void) const
{
    return this->passed;
}

