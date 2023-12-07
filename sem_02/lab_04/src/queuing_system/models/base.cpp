#include "base.h"

Model::Model(std::string name) : name(name), modifier(nullptr) {}
Model::~Model(void) {}

const std::string &Model::getName(void) const
{
    return this->name;
}

void Model::setModifier(std::shared_ptr<RequestModifier> modifier)
{
    this->modifier = modifier;
}

std::shared_ptr<RequestModifier> Model::getModifier(void) const
{
    return this->modifier;
}

Request::~Request(void) {}

Pipe::Pipe(std::string name) : Model(name) {}

Receiver::Receiver(std::shared_ptr<Pipe> pipe) : _inpipe(pipe) {}
Receiver::~Receiver(void) {}

void Receiver::connectInPipe(std::shared_ptr<Pipe> pipe)
{
    this->_inpipe = pipe;
}

std::shared_ptr<Pipe> Receiver::inpipe(void)
{
    return this->_inpipe;
}

void Receiver::askSender(void)
{
    for (auto sender : this->_senders)
        if (sender)
            sender->callback();
}

void Receiver::registerSender(std::shared_ptr<Sender> sender)
{
    if (sender)
        this->_senders.push_back(sender);
}

Sender::Sender(std::shared_ptr<Pipe> pipe) : _outpipe(pipe) {}
Sender::~Sender(void) {}

void Sender::connectOutPipe(std::shared_ptr<Pipe> pipe)
{
    this->_outpipe = pipe;
}

std::shared_ptr<Pipe> Sender::outpipe(void)
{
    return this->_outpipe;
}

