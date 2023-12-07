#include "block_statistics.h"

#include <stdexcept>

StatatisticsBlock::StatatisticsBlock(std::string name) : Model(name) {}

void StatatisticsBlock::registerStrategy(std::shared_ptr<Strategy> strategy)
{
    if (nullptr == strategy)
        throw std::logic_error("Nullptr occured");
}

void StatatisticsBlock::write(void)
{
    for (auto strat : this->strategies)
        strat->execute();
}

