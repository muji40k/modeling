#include "chrono_request.h"

#include "terminator.h"

ChronoRequest::ChronoRequest(size_t index) : index(index) {}

size_t ChronoRequest::getIndex(void) const
{
    return this->index;
}

void ChronoRequest::addEvent(std::string modelname, double time, std::string event)
{
    this->events.push_back({modelname, time, event});
}

const std::list<ChronoRequest::Event> &ChronoRequest::getEvents(void) const
{
    return this->events;
}

void ChronoRequestModifier::modify(std::shared_ptr<Request> request,
                                 const Model &modifier,
                                 std::string event)
{
    if (nullptr == this->time)
        return;

    auto trequest = std::dynamic_pointer_cast<ChronoRequest>(request);

    if (nullptr == trequest)
        return;

    trequest->addEvent(modifier.getName(), *this->time, event);
}

void ChronoRequestModifier::setTime(const double &time)
{
    this->time = &time;
}

std::shared_ptr<Request> ChronoRequestCreator::create(void)
{
    this->mutex.lock();
    size_t current = this->current++;
    this->mutex.unlock();

    return std::make_shared<ChronoRequest>(current);
}

