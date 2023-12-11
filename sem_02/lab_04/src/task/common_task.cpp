#include "common_task.h"

#include <stdexcept>

#include "basic_pipe.h"
#include "buffer.h"
#include "generator.h"
#include "processor.h"
#include "gate.h"
#include "terminator.h"

static double probability = 0;

void set_probability(double value)
{
    probability = value;
}

const std::string &redirect_func(const std::list<std::string> &names, double)
{
    double val = (double)std::rand() / RAND_MAX;

    auto iter = names.begin();

    if (1 - probability < val)
        ++iter;

    return *iter;
}

bool check_done(std::shared_ptr<Request>, const Model &modifier, std::string)
{
    try
    {
        (void)dynamic_cast<const Terminator&>(modifier);
    }
    catch (std::bad_cast &)
    {
        return false;
    }

    return true;
}

void run_task(std::shared_ptr<RunnerBuilder> builder)
{
    std::shared_ptr<BasicPipe> pipe1 = std::make_shared<BasicPipe>("pipe1");
    std::shared_ptr<BasicPipe> pipe2 = std::make_shared<BasicPipe>("pipe2");
    std::shared_ptr<BasicPipe> pipe3 = std::make_shared<BasicPipe>("pipe3");
    std::shared_ptr<BasicPipe> pipe4 = std::make_shared<BasicPipe>("pipe4");

    std::shared_ptr<Generator> generator = std::make_shared<Generator>("generator", pipe1);
    std::shared_ptr<Buffer> buffer = std::make_shared<Buffer>("buffer", 0, pipe1, pipe2);
    std::shared_ptr<Processor> processor = std::make_shared<Processor>("processor", pipe2, pipe3);
    std::shared_ptr<Gate> gate = std::make_shared<Gate>("gate", pipe3, std::list<std::shared_ptr<Pipe>>{pipe4, pipe1});

    processor->registerSender(buffer);

    std::shared_ptr<Terminator> terminator1 = std::make_shared<Terminator>("terminator1", pipe1);
    std::shared_ptr<Terminator> terminator2 = std::make_shared<Terminator>("terminator2", pipe2);
    std::shared_ptr<Terminator> terminator3 = std::make_shared<Terminator>("terminator3", pipe4);

    std::shared_ptr<StatatisticsBlock> stats = std::make_shared<StatatisticsBlock>("stats",
        std::list<std::shared_ptr<Model>>{
            pipe1, pipe2, pipe3, pipe4,
            generator, buffer, processor, gate,
            terminator1, terminator2, terminator3
        });

    builder->addModel(generator)
            .addModel(pipe1)
            .addModel(processor)
            .addModel(terminator1)
            .addModel(pipe2)
            .addModel(buffer)
            .addModel(terminator2)
            .addModel(pipe3)
            .addModel(gate)
            .addModel(pipe4)
            .addModel(terminator3)
            .addModel(stats);

    builder->create();
    auto runner = builder->result();

    runner->run();
}

std::shared_ptr<RunnerBuilder> getTimeBuilder(const time_setup &setup)
{
    auto builder = std::make_shared<TimeRunnerBuilder>();

    builder->setRequests(setup.requests)
            .setTimeStep(setup.step)
            .setTimeLimit(setup.time_limit)
            .setTimeRequestModifier(setup.modifier)
            .registerModelCreator(std::make_shared<PipeTimeModelCreator>())
            .registerModelCreator(std::make_shared<BufferTimeModelCreator>())
            .registerModelCreator(std::make_shared<GeneratorTimeModelCreator>(setup.random, setup.creator))
            .registerModelCreator(std::make_shared<ProcessorTimeModelCreator>(setup.random))
            .registerModelCreator(std::make_shared<TerminatorTimeModelCreator>())
            .registerModelCreator(std::make_shared<GateTimeModelCreator>(setup.redirect))
            .registerModelCreator(std::make_shared<StatisticsBlockTimeModelCreator>(setup.stats));

    return builder;
}

