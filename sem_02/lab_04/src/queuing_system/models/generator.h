#ifndef _GENERATOR_H_
#define _GENERATOR_H_

#include <list>
#include <memory>
#include <string>

#include "base.h"

class RequestCreator
{
    public:
        virtual ~RequestCreator(void) = default;
        virtual std::shared_ptr<Request> create(void) = 0;
};

class Generator : public Model, public Sender
{
    public:
        Generator(std::string name, std::shared_ptr<Pipe> outpipe = nullptr);
        virtual ~Generator(void) override = default;
        virtual void callback(void) override;

        virtual void setCreator(std::shared_ptr<RequestCreator> creator);

        virtual void generate(const size_t amount = 1);

    private:
        std::shared_ptr<RequestCreator> cretator = nullptr;
};

#endif

