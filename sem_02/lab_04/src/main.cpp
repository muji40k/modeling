#include "time_model.h"
#include "time_model_builder.h"
#include "event_model.h"
#include "event_model_builder.h"

#include "uniform.h"
#include "chrono_request.h"

#include <iostream>

const std::string &uniform_redirect(const std::list<std::string> &names, double)
{
    size_t val = (size_t)(names.size() * (double)std::rand() / RAND_MAX) % names.size();

    auto iter = names.begin();

    for (; val; val--, ++iter);

    return *iter;
}

class ETest : public EventRequestModifier
{
    public:
        ETest(std::shared_ptr<ChronoRequestModifier> modifier)
            : modifier(std::make_shared<Wrap>(modifier))
        {}

        virtual ~ETest(void) override = default;

        virtual void setTime(const double &time) override
        {
            this->modifier->wrapped->setTime(time);
        }

        virtual size_t getPassed(void) override
        {
            return this->modifier->passed;
        }

        virtual std::shared_ptr<RequestModifier> getModifier(void) override
        {
            return this->modifier;
        }

    private:
        class Wrap : public RequestModifier
        {
            public:
                Wrap(std::shared_ptr<ChronoRequestModifier> wrapped)
                    : wrapped(wrapped)
                {}

                virtual ~Wrap(void) override = default;

                virtual void modify(std::shared_ptr<Request> request,
                                    const Model &modifier,
                                    std::string event) override
                {
                    if (this->wrapped)
                        this->wrapped->modify(request, modifier, event);

                    // if (modifier.getName() == "terminator3")
                    //     this->passed++;
                    try
                    {
                        (void)dynamic_cast<const Terminator&>(modifier);
                        this->passed++;
                    }
                    catch (std::bad_cast &)
                    {}
                }

            public:
                size_t passed = 0;
                std::shared_ptr<ChronoRequestModifier> wrapped;
        };

    private:
        std::shared_ptr<Wrap> modifier;
};

class Test : public TimeRequestModifier
{
    public:
        Test(std::shared_ptr<ChronoRequestModifier> modifier)
            : modifier(std::make_shared<Wrap>(modifier))
        {}

        virtual ~Test(void) override = default;

        virtual void setTime(const double &time) override
        {
            this->modifier->wrapped->setTime(time);
        }

        virtual size_t getPassed(void) override
        {
            return this->modifier->passed;
        }

        virtual std::shared_ptr<RequestModifier> getModifier(void) override
        {
            return this->modifier;
        }

    private:
        class Wrap : public RequestModifier
        {
            public:
                Wrap(std::shared_ptr<ChronoRequestModifier> wrapped)
                    : wrapped(wrapped)
                {}

                virtual ~Wrap(void) override = default;

                virtual void modify(std::shared_ptr<Request> request,
                                    const Model &modifier,
                                    std::string event) override
                {
                    if (this->wrapped)
                        this->wrapped->modify(request, modifier, event);

                    // if (modifier.getName() == "terminator3")
                    //     this->passed++;
                    try
                    {
                        (void)dynamic_cast<const Terminator&>(modifier);
                        this->passed++;
                    }
                    catch (std::bad_cast &)
                    {}
                }

            public:
                size_t passed = 0;
                std::shared_ptr<ChronoRequestModifier> wrapped;
        };

    private:
        std::shared_ptr<Wrap> modifier;
};

struct req
{
    std::shared_ptr<RequestCreator> creator;
    struct
    {
        std::shared_ptr<TimeRequestModifier> time;
        std::shared_ptr<EventRequestModifier> event;
    } modifier;
};

