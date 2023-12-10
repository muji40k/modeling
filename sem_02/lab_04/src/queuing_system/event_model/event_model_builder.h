#ifndef _EVENT_MODEL_BUILDER_H_
#define _EVENT_MODEL_BUILDER_H_

#include <unordered_map>

#include "random.h"

#include "builder.h"
#include "event_model.h"
#include "event_models.h"

class EventModelCreator
{
    public:
        virtual ~EventModelCreator(void) = default;
        virtual bool check(std::shared_ptr<Model> model) const = 0;
        virtual std::shared_ptr<EventModel> create(std::shared_ptr<Model> model) const = 0;
};

class EventRunnerBuilder : public RunnerBuilder
{
    public:
        using RandomMap = std::unordered_map<std::string, std::shared_ptr<Random>>;

    public:
        virtual ~EventRunnerBuilder(void) override = default;
        virtual void create(void) override;
        virtual RunnerBuilder &addModel(std::shared_ptr<Model> model) override;
        virtual std::shared_ptr<Runner> result(void) override;

        EventRunnerBuilder &setRequests(size_t val);
        EventRunnerBuilder &setTimeLimit(double val);
        EventRunnerBuilder &setEventRequestModifier(std::shared_ptr<EventRequestModifier> val);

        EventRunnerBuilder &registerModelCreator(std::shared_ptr<EventModelCreator> creator);

    private:
        std::shared_ptr<Runner> runner = nullptr;
        size_t requests = 0;
        double time_limit = 0;
        std::shared_ptr<EventRequestModifier> modifier;
        std::list<std::shared_ptr<EventModel>> models;
        std::list<std::shared_ptr<EventModelCreator>> creators;
};

namespace EventRunnerBuilderMisc
{
    using IntervalMap = std::unordered_map<std::string, LinearIntervals>;
    using RandomMap = std::unordered_map<std::string, std::shared_ptr<Random>>;
    using RedirectMap = std::unordered_map<std::string, GateEventModel::RedirectFunc>;
    using StatisticsMap = std::unordered_map<std::string, std::list<std::shared_ptr<StatatisticsBlock::Strategy>>>;
}

// Creators

class PipeEventModelCreator : public EventModelCreator
{
    public:
        using IntervalMap = EventRunnerBuilderMisc::IntervalMap;

    public:
        PipeEventModelCreator(IntervalMap map);
        virtual ~PipeEventModelCreator(void) override = default;
        virtual bool check(std::shared_ptr<Model> model) const override;
        virtual std::shared_ptr<EventModel> create(std::shared_ptr<Model> model) const override;

    private:
        IntervalMap map;
};

class BufferEventModelCreator : public EventModelCreator
{
    public:
        using IntervalMap = EventRunnerBuilderMisc::IntervalMap;

    public:
        BufferEventModelCreator(IntervalMap map);
        virtual ~BufferEventModelCreator(void) override = default;
        virtual bool check(std::shared_ptr<Model> model) const override;
        virtual std::shared_ptr<EventModel> create(std::shared_ptr<Model> model) const override;

    private:
        IntervalMap map;
};

class GeneratorEventModelCreator : public EventModelCreator
{
    public:
        using RandomMap = EventRunnerBuilderMisc::RandomMap;

    public:
        GeneratorEventModelCreator(RandomMap random,
                                   std::shared_ptr<RequestCreator> creator);
        virtual ~GeneratorEventModelCreator(void) override = default;
        virtual bool check(std::shared_ptr<Model> model) const override;
        virtual std::shared_ptr<EventModel> create(std::shared_ptr<Model> model) const override;

    private:
        RandomMap map;
        std::shared_ptr<RequestCreator> creator;
};

class ProcessorEventModelCreator : public EventModelCreator
{
    public:
        using RandomMap = EventRunnerBuilderMisc::RandomMap;
        using IntervalMap = EventRunnerBuilderMisc::IntervalMap;

    public:
        ProcessorEventModelCreator(RandomMap random, IntervalMap interval);
        virtual ~ProcessorEventModelCreator(void) override = default;
        virtual bool check(std::shared_ptr<Model> model) const override;
        virtual std::shared_ptr<EventModel> create(std::shared_ptr<Model> model) const override;

    private:
        RandomMap rmap;
        IntervalMap imap;
};

class TerminatorEventModelCreator : public EventModelCreator
{
    public:
        using IntervalMap = EventRunnerBuilderMisc::IntervalMap;

    public:
        TerminatorEventModelCreator(IntervalMap map);
        virtual ~TerminatorEventModelCreator(void) override = default;
        virtual bool check(std::shared_ptr<Model> model) const override;
        virtual std::shared_ptr<EventModel> create(std::shared_ptr<Model> model) const override;

    private:
        IntervalMap map;
};

class GateEventModelCreator : public EventModelCreator
{
    public:
        using RedirectMap = EventRunnerBuilderMisc::RedirectMap;
        using IntervalMap = EventRunnerBuilderMisc::IntervalMap;

    public:
        GateEventModelCreator(RedirectMap rmap, IntervalMap imap);
        virtual ~GateEventModelCreator(void) override = default;
        virtual bool check(std::shared_ptr<Model> model) const override;
        virtual std::shared_ptr<EventModel> create(std::shared_ptr<Model> model) const override;

    private:
        RedirectMap rmap;
        IntervalMap imap;
};

class StatisticsBlockEventModelCreator : public EventModelCreator
{
    public:
        using IntervalMap = EventRunnerBuilderMisc::IntervalMap;
        using StatisticsMap = EventRunnerBuilderMisc::StatisticsMap;

    public:
        StatisticsBlockEventModelCreator(IntervalMap imap, StatisticsMap smap);
        virtual ~StatisticsBlockEventModelCreator(void) override = default;
        virtual bool check(std::shared_ptr<Model> model) const override;
        virtual std::shared_ptr<EventModel> create(std::shared_ptr<Model> model) const override;

    private:
        IntervalMap imap;
        StatisticsMap smap;
};

#endif

