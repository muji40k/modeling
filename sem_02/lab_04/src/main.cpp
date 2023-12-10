#include <iostream>

#include "uniform.h"
#include "normal.h"

#include "common_task.h"
#include "time_task.h"
#include "time_model_builder.h"
#include "event_task.h"
#include "event_model_builder.h"

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
                                              const TimeRunnerBuilderMisc::StatisticsMap &stats,
                                              const struct req &request)
{
    auto builder = std::make_shared<TimeRunnerBuilder>();

    builder->setRequests(requests)
            .setTimeStep(step)
            .setTimeLimit(limit)
            .setTimeRequestModifier(request.modifier.time)
            .registerModelCreator(std::make_shared<PipeTimeModelCreator>())
            .registerModelCreator(std::make_shared<BufferTimeModelCreator>())
            .registerModelCreator(std::make_shared<GeneratorTimeModelCreator>(random, request.creator))
            .registerModelCreator(std::make_shared<ProcessorTimeModelCreator>(random))
            .registerModelCreator(std::make_shared<TerminatorTimeModelCreator>())
            .registerModelCreator(std::make_shared<GateTimeModelCreator>(redirect))
            .registerModelCreator(std::make_shared<StatisticsBlockTimeModelCreator>(stats));

    return builder;
}

std::shared_ptr<RunnerBuilder> getEventBuilder(size_t requests, double limit,
                                               const EventRunnerBuilderMisc::IntervalMap &interval,
                                               const EventRunnerBuilderMisc::RandomMap &random,
                                               const EventRunnerBuilderMisc::RedirectMap &redirect,
                                               const TimeRunnerBuilderMisc::StatisticsMap &stats,
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
            .registerModelCreator(std::make_shared<StatisticsBlockEventModelCreator>(interval, stats));

    return builder;
}

int main(void)
{
    constexpr const size_t requests = 1000;

    struct req request =
    {
        std::make_shared<TaskRequestCreator>(),
        {std::make_shared<TaskTimeRequestModifier>(std::make_shared<ChronoRequestModifier>()),
         std::make_shared<TaskEventRequestModifier>(std::make_shared<ChronoRequestModifier>())}
    };

    TimeRunnerBuilderMisc::RandomMap random =
    {
        {"generator", std::make_shared<UniformRandom>(3, 7)},
        {"processor", std::make_shared<NormalRandom>(2, 1)}
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
        {"stats", LinearIntervals(0.12, 0.1)}
    };

    auto bufstrat = std::make_shared<FilledBufferStrategy>("buffer");
    auto awaitstrat = std::make_shared<AwaitBufferStrategy>(std::list<std::string>({"terminator1", "terminator2", "terminator3"}));
    auto tickstrat = std::make_shared<TickCountStrategy>();

    EventRunnerBuilderMisc::StatisticsMap statistics =
    {
        {"stats", {bufstrat, awaitstrat, tickstrat}}
    };

    // auto builder = getTimeBuilder(requests, 1000000, 0.1, random, redirect, statistics, request);
    auto builder = getEventBuilder(requests, 1000000, interval, random, redirect, statistics, request);

    run_task(builder);

    std::cout << "Max buffer size: " << bufstrat->getMaxSize() << std::endl
              << "Average await time: " << awaitstrat->getAvgAwait() << std::endl
              << "Total time: " << 0.1 * tickstrat->getTicks() << std::endl;

    return 0;
}

