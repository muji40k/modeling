#ifndef _BUFFER_H_
#define _BUFFER_H_

#include <list>
#include <memory>
#include <string>
#include <mutex>

#include "base.h"

class Buffer : public Model, public Sender, public Receiver
{
    public:
        Buffer(std::string name, const size_t size,
               std::shared_ptr<Pipe> inpipe, std::shared_ptr<Pipe> outpipe);
        virtual ~Buffer(void) override = default;

        virtual size_t read(void);
        virtual size_t send(size_t amount = 1);

        virtual size_t used(void) const;

        virtual void callback(void) override;

    private:
        const size_t size;
        std::list<std::shared_ptr<Request>> memory;
        std::mutex mutex;
};

#endif

