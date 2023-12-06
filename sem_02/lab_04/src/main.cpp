#include "time_model.h"
#include "time_model_builder.h"
#include "uniform.h"

#include <iostream>

const std::string &uniform_redirect(const std::list<std::string> &names, double)
{
    size_t val = (size_t)(names.size() * (double)std::rand() / RAND_MAX) % names.size();

    auto iter = names.begin();

    for (; val; val--, ++iter);

    return *iter;
}

std::shared_ptr<RunnerBuilder> getTimeBuilder(size_t requests, double limit,
                                              double step, const RandomMap &random,
                                              const GateTimeModelCreator::RedirectMap &redirect)
{
    auto builder = std::make_shared<TimeRunnerBuilder>();

    builder->setRequests(requests)
            .setTimeStep(step)
            .setTimeLimit(limit)
            .registerModelCreator(std::make_shared<PipeTimeModelCreator>())
            .registerModelCreator(std::make_shared<BufferTimeModelCreator>())
            .registerModelCreator(std::make_shared<GeneratorTimeModelCreator>(random))
            .registerModelCreator(std::make_shared<ProcessorTimeModelCreator>(random))
            .registerModelCreator(std::make_shared<TerminatorTimeModelCreator>())
            .registerModelCreator(std::make_shared<GateTimeModelCreator>(redirect));

    return builder;
}

int main(void)
{
    constexpr const size_t requests = 1000;

    RandomMap random =
    {
        {"generator", std::make_shared<UniformRandom>(3, 7)},
        {"processor", std::make_shared<UniformRandom>(2, 5)}
    };

    GateTimeModelCreator::RedirectMap redirect =
    {
        {"gate", uniform_redirect}
    };

    std::shared_ptr<BasicPipe> pipe1 = std::make_shared<BasicPipe>("pipe1");
    std::shared_ptr<BasicPipe> pipe2 = std::make_shared<BasicPipe>("pipe2");
    std::shared_ptr<BasicPipe> pipe3 = std::make_shared<BasicPipe>("pipe3");
    std::shared_ptr<BasicPipe> pipe4 = std::make_shared<BasicPipe>("pipe4");

    std::shared_ptr<Generator> generator = std::make_shared<Generator>("generator", pipe1);
    std::shared_ptr<Buffer> buffer = std::make_shared<Buffer>("buffer", 250, pipe1, pipe2);
    std::shared_ptr<Processor> processor = std::make_shared<Processor>("processor", pipe2, pipe3);
    std::shared_ptr<Gate> gate = std::make_shared<Gate>("gate", pipe3, std::list<std::shared_ptr<Pipe>>{pipe4, pipe1});

    processor->registerSender(buffer);

    std::shared_ptr<Terminator> terminator1 = std::make_shared<Terminator>("terminator1", pipe1);
    std::shared_ptr<Terminator> terminator2 = std::make_shared<Terminator>("terminator2", pipe2);
    std::shared_ptr<Terminator> terminator3 = std::make_shared<Terminator>("terminator3", pipe4);

    auto builder = getTimeBuilder(requests, 1000000, 0.01, random, redirect);
    // auto builder = getTimeBuilder(200, 10000, 1, random, redirect);

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
    double maxtime = 0;
    double totalawait = 0;
    size_t total = 0;
    size_t finished = 0;

    for (auto terminator : terminators)
    {
        std::cout << std::endl << "Terminator: " << terminator->getName() << std::endl;

        for (auto request : terminator->getDone())
        {
            auto treq = std::dynamic_pointer_cast<TimeRequest>(request);
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

    return 0;
}

