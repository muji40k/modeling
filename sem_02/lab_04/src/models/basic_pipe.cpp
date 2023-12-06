#include "basic_pipe.h"

BasicPipe::BasicPipe(std::string name) : Pipe(name) {}

bool BasicPipe::push(std::shared_ptr<Request> request)
{
    this->mutex.lock();
    bool res = true;

    if (0 == this->sets.size())
        res = false;

    if (res && nullptr == request)
        res = false;

    if (res)
        this->sets.back().push_back(request);

    this->mutex.unlock();

    return res;
}

std::shared_ptr<Request> BasicPipe::pop(void)
{
    this->mutex.lock();
    std::shared_ptr<Request> out = nullptr;

    if (0 != this->sets.size())
    {
        std::list<std::shared_ptr<Request>> &top = this->sets.front();

        if (0 != top.size())
        {
            out = top.front();
            top.pop_front();
        }
    }

    this->mutex.unlock();

    return out;
}

void BasicPipe::newSet(void)
{
    this->mutex.lock();
    this->sets.push_back(std::list<std::shared_ptr<Request>>());
    this->mutex.unlock();
}

void BasicPipe::dropCurrentSet(void)
{
    this->mutex.lock();
    this->sets.pop_front();
    this->mutex.unlock();
}

void BasicPipe::clear(void)
{
    this->mutex.lock();
    this->sets.clear();
    this->mutex.unlock();
}

