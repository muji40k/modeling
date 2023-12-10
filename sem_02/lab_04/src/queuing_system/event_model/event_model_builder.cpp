#include "event_model_builder.h"

#include <stdexcept>

#include "event_runner.h"

void EventRunnerBuilder::create(void)
{
    this->runner = std::make_shared<EventRunner>(this->requests,
                                                 this->time_limit,
                                                 this->modifier,
                                                 this->models);
}

std::shared_ptr<Runner> EventRunnerBuilder::result(void)
{
    return this->runner;
}

EventRunnerBuilder &EventRunnerBuilder::setRequests(size_t val)
{
    this->requests = val;

    return *this;
}

EventRunnerBuilder &EventRunnerBuilder::setTimeLimit(double val)
{
    this->time_limit = val;

    return *this;
}

EventRunnerBuilder &EventRunnerBuilder::setEventRequestModifier(std::shared_ptr<EventRequestModifier> val)
{
    this->modifier = val;

    return *this;
}

RunnerBuilder &EventRunnerBuilder::addModel(std::shared_ptr<Model> model)
{
    if (nullptr == model)
        return *this;

    auto iter = this->creators.begin();

    for (; this->creators.end() != iter && !(*iter)->check(model); ++iter);

    if (this->creators.end() != iter)
        this->models.push_back((*iter)->create(model));

    return *this;
}

EventRunnerBuilder &EventRunnerBuilder::registerModelCreator(std::shared_ptr<EventModelCreator> creator)
{
    if (nullptr != creator)
        this->creators.push_back(creator);

    return *this;
}

// Creators

PipeEventModelCreator::PipeEventModelCreator(IntervalMap map)
    : map(map)
{}

bool PipeEventModelCreator::check(std::shared_ptr<Model> model) const
{
    return nullptr != std::dynamic_pointer_cast<Pipe>(model);
}

std::shared_ptr<EventModel> PipeEventModelCreator::create(std::shared_ptr<Model> model) const
{
    auto interval = this->map.find(model->getName());

    if (this->map.end() == interval)
        throw std::runtime_error("No interval found");

    return std::make_shared<PipeEventModel>(std::dynamic_pointer_cast<BasicPipe>(model), (*interval).second);
}

// ----------------------------------------------------------------------------

BufferEventModelCreator::BufferEventModelCreator(IntervalMap map)
    : map(map)
{}

bool BufferEventModelCreator::check(std::shared_ptr<Model> model) const
{
    return nullptr != std::dynamic_pointer_cast<Buffer>(model);
}

std::shared_ptr<EventModel> BufferEventModelCreator::create(std::shared_ptr<Model> model) const
{
    auto interval = this->map.find(model->getName());

    if (this->map.end() == interval)
        throw std::runtime_error("No interval found");

    return std::make_shared<BufferEventModel>(std::dynamic_pointer_cast<Buffer>(model), (*interval).second);
}

// ----------------------------------------------------------------------------

GeneratorEventModelCreator::GeneratorEventModelCreator(RandomMap random,
                                                       std::shared_ptr<RequestCreator> creator)
    : map(random), creator(creator)
{
    if (nullptr == creator)
        throw std::logic_error("Nullptr occured");
}

bool GeneratorEventModelCreator::check(std::shared_ptr<Model> model) const
{
    return nullptr != std::dynamic_pointer_cast<Generator>(model);
}

std::shared_ptr<EventModel> GeneratorEventModelCreator::create(std::shared_ptr<Model> model) const
{
    auto random = this->map.find(model->getName());

    if (this->map.end() == random)
        throw std::runtime_error("No random found");

    return std::make_shared<GeneratorEventModel>(std::dynamic_pointer_cast<Generator>(model), this->creator, (*random).second);
}

// ----------------------------------------------------------------------------

ProcessorEventModelCreator::ProcessorEventModelCreator(RandomMap random,
                                                       IntervalMap interval)
    : rmap(random), imap(interval)
{}

bool ProcessorEventModelCreator::check(std::shared_ptr<Model> model) const
{
    return nullptr != std::dynamic_pointer_cast<Processor>(model);
}

std::shared_ptr<EventModel> ProcessorEventModelCreator::create(std::shared_ptr<Model> model) const
{
    auto interval = this->imap.find(model->getName());

    if (this->imap.end() == interval)
        throw std::runtime_error("No interval found");

    auto random = this->rmap.find(model->getName());

    if (this->rmap.end() == random)
        throw std::runtime_error("No random found");

    return std::make_shared<ProcessorEventModel>(std::dynamic_pointer_cast<Processor>(model), (*random).second, (*interval).second);
}

// ----------------------------------------------------------------------------

TerminatorEventModelCreator::TerminatorEventModelCreator(IntervalMap map)
    : map(map)
{}

bool TerminatorEventModelCreator::check(std::shared_ptr<Model> model) const
{
    return nullptr != std::dynamic_pointer_cast<Terminator>(model);
}

std::shared_ptr<EventModel> TerminatorEventModelCreator::create(std::shared_ptr<Model> model) const
{
    auto interval = this->map.find(model->getName());

    if (this->map.end() == interval)
        throw std::runtime_error("No interval found");

    return std::make_shared<TerminatorEventModel>(std::dynamic_pointer_cast<Terminator>(model), (*interval).second);
}

// ----------------------------------------------------------------------------

GateEventModelCreator::GateEventModelCreator(RedirectMap rmap, IntervalMap imap)
    : rmap(rmap), imap(imap)
{}

bool GateEventModelCreator::check(std::shared_ptr<Model> model) const
{
    return nullptr != std::dynamic_pointer_cast<Gate>(model);
}

std::shared_ptr<EventModel> GateEventModelCreator::create(std::shared_ptr<Model> model) const
{
    auto interval = this->imap.find(model->getName());

    if (this->imap.end() == interval)
        throw std::runtime_error("No interval found");

    auto redirect = this->rmap.find(model->getName());

    if (this->rmap.end() == redirect)
        throw std::runtime_error("No random found");

    return std::make_shared<GateEventModel>(std::dynamic_pointer_cast<Gate>(model), (*interval).second, (*redirect).second);
}

// ----------------------------------------------------------------------------

StatisticsBlockEventModelCreator::StatisticsBlockEventModelCreator(IntervalMap imap, StatisticsMap smap)
    : imap(imap), smap(smap)
{}

bool StatisticsBlockEventModelCreator::check(std::shared_ptr<Model> model) const
{
    return nullptr != std::dynamic_pointer_cast<StatatisticsBlock>(model);
}

std::shared_ptr<EventModel> StatisticsBlockEventModelCreator::create(std::shared_ptr<Model> model) const
{
    auto interval = this->imap.find(model->getName());

    if (this->imap.end() == interval)
        throw std::runtime_error("No interval found");

    auto stats = this->smap.find(model->getName());

    if (this->smap.end() == stats)
        throw std::runtime_error("Statistic strategies not set");

    return std::make_shared<StatatisticsBlockEventModel>(std::dynamic_pointer_cast<StatatisticsBlock>(model), (*interval).second, (*stats).second);
}

