#include "event_runner.h"

#include <stdexcept>

EventRunner::EventRunner(size_t requests, double time,
                         std::shared_ptr<EventRequestModifier> modifier,
                         std::list<std::shared_ptr<EventModel>> items)
    : requests(requests), end(time), modifier(modifier), items(items)
{
    if (nullptr == this->modifier)
        throw std::logic_error("Nullptr modifier");

    for (auto &item : items)
        if (nullptr == item)
            throw std::logic_error("Nullptr modifier");
}

void EventRunner::run(void)
{
    double time = 0;
    this->modifier->setTime(time);
    auto modifier = this->modifier->getModifier();

    for (auto &item : this->items)
        item->setModifier(modifier);

    while (this->end > time && this->requests > this->modifier->getPassed())
    {
        auto iter = this->items.begin(), next = iter;

        for (; this->items.end() != iter; ++iter)
            if ((*iter)->nextEvent() < (*next)->nextEvent())
                next = iter;

        auto model = *next;
        time = model->nextEvent();
        model->event();
        model->generateNextEvent();
    }
}

