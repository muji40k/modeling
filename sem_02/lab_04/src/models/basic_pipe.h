#ifndef _BASIC_PIPE_H_
#define _BASIC_PIPE_H_

#include <list>
#include <memory>
#include <mutex>

#include "base.h"

class BasicPipe : public Pipe
{
    public:
        BasicPipe(std::string name);
        virtual ~BasicPipe(void) override = default;

        virtual bool push(std::shared_ptr<Request> request) override;
        virtual std::shared_ptr<Request> pop(void) override;

        virtual void newSet(void) override;
        virtual void dropCurrentSet(void) override;
        virtual void clear(void) override;

    private:
        std::mutex mutex;
        std::list<std::list<std::shared_ptr<Request>>> sets;
};

#endif

