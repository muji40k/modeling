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

class EventModelRequestCreator : public RequestCreator
{
    public:
        virtual ~EventModelRequestCreator(void) override = default;
        virtual std::shared_ptr<Request> create(void) override;

    private:
        size_t current = 0;
};

class PipeEventModel : public EventModel
{
    public:
        PipeEventModel(std::shared_ptr<Pipe> pipe);
        virtual ~PipeEventModel(void) override = default;
        virtual size_t priority(void) override;
        virtual void tick(double time) override;
        virtual void setModifier(std::shared_ptr<RequestModifier> modifier) override;

    private:
        std::shared_ptr<Pipe> pipe;
};

class BufferEventModel : public EventModel
{
    public:
        BufferEventModel(std::shared_ptr<Buffer> buffer);
        virtual ~BufferEventModel(void) override = default;
        virtual size_t priority(void) override;
        virtual void tick(double time) override;
        virtual void setModifier(std::shared_ptr<RequestModifier> modifier) override;

    private:
        std::shared_ptr<Buffer> buffer;
};

class GeneratorEventModel : public EventModel
{
    public:
        GeneratorEventModel(std::shared_ptr<Generator> generator,
                           std::shared_ptr<Random> random);
        virtual ~GeneratorEventModel(void) override = default;
        virtual size_t priority(void) override;
        virtual void tick(double time) override;
        virtual void setModifier(std::shared_ptr<RequestModifier> modifier) override;

    private:
        std::shared_ptr<Generator> generator;
        std::shared_ptr<Random> random;
        double next;

    private:
        static std::shared_ptr<EventModelRequestCreator> creator;
};

class ProcessorEventModel : public EventModel
{
    public:
        ProcessorEventModel(std::shared_ptr<Processor> processor,
                           std::shared_ptr<Random> random);
        virtual ~ProcessorEventModel(void) override = default;
        virtual size_t priority(void) override;
        virtual void tick(double time) override;
        virtual void setModifier(std::shared_ptr<RequestModifier> modifier) override;

    private:
        std::shared_ptr<Processor> processor;
        std::shared_ptr<Random> random;
        double next;
};

class TerminatorEventModel : public EventModel
{
    public:
        TerminatorEventModel(std::shared_ptr<Terminator> terminator);
        virtual ~TerminatorEventModel(void) override = default;
        virtual size_t priority(void) override;
        virtual void tick(double time) override;
        virtual void setModifier(std::shared_ptr<RequestModifier> modifier) override;

    private:
        std::shared_ptr<Terminator> terminator;
};

class GateEventModel : public EventModel
{
    public:
        using RedirectFunc = \
        const std::string &(*)(const std::list<std::string> &names,
                               double time);

    public:
        GateEventModel(std::shared_ptr<Gate> gate, RedirectFunc func);
        virtual ~GateEventModel(void) override = default;
        virtual size_t priority(void) override;
        virtual void tick(double time) override;
        virtual void setModifier(std::shared_ptr<RequestModifier> modifier) override;

    private:
        std::shared_ptr<Gate> gate;
        RedirectFunc func;
};

#endif

