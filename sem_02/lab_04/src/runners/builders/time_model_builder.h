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

        TimeRunnerBuilder &registerModelCreator(std::shared_ptr<TimeModelCreator> creator);

    private:
        std::shared_ptr<Runner> runner = nullptr;
        size_t requests = 0;
        double time_limit = 0;
        double step = 0;
        std::list<std::shared_ptr<TimeModel>> models;
        std::list<std::shared_ptr<TimeModelCreator>> creators;
};

using RandomMap = std::unordered_map<std::string, std::shared_ptr<Random>>;

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
        GeneratorTimeModelCreator(RandomMap random);
        virtual ~GeneratorTimeModelCreator(void) override = default;
        virtual bool check(std::shared_ptr<Model> model) const override;
        virtual std::shared_ptr<TimeModel> create(std::shared_ptr<Model> model) const override;

    private:
        RandomMap map;
};

class ProcessorTimeModelCreator : public TimeModelCreator
{
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
        using RedirectMap = std::unordered_map<std::string, GateTimeModel::RedirectFunc>;

    public:
        GateTimeModelCreator(RedirectMap map);
        virtual ~GateTimeModelCreator(void) override = default;
        virtual bool check(std::shared_ptr<Model> model) const override;
        virtual std::shared_ptr<TimeModel> create(std::shared_ptr<Model> model) const override;

    private:
        RedirectMap map;
};

#endif

