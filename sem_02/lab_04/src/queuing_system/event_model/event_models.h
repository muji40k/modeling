#ifndef _EVENT_MODELS_H_
#define _EVENT_MODELS_H_

#include "event_model.h"

#include "random.h"

#include "basic_pipe.h"
#include "generator.h"
#include "buffer.h"
#include "processor.h"
#include "terminator.h"
#include "gate.h"
#include "block_statistics.h"

struct LinearIntervals
{
    public:
        double start;
        double delay;

    public:
        LinearIntervals(double start, double delay);
        void next(void);
        void reset(void);
        const double &current(void) const;

    private:
        double _current;
};

class PipeEventModel : public EventModel
{
    public:
        PipeEventModel(std::shared_ptr<Pipe> pipe, LinearIntervals intervals);
        virtual ~PipeEventModel(void) override = default;
        virtual void event(void) override;
        virtual double nextEvent(void) const override;
        virtual void generateNextEvent(void) override;
        virtual void setModifier(std::shared_ptr<RequestModifier> modifier) override;

    private:
        std::shared_ptr<Pipe> pipe;
        LinearIntervals intervals;
};

class BufferEventModel : public EventModel
{
    public:
        BufferEventModel(std::shared_ptr<Buffer> buffer,
                         LinearIntervals intervals);
        virtual ~BufferEventModel(void) override = default;
        virtual void event(void) override;
        virtual double nextEvent(void) const override;
        virtual void generateNextEvent(void) override;
        virtual void setModifier(std::shared_ptr<RequestModifier> modifier) override;

    private:
        std::shared_ptr<Buffer> buffer;
        LinearIntervals intervals;
};

class GeneratorEventModel : public EventModel
{
    public:
        GeneratorEventModel(std::shared_ptr<Generator> generator, 
                            std::shared_ptr<RequestCreator> creator,
                            std::shared_ptr<Random> random);
        virtual ~GeneratorEventModel(void) override = default;
        virtual void event(void) override;
        virtual double nextEvent(void) const override;
        virtual void generateNextEvent(void) override;
        virtual void setModifier(std::shared_ptr<RequestModifier> modifier) override;

    private:
        std::shared_ptr<Generator> generator;
        std::shared_ptr<Random> random;
        double next;
};


class ProcessorEventModel : public EventModel
{
    public:
        ProcessorEventModel(std::shared_ptr<Processor> processor,
                            std::shared_ptr<Random> random,
                            LinearIntervals intervals);
        virtual ~ProcessorEventModel(void) override = default;
        virtual void event(void) override;
        virtual double nextEvent(void) const override;
        virtual void generateNextEvent(void) override;
        virtual void setModifier(std::shared_ptr<RequestModifier> modifier) override;

    private:
        std::shared_ptr<Processor> processor;
        std::shared_ptr<Random> random;
        LinearIntervals intervals;
        double last;
        double next;
        bool seq = true;
};

class TerminatorEventModel : public EventModel
{
    public:
        TerminatorEventModel(std::shared_ptr<Terminator> terminator,
                             LinearIntervals intervals);
        virtual ~TerminatorEventModel(void) override = default;
        virtual void event(void) override;
        virtual double nextEvent(void) const override;
        virtual void generateNextEvent(void) override;
        virtual void setModifier(std::shared_ptr<RequestModifier> modifier) override;

    private:
        std::shared_ptr<Terminator> terminator;
        LinearIntervals intervals;
};

class GateEventModel : public EventModel
{
    public:
        using RedirectFunc = \
        const std::string &(*)(const std::list<std::string> &names,
                               double time);

    public:
        GateEventModel(std::shared_ptr<Gate> gate, LinearIntervals intervals,
                       RedirectFunc func);
        virtual ~GateEventModel(void) override = default;
        virtual void event(void) override;
        virtual double nextEvent(void) const override;
        virtual void generateNextEvent(void) override;
        virtual void setModifier(std::shared_ptr<RequestModifier> modifier) override;

    private:
        std::shared_ptr<Gate> gate;
        RedirectFunc func;
        LinearIntervals intervals;
};

class StatatisticsBlockEventModel : public EventModel
{
    public:
        StatatisticsBlockEventModel(std::shared_ptr<StatatisticsBlock> block,
                                    LinearIntervals intervals,
                                    std::list<std::shared_ptr<StatatisticsBlock::Strategy>> strategies);
        virtual ~StatatisticsBlockEventModel(void) override = default;
        virtual void event(void) override;
        virtual double nextEvent(void) const override;
        virtual void generateNextEvent(void) override;
        virtual void setModifier(std::shared_ptr<RequestModifier> modifier) override;

    private:
        std::shared_ptr<StatatisticsBlock> block;
        LinearIntervals intervals;
};

#endif

