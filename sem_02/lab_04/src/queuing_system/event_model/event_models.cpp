#include "event_models.h"

#include <stdexcept>
#include <cmath>

LinearIntervals::LinearIntervals(double start, double delay)
    : start(start), delay(delay)
{
    this->reset();
}

void LinearIntervals::next(void)
{
    this->_current += this->delay;
}

void LinearIntervals::reset(void)
{
    this->_current = this->start;
}

const double &LinearIntervals::current(void) const
{
    return this->_current;
}

PipeEventModel::PipeEventModel(std::shared_ptr<Pipe> pipe,
                               LinearIntervals intervals)
    : pipe(pipe), intervals(intervals)
{
    if (nullptr == pipe)
        throw std::logic_error("Nullptr occured");

    this->intervals.reset();
    this->pipe->clear();
    this->pipe->newSet();
    this->pipe->newSet();
}

void PipeEventModel::event(void)
{
    if (this->pipe->empty())
        this->pipe->dropCurrentSet();

    this->pipe->newSet();
}

double PipeEventModel::nextEvent(void) const
{
    return this->intervals.current();
}

void PipeEventModel::generateNextEvent(void)
{
    this->intervals.next();
}

void PipeEventModel::setModifier(std::shared_ptr<RequestModifier>)
{}

// ---------------------------------------------------------------------------

BufferEventModel::BufferEventModel(std::shared_ptr<Buffer> buffer,
                                   LinearIntervals intervals)
    : buffer(buffer), intervals(intervals)
{
    if (nullptr == buffer)
        throw std::logic_error("Nullptr occured");
}

void BufferEventModel::event(void)
{
    this->buffer->read();
    this->buffer->askSender();
}

double BufferEventModel::nextEvent(void) const
{
    return this->intervals.current();
}

void BufferEventModel::generateNextEvent(void)
{
    this->intervals.next();
}

void BufferEventModel::setModifier(std::shared_ptr<RequestModifier> modifier)
{
    this->buffer->setModifier(modifier);
}

// ---------------------------------------------------------------------------

GeneratorEventModel::GeneratorEventModel(std::shared_ptr<Generator> generator,  
                                         std::shared_ptr<RequestCreator> creator,
                                         std::shared_ptr<Random> random)
    : generator(generator), random(random)
{
    if (nullptr == generator)
        throw std::logic_error("Nullptr occured");

    this->generator->setCreator(creator);
    this->next = this->random->generate();
}

void GeneratorEventModel::event(void)
{
    this->generator->generate();
}

double GeneratorEventModel::nextEvent(void) const
{
    return this->next;
}

void GeneratorEventModel::generateNextEvent(void)
{
    this->next += this->random->generate();
}

void GeneratorEventModel::setModifier(std::shared_ptr<RequestModifier> modifier)
{
    this->generator->setModifier(modifier);
}

// ---------------------------------------------------------------------------

ProcessorEventModel::ProcessorEventModel(std::shared_ptr<Processor> processor,
                                         std::shared_ptr<Random> random,
                                         LinearIntervals intervals)
    : processor(processor), random(random), intervals(intervals)
{
    if (nullptr == processor || nullptr == random)
        throw std::logic_error("Nullptr occured");

    this->intervals.reset();
    this->last = 0;
    this->next = this->intervals.current();
}

void ProcessorEventModel::event(void)
{
    if (this->processor->isActive())
        this->processor->release();
    else if (!this->processor->read())
        this->processor->askSender();

    this->last = this->next;
}

double ProcessorEventModel::nextEvent(void) const
{
    return this->next;
}

void ProcessorEventModel::generateNextEvent(void)
{
    if (this->processor->isActive())
    {
        this->next = this->last + this->random->generate();
        this->seq = false;
    }
    else if (this->seq)
    {
        this->intervals.next();
        this->next = this->intervals.current();
    }
    else
    {
        LinearIntervals &i = this->intervals;
        double rest = i.delay - std::fmod(this->last - i.current(), i.delay);

        this->intervals.start = this->last + rest;
        this->intervals.reset();
        this->next = this->intervals.current();
        this->seq = true;
    }
}

void ProcessorEventModel::setModifier(std::shared_ptr<RequestModifier> modifier)
{
    this->processor->setModifier(modifier);
}

// ---------------------------------------------------------------------------

TerminatorEventModel::TerminatorEventModel(std::shared_ptr<Terminator> terminator,
                                           LinearIntervals intervals)
    : terminator(terminator), intervals(intervals)
{
    if (nullptr == terminator)
        throw std::logic_error("Nullptr occured");

    this->intervals.reset();
}

void TerminatorEventModel::event(void)
{
    this->terminator->read();
    this->terminator->askSender();
}

double TerminatorEventModel::nextEvent(void) const
{
    return this->intervals.current();
}

void TerminatorEventModel::generateNextEvent(void)
{
    this->intervals.next();
}

void TerminatorEventModel::setModifier(std::shared_ptr<RequestModifier> modifier)
{
    this->terminator->setModifier(modifier);
}

// ---------------------------------------------------------------------------

GateEventModel::GateEventModel(std::shared_ptr<Gate> gate,
                               LinearIntervals intervals,
                               RedirectFunc func)
    : gate(gate), func(func), intervals(intervals)
{
    if (nullptr == gate || nullptr == func)
        throw std::logic_error("Nullptr occured");

    this->intervals.reset();
}

void GateEventModel::event(void)
{
    const auto &list = this->gate->list();

    while (this->gate->read())
    {
        const std::string &target = this->func(list, this->intervals.current());
        this->gate->redirect(target);
    }

    this->gate->askSender();
}

double GateEventModel::nextEvent(void) const
{
    return this->intervals.current();
}

void GateEventModel::generateNextEvent(void)
{
    this->intervals.next();
}

void GateEventModel::setModifier(std::shared_ptr<RequestModifier> modifier)
{
    this->gate->setModifier(modifier);
}

// ---------------------------------------------------------------------------

StatatisticsBlockEventModel::StatatisticsBlockEventModel(std::shared_ptr<StatatisticsBlock> block,
                                                         LinearIntervals intervals,
                                                         std::list<std::shared_ptr<StatatisticsBlock::Strategy>> strategies)
    : block(block), intervals(intervals)
{
    if (nullptr == block)
        throw std::logic_error("Nullptr occured");

    this->intervals.reset();


    for (auto strat : strategies)
    {
        if (nullptr == strat)
            throw std::logic_error("Nullptr occured");

        this->block->registerStrategy(strat);
    }
}

void StatatisticsBlockEventModel::event(void)
{
    this->block->write();
}

double StatatisticsBlockEventModel::nextEvent(void) const
{
    return this->intervals.current();
}

void StatatisticsBlockEventModel::generateNextEvent(void)
{
    this->intervals.next();
}

void StatatisticsBlockEventModel::setModifier(std::shared_ptr<RequestModifier> modifier)
{
    this->block->setModifier(modifier);
}

