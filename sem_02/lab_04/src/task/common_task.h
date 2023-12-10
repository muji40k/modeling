#ifndef _COMMON_TASK_H_
#define _COMMON_TASK_H_

#include <list>
#include <string>
#include <memory>

#include "builder.h"
#include "buffer.h"
#include "terminator.h"
#include "block_statistics.h"

#include "chrono_request.h"

const std::string &uniform_redirect(const std::list<std::string> &names,
                                    double time);

bool check_done(std::shared_ptr<Request> request, const Model &modifier,
                std::string event);

void run_task(std::shared_ptr<RunnerBuilder> builder);

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

class FilledBufferStrategy : public StatatisticsBlock::Strategy
{
    public:
        FilledBufferStrategy(std::string name);
        virtual ~FilledBufferStrategy(void) override = default;
        virtual void execute(const StatatisticsBlock::ModelMap &map) override;

        size_t getMaxSize(void) const;

    private:
        std::shared_ptr<Buffer> getBuffer(const StatatisticsBlock::ModelMap &map) const;

    private:
        const std::string name;
        size_t max_size = 0;
};

class AwaitBufferStrategy : public StatatisticsBlock::Strategy
{
    public:
        AwaitBufferStrategy(std::list<std::string> names);
        virtual ~AwaitBufferStrategy(void) override = default;
        virtual void execute(const StatatisticsBlock::ModelMap &map) override;

        double getAvgAwait(void) const;

    private:
        std::list<std::shared_ptr<TaskRequest>> getRequests(const StatatisticsBlock::ModelMap &map) const;
        std::list<std::shared_ptr<Terminator>> getTerminators(const StatatisticsBlock::ModelMap &map) const;

    private:
        std::list<std::string> names;
        std::list<std::shared_ptr<TaskRequest>> requsts;
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

