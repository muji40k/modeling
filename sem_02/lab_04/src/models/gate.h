#ifndef _GATE_H_
#define _GATE_H_

#include <list>
#include <memory>
#include <string>

#include "base.h"

class Gate : public Model, public Receiver
{
    public:
        class Out : public Model, public Sender
        {
            public:
                Out(std::string name, std::shared_ptr<Pipe> outpipe);
                virtual ~Out(void) override = default;

                virtual bool send(std::shared_ptr<Request> request);

                virtual void callback(void) override;
        };

    public:
        Gate(std::string name, std::shared_ptr<Pipe> inpipe,
             std::list<std::shared_ptr<Pipe>> outpipes);
        virtual ~Gate(void) override = default;

        virtual void setModifier(std::shared_ptr<RequestModifier> modifier) override;

        virtual bool read(void);
        virtual bool redirect(std::string name);
        virtual const std::list<std::string> &list(void);

    private:
        std::list<std::shared_ptr<Out>> outs;
        std::list<std::string> names;
        std::shared_ptr<Request> current = nullptr;
};

#endif

