#ifndef _COMMON_TASK_H_
#define _COMMON_TASK_H_

#include <list>
#include <string>
#include <memory>

#include "builder.h"
#include "time_model_builder.h"
#include "event_model_builder.h"
#include "buffer.h"
#include "terminator.h"
#include "block_statistics.h"

#include "chrono_request.h"

bool check_done(std::shared_ptr<Request> request, const Model &modifier,
                std::string event);

void run_task(std::shared_ptr<RunnerBuilder> builder);

struct time_setup
{
    std::shared_ptr<RequestCreator> creator;
    size_t requests;
    double time_limit;

    double step;
    std::shared_ptr<TimeRequestModifier> modifier;
    const TimeRunnerBuilderMisc::RandomMap &random;
    const TimeRunnerBuilderMisc::RedirectMap &redirect;
    const TimeRunnerBuilderMisc::StatisticsMap &stats;
};

struct event_setup
{
    std::shared_ptr<RequestCreator> creator;
    size_t requests;
    double time_limit;

    std::shared_ptr<EventRequestModifier> modifier;
    const EventRunnerBuilderMisc::IntervalMap &interval;
    const EventRunnerBuilderMisc::RandomMap &random;
    const EventRunnerBuilderMisc::RedirectMap &redirect;
    const EventRunnerBuilderMisc::StatisticsMap &stats;
};

std::shared_ptr<RunnerBuilder> getTimeBuilder(const struct time_setup &setup);
std::shared_ptr<RunnerBuilder> getEventBuilder(const struct event_setup &setup);

class TaskRequest : public ChronoRequest
{
    public:
        TaskRequest(size_t index);
        virtual ~TaskRequest(void) override = default;
        virtual void addEvent(std::string modelname, double time, std::string event) override;

        double getAwait(void) const;

    private:
        bool done = false;
        double in = 0;
        double out = 0;
};

class TaskRequestCreator : public RequestCreator
{
    public:
        virtual ~TaskRequestCreator(void) override = default;
        virtual std::shared_ptr<Request> create(void) override;

    private:
        std::mutex mutex;
        size_t current = 0;
};

class TerminatorStrategy : public StatatisticsBlock::Strategy
{
    public:
        TerminatorStrategy(std::list<std::string> names,
                           std::list<std::string> targets);
        virtual ~TerminatorStrategy(void) override = default;
        virtual void execute(const StatatisticsBlock::ModelMap &map) override;

        double getAvgAwait(void) const;
        double getLostProbability(void) const;
        size_t getLost(void) const;
        size_t getTotal(void) const;

    private:
        std::list<std::shared_ptr<TaskRequest>> getRequests(const StatatisticsBlock::ModelMap &map);
        std::list<std::shared_ptr<Terminator>> getTerminators(const StatatisticsBlock::ModelMap &map) const;

    private:
        std::list<std::string> names;
        std::list<std::string> targets;
        std::list<std::shared_ptr<TaskRequest>> requsts;
        size_t lost = 0;
        size_t total = 0;
};

class TickCountStrategy : public StatatisticsBlock::Strategy
{
    public:
        virtual ~TickCountStrategy(void) override = default;
        virtual void execute(const StatatisticsBlock::ModelMap &map) override;

        double getTicks(void) const;

    private:
        size_t ticks;
};

#endif

