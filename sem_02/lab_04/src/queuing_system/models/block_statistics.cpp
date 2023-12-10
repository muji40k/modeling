#include "block_statistics.h"

#include <stdexcept>

StatatisticsBlock::StatatisticsBlock(std::string name,
                                     std::list<std::shared_ptr<Model>> targets)
    : Model(name)
{
    for (auto model : targets)
    {
        if (nullptr == model)
            throw std::logic_error("Nullptr occured");

        if (this->map.end() != this->map.find(model->getName()))
            throw std::logic_error("Duplicate model");

        this->map.emplace(model->getName(), model);
    }
}

void StatatisticsBlock::registerStrategy(std::shared_ptr<Strategy> strategy)
{
    if (nullptr == strategy)
        throw std::logic_error("Nullptr occured");

    this->strategies.push_back(strategy);
}

void StatatisticsBlock::write(void)
{
    for (auto strat : this->strategies)
        strat->execute(this->map);
}

