#ifndef _TIME_MODELS_H_
#define _TIME_MODELS_H_

#include "time_model.h"

#include "random.h"

#include "basic_pipe.h"
#include "generator.h"
#include "buffer.h"
#include "processor.h"
#include "terminator.h"
#include "gate.h"
#include "block_statistics.h"

class PipeTimeModel : public TimeModel
{
    public:
        PipeTimeModel(std::shared_ptr<Pipe> pipe);
        virtual ~PipeTimeModel(void) override = default;
        virtual size_t priority(void) override;
        virtual void tick(double time) override;
        virtual void setModifier(std::shared_ptr<RequestModifier> modifier) override;

    private:
        std::shared_ptr<Pipe> pipe;
};

class BufferTimeModel : public TimeModel
{
    public:
        BufferTimeModel(std::shared_ptr<Buffer> buffer);
        virtual ~BufferTimeModel(void) override = default;
        virtual size_t priority(void) override;
        virtual void tick(double time) override;
        virtual void setModifier(std::shared_ptr<RequestModifier> modifier) override;

    private:
        std::shared_ptr<Buffer> buffer;
};

class GeneratorTimeModel : public TimeModel
{
    public:
        GeneratorTimeModel(std::shared_ptr<Generator> generator,
                           std::shared_ptr<RequestCreator> creator,
                           std::shared_ptr<Random> random);
        virtual ~GeneratorTimeModel(void) override = default;
        virtual size_t priority(void) override;
        virtual void tick(double time) override;
        virtual void setModifier(std::shared_ptr<RequestModifier> modifier) override;

    private:
        std::shared_ptr<Generator> generator;
        std::shared_ptr<Random> random;
        double next;
};

class ProcessorTimeModel : public TimeModel
{
    public:
        ProcessorTimeModel(std::shared_ptr<Processor> processor,
                           std::shared_ptr<Random> random);
        virtual ~ProcessorTimeModel(void) override = default;
        virtual size_t priority(void) override;
        virtual void tick(double time) override;
        virtual void setModifier(std::shared_ptr<RequestModifier> modifier) override;

    private:
        std::shared_ptr<Processor> processor;
        std::shared_ptr<Random> random;
        double next;
};

class TerminatorTimeModel : public TimeModel
{
    public:
        TerminatorTimeModel(std::shared_ptr<Terminator> terminator);
        virtual ~TerminatorTimeModel(void) override = default;
        virtual size_t priority(void) override;
        virtual void tick(double time) override;
        virtual void setModifier(std::shared_ptr<RequestModifier> modifier) override;

    private:
        std::shared_ptr<Terminator> terminator;
};

class GateTimeModel : public TimeModel
{
    public:
        using RedirectFunc = \
        const std::string &(*)(const std::list<std::string> &names,
                               double time);

    public:
        GateTimeModel(std::shared_ptr<Gate> gate, RedirectFunc func);
        virtual ~GateTimeModel(void) override = default;
        virtual size_t priority(void) override;
        virtual void tick(double time) override;
        virtual void setModifier(std::shared_ptr<RequestModifier> modifier) override;

    private:
        std::shared_ptr<Gate> gate;
        RedirectFunc func;
};

class StatatisticsBlockTimeModel : public TimeModel
{
    public:
        StatatisticsBlockTimeModel(std::shared_ptr<StatatisticsBlock> block,
                                   double interval);
        virtual ~StatatisticsBlockTimeModel(void) override = default;
        virtual size_t priority(void) override;
        virtual void tick(double time) override;
        virtual void setModifier(std::shared_ptr<RequestModifier> modifier) override;

    private:
        std::shared_ptr<StatatisticsBlock> block;
        double next;
        const double interval;
};

#endif

