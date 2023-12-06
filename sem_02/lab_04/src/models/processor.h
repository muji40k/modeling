#ifndef _PROCESSOR_H_
#define _PROCESSOR_H_

#include <memory>
#include <string>

#include "base.h"

class Processor : public Model, public Sender, public Receiver
{
    public:
        Processor(std::string name,
                  std::shared_ptr<Pipe> inpipe = nullptr,
                  std::shared_ptr<Pipe> outpipe = nullptr);
        virtual ~Processor(void) override = default;

        virtual bool read(void);
        virtual bool isActive(void) const;
        virtual bool release(void);

        virtual void callback(void) override;

    private:
        std::shared_ptr<Request> active = nullptr;
        std::list<std::shared_ptr<Request>> current;
};

#endif

