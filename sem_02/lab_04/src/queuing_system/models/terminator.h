#ifndef _TERMINATOR_H_
#define _TERMINATOR_H_

#include <memory>
#include <string>

#include "base.h"

class Terminator : public Model, public Receiver
{
    public:
        Terminator(std::string name,
                   std::shared_ptr<Pipe> inpipe = nullptr);
        virtual ~Terminator(void) override = default;

        virtual void read(void);
        std::list<std::shared_ptr<Request>> getDone(void);

    private:
        std::list<std::shared_ptr<Request>> done;
};

#endif

