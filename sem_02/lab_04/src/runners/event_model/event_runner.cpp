#include "event_runner.h"

EventRunner::EventRunner(size_t requests, double time,
                         std::list<std::shared_ptr<EventModel>> items)
    : requests(requests), end(time), items(items)
{}

void EventRunner::run(void)
{
    double time = 0;
    auto modifier = std::make_shared<EventRequestModifier>(time);

    for (auto &item : this->items)
        item->setModifier(modifier);

    while (this->end > time && this->requests > modifier->getPassed())
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

