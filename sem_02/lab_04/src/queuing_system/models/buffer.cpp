#include "buffer.h"

Buffer::Buffer(std::string name, const size_t size,
               std::shared_ptr<Pipe> inpipe, std::shared_ptr<Pipe> outpipe)
    : Model(name), Sender(outpipe), Receiver(inpipe), size(size)
{}

size_t Buffer::read(void)
{
    std::shared_ptr<RequestModifier> modifier = this->getModifier();
    std::shared_ptr<Pipe> inpipe = this->inpipe();
    size_t count = 0;

    if (0 != this->size && this->size == this->memory.size())
        return count;

    for (std::shared_ptr<Request> current = inpipe->pop(); current;)
    {
        this->memory.push_back(current);
        count++;

        if (modifier)
            modifier->modify(current, *this, "read");

        if (0 != this->size && this->size == this->memory.size())
            current = nullptr;
        else
            current = inpipe->pop();
    }

    return count;
}

size_t Buffer::send(size_t amount)
{
    if (0 == amount)
        return 0;

    this->mutex.lock();

    if (this->memory.size() < amount)
        amount = this->memory.size();

    std::shared_ptr<RequestModifier> modifier = this->getModifier();
    std::shared_ptr<Pipe> outpipe = this->outpipe();
    std::shared_ptr<Request> request = nullptr;

    for (size_t i = 0; amount > i; i++)
    {
        request = this->memory.front();
        this->memory.pop_front();
        outpipe->push(request);

        if (modifier)
            modifier->modify(request, *this, "send");
    }

    this->mutex.unlock();

    return amount;
}

size_t Buffer::used(void) const
{
    return this->memory.size();
}

void Buffer::callback(void)
{
    this->mutex.lock();

    if (0 != this->memory.size())
    {
        std::shared_ptr<RequestModifier> modifier = this->getModifier();
        std::shared_ptr<Pipe> outpipe = this->outpipe();
        std::shared_ptr<Request> request = this->memory.front();
        this->memory.pop_front();
        outpipe->push(request);

        if (modifier)
            modifier->modify(request, *this, "callback");
    }

    this->mutex.unlock();
}

