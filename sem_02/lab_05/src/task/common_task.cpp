#include "common_task.h"

#include <stdexcept>

#include "basic_pipe.h"
#include "buffer.h"
#include "generator.h"
#include "processor.h"
#include "gate.h"
#include "terminator.h"

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
    std::shared_ptr<BasicPipe> pipe5 = std::make_shared<BasicPipe>("pipe5");
    std::shared_ptr<BasicPipe> pipe6 = std::make_shared<BasicPipe>("pipe6");

    std::shared_ptr<Generator> generator = std::make_shared<Generator>("generator", pipe1);
    std::shared_ptr<Processor> operator1 = std::make_shared<Processor>("operator1", pipe1, pipe2);
    std::shared_ptr<Processor> operator2 = std::make_shared<Processor>("operator2", pipe1, pipe2);
    std::shared_ptr<Processor> operator3 = std::make_shared<Processor>("operator3", pipe1, pipe3);
    std::shared_ptr<Buffer> buffer1 = std::make_shared<Buffer>("buffer1", 0, pipe2, pipe4);
    std::shared_ptr<Buffer> buffer2 = std::make_shared<Buffer>("buffer2", 0, pipe3, pipe5);
    std::shared_ptr<Processor> processor1 = std::make_shared<Processor>("processor1", pipe4, pipe6);
    std::shared_ptr<Processor> processor2 = std::make_shared<Processor>("processor2", pipe5, pipe6);

    processor1->registerSender(buffer1);
    processor2->registerSender(buffer2);

    std::shared_ptr<Terminator> terminator1 = std::make_shared<Terminator>("terminator1", pipe1);
    std::shared_ptr<Terminator> terminator2 = std::make_shared<Terminator>("terminator2", pipe6);

    std::shared_ptr<StatatisticsBlock> stats = std::make_shared<StatatisticsBlock>("stats",
        std::list<std::shared_ptr<Model>>{
            pipe1, pipe2, pipe3, pipe4, pipe5, pipe6,
            generator, operator1, operator2, operator3, buffer1, buffer2,
            processor1, processor2,
            terminator1, terminator2
        });

    builder->addModel(generator)
            .addModel(pipe1)
            .addModel(operator1)
            .addModel(operator2)
            .addModel(operator3)
            .addModel(terminator1)
            .addModel(pipe2)
            .addModel(pipe3)
            .addModel(buffer1)
            .addModel(buffer2)
            .addModel(pipe4)
            .addModel(pipe5)
            .addModel(processor1)
            .addModel(processor2)
            .addModel(pipe6)
            .addModel(terminator2)
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
    else if (("terminator1" == modelname || "terminator2" == modelname)
             && "read" == event)
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

TerminatorStrategy::TerminatorStrategy(std::list<std::string> names,
                                       std::list<std::string> targets)
    : names(names), targets(targets)
{}

void TerminatorStrategy::execute(const StatatisticsBlock::ModelMap &map)
{
    this->requsts.merge(this->getRequests(map));
}

double TerminatorStrategy::getAvgAwait(void) const
{
    if (0 == this->total)
        throw std::logic_error("No requests found");

    double sum = 0;

    for (auto req : this->requsts)
    {
        sum += req->getAwait();
    }

    return sum / this->total;
}

double TerminatorStrategy::getLostProbability(void) const
{
    if (0 == this->total)
        throw std::logic_error("No requests found");

    return (double)this->lost / this->total;
}

size_t TerminatorStrategy::getLost(void) const
{
    return this->lost;
}

size_t TerminatorStrategy::getTotal(void) const
{
    return this->total;
}

std::list<std::shared_ptr<TaskRequest>> TerminatorStrategy::getRequests(const StatatisticsBlock::ModelMap &map)
{
    std::list<std::shared_ptr<TaskRequest>> out;

    for (auto terminator : this->getTerminators(map))
    {
        auto done = terminator->getDone();

        for (auto ptr : done)
        {
            auto tptr = std::dynamic_pointer_cast<TaskRequest>(ptr);

            if (nullptr == tptr)
                throw std::runtime_error("Cast error");

            out.push_back(tptr);
        }

        auto iter = this->targets.begin();

        for (; this->targets.end() != iter && (*iter) != terminator->getName();
             ++iter);

        if (this->targets.end() == iter)
            this->lost += done.size();

        this->total += done.size();
    }

    return out;
}

std::list<std::shared_ptr<Terminator>> TerminatorStrategy::getTerminators(const StatatisticsBlock::ModelMap &map) const
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

