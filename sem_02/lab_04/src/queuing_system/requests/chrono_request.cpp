#include "chrono_request.h"

#include "terminator.h"

ChronoRequest::ChronoRequest(size_t index) : index(index) {}

size_t ChronoRequest::getIndex(void) const
{
    return this->index;
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