std::shared_ptr<RunnerBuilder> getEventBuilder(const event_setup &setup)
{
    auto builder = std::make_shared<EventRunnerBuilder>();

    builder->setRequests(setup.requests)
            .setTimeLimit(setup.time_limit)
            .setEventRequestModifier(setup.modifier)
            .registerModelCreator(std::make_shared<PipeEventModelCreator>(setup.interval))
            .registerModelCreator(std::make_shared<BufferEventModelCreator>(setup.interval))
            .registerModelCreator(std::make_shared<GeneratorEventModelCreator>(setup.random, setup.creator))
            .registerModelCreator(std::make_shared<ProcessorEventModelCreator>(setup.random, setup.interval))
            .registerModelCreator(std::make_shared<TerminatorEventModelCreator>(setup.interval))
            .registerModelCreator(std::make_shared<GateEventModelCreator>(setup.redirect, setup.interval))
            .registerModelCreator(std::make_shared<StatisticsBlockEventModelCreator>(setup.interval, setup.stats));

    return builder;
}

TaskRequest::TaskRequest(size_t index) : ChronoRequest(index) {}

void TaskRequest::addEvent(std::string modelname, double time, std::string event)
{
    if ("generator" == modelname && "generate" == event)
        this->in = time;
    else if (("terminator1" == modelname || "terminator2" == modelname
        || "terminator3" == modelname) && "read" == event)
    {
        this->out = time;
        this->done = true;
    }
}

double TaskRequest::getAwait(void) const
{
    if (!this->done)
        throw std::runtime_error("Request doesn't reach terminator");

    return this->out - this->in;
}

std::shared_ptr<Request> TaskRequestCreator::create(void)
{
    this->mutex.lock();
    size_t current = this->current++;
    this->mutex.unlock();

    return std::make_shared<TaskRequest>(current);
}

FilledBufferStrategy::FilledBufferStrategy(std::string name)
    : name(name)
{}

void FilledBufferStrategy::execute(const StatatisticsBlock::ModelMap &map)
try
{
    auto buffer = this->getBuffer(map);
    const size_t size = buffer->used();

    if (size > this->max_size)
        this->max_size = size;
}
catch (std::runtime_error &)
{}

size_t FilledBufferStrategy::getMaxSize(void) const
{
    return this->max_size;
}

std::shared_ptr<Buffer> FilledBufferStrategy::getBuffer(const StatatisticsBlock::ModelMap &map) const
{
    auto iter = map.find(this->name);

    if (map.end() == iter)
        throw std::runtime_error("Buffer not set");

    return std::dynamic_pointer_cast<Buffer>((*iter).second);
}

AwaitBufferStrategy::AwaitBufferStrategy(std::list<std::string> names)
    : names(names)
{}

void AwaitBufferStrategy::execute(const StatatisticsBlock::ModelMap &map)
{
    this->requsts.merge(this->getRequests(map));
}

double AwaitBufferStrategy::getAvgAwait(void) const
{
    double sum = 0;
    size_t cnt = 0;

    for (auto req : this->requsts)
    {
        sum += req->getAwait();
        cnt++;
    }

    if (0 == cnt)
        throw std::logic_error("No requests found");

    return sum / cnt;
}

std::list<std::shared_ptr<TaskRequest>> AwaitBufferStrategy::getRequests(const StatatisticsBlock::ModelMap &map) const
{
    std::list<std::shared_ptr<TaskRequest>> out;

    for (auto terminator : this->getTerminators(map))
        for (auto ptr : terminator->getDone())
        {
            auto tptr = std::dynamic_pointer_cast<TaskRequest>(ptr);

            if (nullptr == tptr)
                throw std::runtime_error("Cast error");

            out.push_back(tptr);
        }

    return out;
}

std::list<std::shared_ptr<Terminator>> AwaitBufferStrategy::getTerminators(const StatatisticsBlock::ModelMap &map) const
{
    std::list<std::shared_ptr<Terminator>> out;

    for (auto name : this->names)
    {
        auto iter = map.find(name);

        if (map.end() == iter)
            throw std::runtime_error("Terminator not set");

        out.push_back(std::dynamic_pointer_cast<Terminator>((*iter).second));
    }

    return out;
}

void TickCountStrategy::execute(const StatatisticsBlock::ModelMap &)
{
    this->ticks++;
}

double TickCountStrategy::getTicks(void) const
{
    return this->ticks;
}

