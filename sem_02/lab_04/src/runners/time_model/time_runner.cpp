#include "time_runner.h"

TimeRunner::TimeRunner(size_t requests, double time, double step,
                       std::list<std::shared_ptr<TimeModel>> items)
    : requests(requests), end(std::abs(time)), step(std::abs(step))
{
    for (auto &item : items)
    {
        auto iter = this->items.find(item->priority());

        if (this->items.end() == iter)
            this->items.emplace(item->priority(),
                                std::list<std::shared_ptr<TimeModel>>({item}));
        else
            (*iter).second.push_back(item);
    }
}

void TimeRunner::run(void)
{
    double time = 0;
    auto modifier = std::make_shared<TimeRequestModifier>(time);

    for (auto &pair : this->items)
        for (auto &item : pair.second)
            item->setModifier(modifier);

    for (; this->end > time && this->requests > modifier->getPassed();
           time += this->step)
        for (auto &pair : this->items)
            for (auto &item : pair.second)
                item->tick(time);
}

