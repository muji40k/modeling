#include "time_models.h"

#include <stdexcept>

PipeTimeModel::PipeTimeModel(std::shared_ptr<Pipe> pipe)
    : pipe(pipe)
{
    if (nullptr == pipe)
        throw;

    this->pipe->clear();
    this->pipe->newSet();
    this->pipe->newSet();
}

size_t PipeTimeModel::priority(void)
{
    return 0;
}

void PipeTimeModel::tick(double)
{
    this->pipe->dropCurrentSet();
    this->pipe->newSet();
}

void PipeTimeModel::setModifier(std::shared_ptr<RequestModifier>)
{}

// ---------------------------------------------------------------------------

BufferTimeModel::BufferTimeModel(std::shared_ptr<Buffer> buffer)
    : buffer(buffer)
{
    if (nullptr == buffer)
        throw;
}

size_t BufferTimeModel::priority(void)
{
    return 1;
}

void BufferTimeModel::tick(double)
{
    this->buffer->read();
    this->buffer->askSender();
}

void BufferTimeModel::setModifier(std::shared_ptr<RequestModifier> modifier)
{
    this->buffer->setModifier(modifier);
}

// ---------------------------------------------------------------------------

GeneratorTimeModel::GeneratorTimeModel(std::shared_ptr<Generator> generator,
                                       std::shared_ptr<RequestCreator> creator,
                                       std::shared_ptr<Random> random)
    : generator(generator), random(random)
{
    if (nullptr == generator || nullptr == random || nullptr == creator)
        throw std::logic_error("Nullptr occured");

    this->generator->setCreator(creator);
    this->next = this->random->generate();
}

size_t GeneratorTimeModel::priority(void)
{
    return 1;
}

void GeneratorTimeModel::tick(double time)
{
    while (this->next < time)
    {
        this->generator->generate();
        this->next += this->random->generate();
    }
}

void GeneratorTimeModel::setModifier(std::shared_ptr<RequestModifier> modifier)
{
    this->generator->setModifier(modifier);
}

// ---------------------------------------------------------------------------

ProcessorTimeModel::ProcessorTimeModel(std::shared_ptr<Processor> processor,
                                       std::shared_ptr<Random> random)
    : processor(processor), random(random)
{
    if (nullptr == processor || nullptr == random)
        throw;
}

size_t ProcessorTimeModel::priority(void)
{
    return 1;
}

void ProcessorTimeModel::tick(double time)
{
    if (!this->processor->isActive())
    {
        if (this->processor->read())
            this->next = time + this->random->generate();
        else
            this->processor->askSender();
    }

    while (this->next < time && this->processor->isActive())
    {
        this->processor->release();

        if (this->processor->read())
            this->next += this->random->generate();
        else
            this->processor->askSender();
    }
}

void ProcessorTimeModel::setModifier(std::shared_ptr<RequestModifier> modifier)
{
    this->processor->setModifier(modifier);
}

// ---------------------------------------------------------------------------

TerminatorTimeModel::TerminatorTimeModel(std::shared_ptr<Terminator> terminator)
    : terminator(terminator)
{
    if (nullptr == terminator)
        throw;
}

size_t TerminatorTimeModel::priority(void)
{
    return 2;
}

void TerminatorTimeModel::tick(double)
{
    this->terminator->read();
    this->terminator->askSender();
}

void TerminatorTimeModel::setModifier(std::shared_ptr<RequestModifier> modifier)
{
    this->terminator->setModifier(modifier);
}

// ---------------------------------------------------------------------------

GateTimeModel::GateTimeModel(std::shared_ptr<Gate> gate, RedirectFunc func)
    : gate(gate), func(func)
{
    if (nullptr == gate || nullptr == func)
        throw;
}

size_t GateTimeModel::priority(void)
{
    return 1;
}

void GateTimeModel::tick(double time)
{
    const auto &list = this->gate->list();

    while (this->gate->read())
    {
        const std::string &target = this->func(list, time);
        this->gate->redirect(target);
    }

    this->gate->askSender();
}

void GateTimeModel::setModifier(std::shared_ptr<RequestModifier> modifier)
{
    this->gate->setModifier(modifier);
}

// ---------------------------------------------------------------------------

StatatisticsBlockTimeModel::StatatisticsBlockTimeModel(std::shared_ptr<StatatisticsBlock> block,
                                                       double interval)
    : block(block), interval(interval)
{
    if (nullptr == block)
        throw std::logic_error("Nullptr occured");
}

size_t StatatisticsBlockTimeModel::priority(void)
{
    return 3;
}

void StatatisticsBlockTimeModel::tick(double time)
{
    if (this->next < time)
    {
        this->block->write();
        this->next = time + this->interval;
    }
}

void StatatisticsBlockTimeModel::setModifier(std::shared_ptr<RequestModifier>)
{}