std::shared_ptr<RunnerBuilder> getTimeBuilder(size_t requests, double limit,
                                              double step, const TimeRunnerBuilderMisc::RandomMap &random,
                                              const TimeRunnerBuilderMisc::RedirectMap &redirect,
                                              const struct req &request)
{
    auto builder = std::make_shared<TimeRunnerBuilder>();

    builder->setRequests(requests)
            .setTimeStep(step)
            .setTimeLimit(limit)
            // .setTimeRequestModifier(std::make_shared<Test>(std::make_shared<ChronoRequestModifier>()))
            .setTimeRequestModifier(request.modifier.time)
            .registerModelCreator(std::make_shared<PipeTimeModelCreator>())
            .registerModelCreator(std::make_shared<BufferTimeModelCreator>())
            // .registerModelCreator(std::make_shared<GeneratorTimeModelCreator>(random, std::make_shared<ChronoRequestCreator>()))
            .registerModelCreator(std::make_shared<GeneratorTimeModelCreator>(random, request.creator))
            .registerModelCreator(std::make_shared<ProcessorTimeModelCreator>(random))
            .registerModelCreator(std::make_shared<TerminatorTimeModelCreator>())
            .registerModelCreator(std::make_shared<GateTimeModelCreator>(redirect))
            .registerModelCreator(std::make_shared<StatisticsBlockTimeModelCreator>(1));

    return builder;
}

std::shared_ptr<RunnerBuilder> getEventBuilder(size_t requests, double limit,
                                               const EventRunnerBuilderMisc::IntervalMap &interval,
                                               const EventRunnerBuilderMisc::RandomMap &random,
                                               const EventRunnerBuilderMisc::RedirectMap &redirect,
                                               const struct req &request)
{
    auto builder = std::make_shared<EventRunnerBuilder>();

    builder->setRequests(requests)
            .setTimeLimit(limit)
            .setEventRequestModifier(request.modifier.event)
            .registerModelCreator(std::make_shared<PipeEventModelCreator>(interval))
            .registerModelCreator(std::make_shared<BufferEventModelCreator>(interval))
            .registerModelCreator(std::make_shared<GeneratorEventModelCreator>(random, request.creator))
            .registerModelCreator(std::make_shared<ProcessorEventModelCreator>(random, interval))
            .registerModelCreator(std::make_shared<TerminatorEventModelCreator>(interval))
            .registerModelCreator(std::make_shared<GateEventModelCreator>(redirect, interval))
            .registerModelCreator(std::make_shared<StatisticsBlockEventModelCreator>(interval));

    return builder;
}

