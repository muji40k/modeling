#include "processor.h"

Processor::Processor(std::string name, std::shared_ptr<Pipe> inpipe,
                     std::shared_ptr<Pipe> outpipe)
    : Model(name), Sender(outpipe), Receiver(inpipe)
{}

bool Processor::read(void)
{
    if (nullptr != this->active)
        return false;

    if (nullptr == (this->active = this->inpipe()->pop()))
        return false;

    std::shared_ptr<RequestModifier> modifier = this->getModifier();

    if (modifier)
        modifier->modify(this->active, *this, "read");

    return true;
}

bool Processor::isActive(void) const
{
    return nullptr != this->active;
}

bool Processor::release(void)
{
    if (nullptr == this->active)
        return false;

    std::shared_ptr<RequestModifier> modifier = this->getModifier();

    if (modifier)
        modifier->modify(this->active, *this, "release");

    this->outpipe()->push(this->active);
    this->active = nullptr;

    return true;
}

void Processor::callback(void)
{}

