#include "time_task.h"

#include "common_task.h"

TaskTimeRequestModifier::TaskTimeRequestModifier(std::shared_ptr<ChronoRequestModifier> modifier)
    : modifier(std::make_shared<Wrap>(modifier))
{}

void TaskTimeRequestModifier::setTime(const double &time)
{
    this->modifier->wrapped->setTime(time);
}

size_t TaskTimeRequestModifier::getPassed(void)
{
    return this->modifier->passed;
}

std::shared_ptr<RequestModifier> TaskTimeRequestModifier::getModifier(void)
{
    return this->modifier;
}

TaskTimeRequestModifier::Wrap::Wrap(std::shared_ptr<ChronoRequestModifier> wrapped)
    : wrapped(wrapped)
{}

void TaskTimeRequestModifier::Wrap::modify(std::shared_ptr<Request> request,
                                           const Model &modifier,
                                           std::string event)
{
    if (this->wrapped)
        this->wrapped->modify(request, modifier, event);

    if (check_done(request, modifier, event))
        this->passed++;
}