int main(void)
{
    constexpr const size_t requests = 1000;

    struct req request =
    {
        std::make_shared<ChronoRequestCreator>(),
        {std::make_shared<Test>(std::make_shared<ChronoRequestModifier>()),
         std::make_shared<ETest>(std::make_shared<ChronoRequestModifier>())}
    };

    TimeRunnerBuilderMisc::RandomMap random =
    {
        {"generator", std::make_shared<UniformRandom>(3, 7)},
        {"processor", std::make_shared<UniformRandom>(2, 5)}
    };

    TimeRunnerBuilderMisc::RedirectMap redirect =
    {
        {"gate", uniform_redirect}
    };

    EventRunnerBuilderMisc::IntervalMap interval =
    {
        {"pipe1", LinearIntervals(0.09, 0.1)},
        {"pipe2", LinearIntervals(0.09, 0.1)},
        {"pipe3", LinearIntervals(0.09, 0.1)},
        {"pipe4", LinearIntervals(0.09, 0.1)},
        {"buffer", LinearIntervals(0.1, 0.1)},
        {"processor", LinearIntervals(0.1, 0.1)},
        {"gate", LinearIntervals(0.1, 0.1)},
        {"terminator1", LinearIntervals(0.11, 0.1)},
        {"terminator2", LinearIntervals(0.11, 0.1)},
        {"terminator3", LinearIntervals(0.11, 0.1)},
    };

    std::shared_ptr<BasicPipe> pipe1 = std::make_shared<BasicPipe>("pipe1");
    std::shared_ptr<BasicPipe> pipe2 = std::make_shared<BasicPipe>("pipe2");
    std::shared_ptr<BasicPipe> pipe3 = std::make_shared<BasicPipe>("pipe3");
    std::shared_ptr<BasicPipe> pipe4 = std::make_shared<BasicPipe>("pipe4");

    std::shared_ptr<Generator> generator = std::make_shared<Generator>("generator", pipe1);
    // std::shared_ptr<Buffer> buffer = std::make_shared<Buffer>("buffer", 250, pipe1, pipe2);
    std::shared_ptr<Buffer> buffer = std::make_shared<Buffer>("buffer", 0, pipe1, pipe2);
    std::shared_ptr<Processor> processor = std::make_shared<Processor>("processor", pipe2, pipe3);
    std::shared_ptr<Gate> gate = std::make_shared<Gate>("gate", pipe3, std::list<std::shared_ptr<Pipe>>{pipe4, pipe1});

    processor->registerSender(buffer);

    std::shared_ptr<Terminator> terminator1 = std::make_shared<Terminator>("terminator1", pipe1);
    std::shared_ptr<Terminator> terminator2 = std::make_shared<Terminator>("terminator2", pipe2);
    std::shared_ptr<Terminator> terminator3 = std::make_shared<Terminator>("terminator3", pipe4);

    auto builder = getTimeBuilder(requests, 1000000, 0.01, random, redirect, request);
    // auto builder = getEventBuilder(requests, 1000000, interval, random, redirect, request);

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
            .addModel(terminator3);

    builder->create();
    auto runner = builder->result();

    runner->run();

    std::list<std::shared_ptr<Terminator>> terminators = {terminator1, terminator2, terminator3};
    // std::list<std::shared_ptr<Terminator>> terminators = {terminator1, terminator3};
    double maxtime = 0;
    double totalawait = 0;
    size_t total = 0;
    size_t finished = 0;

    for (auto terminator : terminators)
    {
        std::cout << std::endl << "Terminator: " << terminator->getName() << std::endl;

        for (auto request : terminator->getDone())
        {
            auto treq = std::dynamic_pointer_cast<ChronoRequest>(request);
            const auto &events = treq->getEvents();
            maxtime = std::max(maxtime, events.back().time);

            size_t redirects = 0;
            double await = 0, last_in;

            for (auto &event : events)
            {
                if (event.event == "redirect")
                    redirects++;

                if (event.modelname == "buffer")
                {
                    if (event.event == "read")
                        last_in = event.time;
                    else if (event.event == "callback")
                        await += event.time - last_in;
                }
            }

            if (redirects)
            {
                totalawait += await / redirects;
                total++;
            }

            if (events.back().modelname == "terminator3")
                finished++;

            std::cout << "Request #" << treq->getIndex()
                      << " | origin: " << events.front().time
                      << ", time: " << events.back().time - events.front().time
                      << ", redirects: " << redirects
                      << ", await: " << await
                      << ", avg_await: " << await / redirects
                      << std::endl;
        }
    }

    std::cout << std::endl << "Simulation time: " << maxtime << std::endl
                           << "Correct requests: " << finished << " ("  << (double)finished / requests * 100 << "%)" << std::endl
                           << "Average await time: " << totalawait / total << std::endl;

    // std::cout << "$ ";
    // std::string in;
    // std::cin >> in;
    //  
    // while ("q" != in)
    // {
    //     std::shared_ptr<ChronoRequest> rq = nullptr;
    //  
    //     for (auto iter = terminators.begin(); !rq && terminators.end() != iter; ++iter)
    //     {
    //         const auto &done = (*iter)->getDone();
    //  
    //         for (auto riter = done.begin(); !rq && done.end() != riter; ++riter)
    //         {
    //             auto cur = std::dynamic_pointer_cast<ChronoRequest>(*riter);
    //  
    //             if (in == std::to_string(cur->getIndex()))
    //                 rq = cur;
    //         }
    //     }
    //  
    //     if (!rq)
    //         std::cout << "Not found" << std::endl;
    //     else
    //     {
    //         for (auto event : rq->getEvents())
    //             std::cout << event.time << "\t" << event.modelname << "\t" << event.event << std::endl;
    //     }
    //  
    //     std::cout << "$ ";
    //     std::cin >> in;
    // }

    return 0;
}

