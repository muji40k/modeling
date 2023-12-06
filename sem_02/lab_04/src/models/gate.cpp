#include "gate.h"

Gate::Out::Out(std::string name, std::shared_ptr<Pipe> outpipe)
    : Model(name), Sender(outpipe)
{}

bool Gate::Out::send(std::shared_ptr<Request> request)
{
    std::shared_ptr<Pipe> outpipe = this->outpipe();
    std::shared_ptr<RequestModifier> modifier = this->getModifier();

    if (nullptr == outpipe)
        return false;

    if (modifier)
        modifier->modify(request, *this, "send");

    return outpipe->push(request);
}

void Gate::Out::callback(void)
{}

Gate::Gate(std::string name, std::shared_ptr<Pipe> inpipe,
           std::list<std::shared_ptr<Pipe>> outpipes)
    : Model(name), Receiver(inpipe)
{
    size_t i = 0;

    for (auto pipe : outpipes)
    {
        std::string nname = name + "_out#" + std::to_string(i++);
        this->outs.push_back(std::make_shared<Out>(nname, pipe));
        this->names.push_back(nname);
    }
}

void Gate::setModifier(std::shared_ptr<RequestModifier> modifier)
{
    this->Model::setModifier(modifier);

    for (auto ptr : this->outs)
        ptr->Model::setModifier(modifier);
}

bool Gate::read(void)
{
    if (nullptr != this->current)
        return false;

    this->current = this->inpipe()->pop();

    if (nullptr == this->current)
        return false;

    std::shared_ptr<RequestModifier> modifier = this->getModifier();

    if (modifier)
        modifier->modify(this->current, *this, "read");

    return true;
}

bool Gate::redirect(std::string name)
{
    auto iter = this->outs.begin();

    for (; this->outs.end() != iter && name != (*iter)->getName(); ++iter);

    if (this->outs.end() == iter)
        return false;

    std::shared_ptr<RequestModifier> modifier = this->getModifier();

    if (modifier)
        modifier->modify(this->current, *this, "redirect");

    bool out = (*iter)->send(this->current);
    this->current = nullptr;

    return out;
}

const std::list<std::string> &Gate::list(void)
{
    return this->names;
}



