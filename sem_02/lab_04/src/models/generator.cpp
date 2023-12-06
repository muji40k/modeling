#include "generator.h"

Generator::Generator(std::string name, std::shared_ptr<Pipe> outpipe)
    : Model(name), Sender(outpipe)
{}

void Generator::setCreator(std::shared_ptr<RequestCreator> creator)
{
    this->cretator = creator;
}

void Generator::generate(const size_t amount)
{
    if (0 == amount)
        return;

    std::shared_ptr<Pipe> outpipe = this->outpipe();
    std::shared_ptr<RequestModifier> modifier = this->getModifier();

    for (size_t i = 0; amount > i; i++)
    {
        std::shared_ptr<Request> request = this->cretator->create();
        outpipe->push(request);

        if (modifier)
            modifier->modify(request, *this, "generate");
    }
}

void Generator::callback(void)
{}

