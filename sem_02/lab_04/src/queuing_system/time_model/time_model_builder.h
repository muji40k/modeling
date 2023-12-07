#ifndef _TIME_MODEL_BUILDER_H_
#define _TIME_MODEL_BUILDER_H_

#include <unordered_map>

#include "random.h"

#include "builder.h"
#include "time_model.h"
#include "time_models.h"

class TimeModelCreator
{
    public:
        virtual ~TimeModelCreator(void) = default;
        virtual bool check(std::shared_ptr<Model> model) const = 0;
        virtual std::shared_ptr<TimeModel> create(std::shared_ptr<Model> model) const = 0;
};

class TimeRunnerBuilder : public RunnerBuilder
{
    public:
        virtual ~TimeRunnerBuilder(void) override = default;
        virtual void create(void) override;
        virtual RunnerBuilder &addModel(std::shared_ptr<Model> model) override;
        virtual std::shared_ptr<Runner> result(void) override;

        TimeRunnerBuilder &setRequests(size_t val);
        TimeRunnerBuilder &setTimeLimit(double val);
        TimeRunnerBuilder &setTimeStep(double val);
        TimeRunnerBuilder &setTimeRequestModifier(std::shared_ptr<TimeRequestModifier> val);

        TimeRunnerBuilder &registerModelCreator(std::shared_ptr<TimeModelCreator> creator);

    private:
        std::shared_ptr<Runner> runner = nullptr;
        size_t requests = 0;
        double time_limit = 0;
        double step = 0;
        std::shared_ptr<TimeRequestModifier> modifier;
        std::list<std::shared_ptr<TimeModel>> models;
        std::list<std::shared_ptr<TimeModelCreator>> creators;
};

namespace TimeRunnerBuilderMisc
{
    using RandomMap = std::unordered_map<std::string, std::shared_ptr<Random>>;
    using RedirectMap = std::unordered_map<std::string, GateTimeModel::RedirectFunc>;
}

// Creators

class PipeTimeModelCreator : public TimeModelCreator
{
    public:
        virtual ~PipeTimeModelCreator(void) override = default;
        virtual bool check(std::shared_ptr<Model> model) const override;
        virtual std::shared_ptr<TimeModel> create(std::shared_ptr<Model> model) const override;
};

class BufferTimeModelCreator : public TimeModelCreator
{
    public:
        virtual ~BufferTimeModelCreator(void) override = default;
        virtual bool check(std::shared_ptr<Model> model) const override;
        virtual std::shared_ptr<TimeModel> create(std::shared_ptr<Model> model) const override;
};

class GeneratorTimeModelCreator : public TimeModelCreator
{
    public:
        using RandomMap = TimeRunnerBuilderMisc::RandomMap;

    public:
        GeneratorTimeModelCreator(RandomMap random,
                                  std::shared_ptr<RequestCreator> creator);
        virtual ~GeneratorTimeModelCreator(void) override = default;
        virtual bool check(std::shared_ptr<Model> model) const override;
        virtual std::shared_ptr<TimeModel> create(std::shared_ptr<Model> model) const override;

    private:
        RandomMap map;
        std::shared_ptr<RequestCreator> creator;
};

class ProcessorTimeModelCreator : public TimeModelCreator
{
    public:
        using RandomMap = TimeRunnerBuilderMisc::RandomMap;

    public:
        ProcessorTimeModelCreator(RandomMap random);
        virtual ~ProcessorTimeModelCreator(void) override = default;
        virtual bool check(std::shared_ptr<Model> model) const override;
        virtual std::shared_ptr<TimeModel> create(std::shared_ptr<Model> model) const override;

    private:
        RandomMap map;
};

class TerminatorTimeModelCreator : public TimeModelCreator
{
    public:
        virtual ~TerminatorTimeModelCreator(void) override = default;
        virtual bool check(std::shared_ptr<Model> model) const override;
        virtual std::shared_ptr<TimeModel> create(std::shared_ptr<Model> model) const override;
};

class GateTimeModelCreator : public TimeModelCreator
{
    public:
        using RedirectMap = TimeRunnerBuilderMisc::RedirectMap;

    public:
        GateTimeModelCreator(RedirectMap map);
        virtual ~GateTimeModelCreator(void) override = default;
        virtual bool check(std::shared_ptr<Model> model) const override;
        virtual std::shared_ptr<TimeModel> create(std::shared_ptr<Model> model) const override;

    private:
        RedirectMap map;
};

class StatisticsBlockTimeModelCreator : public TimeModelCreator
{
    public:
        StatisticsBlockTimeModelCreator(size_t interval);
        virtual ~StatisticsBlockTimeModelCreator(void) override = default;
        virtual bool check(std::shared_ptr<Model> model) const override;
        virtual std::shared_ptr<TimeModel> create(std::shared_ptr<Model> model) const override;

    private:
        const size_t interval;
};

#endif

