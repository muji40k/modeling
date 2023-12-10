#include "terminator.h"

Terminator::Terminator(std::string name, std::shared_ptr<Pipe> inpipe)
    : Model(name), Receiver(inpipe)
{}

void Terminator::read(void)
{
    std::shared_ptr<Pipe> inpipe = this->inpipe();
    std::shared_ptr<RequestModifier> modifier = this->getModifier();

    for (std::shared_ptr<Request> request; (request = inpipe->pop());)
    {
        this->done.push_back(request);

        if (modifier)
            modifier->modify(request, *this, "read");
    }
}

std::list<std::shared_ptr<Request>> Terminator::getDone(void)
{
    std::list<std::shared_ptr<Request>> out = this->done;
    this->done.clear();

    return out;
}

