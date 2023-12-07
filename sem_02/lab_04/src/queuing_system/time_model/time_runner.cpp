#include "time_runner.h"

#include <stdexcept>

TimeRunner::TimeRunner(size_t requests, double time, double step,
                       std::shared_ptr<TimeRequestModifier> modifier,
                       std::list<std::shared_ptr<TimeModel>> items)
    : requests(requests), end(std::abs(time)), step(std::abs(step)),
      modifier(modifier)
{
    if (nullptr == this->modifier)
        throw std::logic_error("Nullptr modifier");

    for (auto &item : items)
    {
        if (nullptr == item)
            throw std::logic_error("Nullptr modifier");

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
    this->modifier->setTime(time);
    auto modifier = this->modifier->getModifier();

    for (auto &pair : this->items)
        for (auto &item : pair.second)
            item->setModifier(modifier);

    for (; this->end > time && this->requests > this->modifier->getPassed();
           time += this->step)
        for (auto &pair : this->items)
            for (auto &item : pair.second)
                item->tick(time);
}

