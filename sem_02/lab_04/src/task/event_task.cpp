#include "event_task.h"

#include "common_task.h"

TaskEventRequestModifier::TaskEventRequestModifier(std::shared_ptr<ChronoRequestModifier> modifier)
    : modifier(std::make_shared<Wrap>(modifier))
{}

void TaskEventRequestModifier::setTime(const double &time)
{
    this->modifier->wrapped->setTime(time);
}

size_t TaskEventRequestModifier::getPassed(void)
{
    return this->modifier->passed;
}

std::shared_ptr<RequestModifier> TaskEventRequestModifier::getModifier(void)
{
    return this->modifier;
}

TaskEventRequestModifier::Wrap::Wrap(std::shared_ptr<ChronoRequestModifier> wrapped)
    : wrapped(wrapped)
{}

void TaskEventRequestModifier::Wrap::modify(std::shared_ptr<Request> request,
                                           const Model &modifier,
                                           std::string event)
{
    if (this->wrapped)
        this->wrapped->modify(request, modifier, event);

    if (check_done(request, modifier, event))
        this->passed++;
}

