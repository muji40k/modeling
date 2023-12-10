#include "time_model_builder.h"

#include <stdexcept>

#include "time_runner.h"

void TimeRunnerBuilder::create(void)
{
    this->runner = std::make_shared<TimeRunner>(this->requests,
                                                this->time_limit,
                                                this->step, this->modifier,
                                                this->models);
}

std::shared_ptr<Runner> TimeRunnerBuilder::result(void)
{
    return this->runner;
}

TimeRunnerBuilder &TimeRunnerBuilder::setRequests(size_t val)
{
    this->requests = val;

    return *this;
}

TimeRunnerBuilder &TimeRunnerBuilder::setTimeLimit(double val)
{
    this->time_limit = val;

    return *this;
}

TimeRunnerBuilder &TimeRunnerBuilder::setTimeStep(double val)
{
    this->step = val;

    return *this;
}

TimeRunnerBuilder &TimeRunnerBuilder::setTimeRequestModifier(std::shared_ptr<TimeRequestModifier> val)
{
    this->modifier = val;

    return *this;
}

RunnerBuilder &TimeRunnerBuilder::addModel(std::shared_ptr<Model> model)
{
    if (nullptr == model)
        return *this;

    auto iter = this->creators.begin();

    for (; this->creators.end() != iter && !(*iter)->check(model); ++iter);

    if (this->creators.end() != iter)
        this->models.push_back((*iter)->create(model));

    return *this;
}

TimeRunnerBuilder &TimeRunnerBuilder::registerModelCreator(std::shared_ptr<TimeModelCreator> creator)
{
    if (nullptr != creator)
        this->creators.push_back(creator);

    return *this;
}

// Creators

bool PipeTimeModelCreator::check(std::shared_ptr<Model> model) const
{
    return nullptr != std::dynamic_pointer_cast<Pipe>(model);
}

std::shared_ptr<TimeModel> PipeTimeModelCreator::create(std::shared_ptr<Model> model) const
{
    return std::make_shared<PipeTimeModel>(std::dynamic_pointer_cast<Pipe>(model));
}

// ----------------------------------------------------------------------------

bool BufferTimeModelCreator::check(std::shared_ptr<Model> model) const
{
    return nullptr != std::dynamic_pointer_cast<Buffer>(model);
}

std::shared_ptr<TimeModel> BufferTimeModelCreator::create(std::shared_ptr<Model> model) const
{
    return std::make_shared<BufferTimeModel>(std::dynamic_pointer_cast<Buffer>(model));
}

// ----------------------------------------------------------------------------

GeneratorTimeModelCreator::GeneratorTimeModelCreator(RandomMap random,
                                                     std::shared_ptr<RequestCreator> creator)
    : map(random), creator(creator)
{
    if (nullptr == creator)
        throw;
}

bool GeneratorTimeModelCreator::check(std::shared_ptr<Model> model) const
{
    return nullptr != std::dynamic_pointer_cast<Generator>(model);
}

std::shared_ptr<TimeModel> GeneratorTimeModelCreator::create(std::shared_ptr<Model> model) const
{
    auto random = this->map.find(model->getName());

    if (this->map.end() == random)
        throw;

    return std::make_shared<GeneratorTimeModel>(std::dynamic_pointer_cast<Generator>(model), this->creator, (*random).second);
}

// ----------------------------------------------------------------------------

ProcessorTimeModelCreator::ProcessorTimeModelCreator(RandomMap random)
    : map(random)
{}

bool ProcessorTimeModelCreator::check(std::shared_ptr<Model> model) const
{
    return nullptr != std::dynamic_pointer_cast<Processor>(model);
}

std::shared_ptr<TimeModel> ProcessorTimeModelCreator::create(std::shared_ptr<Model> model) const
{
    auto random = this->map.find(model->getName());

    if (this->map.end() == random)
        throw;

    return std::make_shared<ProcessorTimeModel>(std::dynamic_pointer_cast<Processor>(model), (*random).second);
}

// ----------------------------------------------------------------------------

bool TerminatorTimeModelCreator::check(std::shared_ptr<Model> model) const
{
    return nullptr != std::dynamic_pointer_cast<Terminator>(model);
}

std::shared_ptr<TimeModel> TerminatorTimeModelCreator::create(std::shared_ptr<Model> model) const
{
    return std::make_shared<TerminatorTimeModel>(std::dynamic_pointer_cast<Terminator>(model));
}

// ----------------------------------------------------------------------------

GateTimeModelCreator::GateTimeModelCreator(RedirectMap map)
    : map(map)
{}

bool GateTimeModelCreator::check(std::shared_ptr<Model> model) const
{
    return nullptr != std::dynamic_pointer_cast<Gate>(model);
}

std::shared_ptr<TimeModel> GateTimeModelCreator::create(std::shared_ptr<Model> model) const
{
    auto func = this->map.find(model->getName());

    if (this->map.end() == func)
        throw std::runtime_error("Redirect not set");

    return std::make_shared<GateTimeModel>(std::dynamic_pointer_cast<Gate>(model), (*func).second);
}

// ----------------------------------------------------------------------------

StatisticsBlockTimeModelCreator::StatisticsBlockTimeModelCreator(StatisticsMap map)
    : map(map)
{}

bool StatisticsBlockTimeModelCreator::check(std::shared_ptr<Model> model) const
{
    return nullptr != std::dynamic_pointer_cast<StatatisticsBlock>(model);
}

std::shared_ptr<TimeModel> StatisticsBlockTimeModelCreator::create(std::shared_ptr<Model> model) const
{
    auto stats = this->map.find(model->getName());

    if (this->map.end() == stats)
        throw std::runtime_error("Statistic strategies not set");

    return std::make_shared<StatatisticsBlockTimeModel>(std::dynamic_pointer_cast<StatatisticsBlock>(model), (*stats).second);
}

