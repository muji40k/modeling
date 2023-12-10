#ifndef _CHRONO_REQUEST_H_
#define _CHRONO_REQUEST_H_

#include <mutex>

#include "base.h"
#include "generator.h"

class ChronoRequest : public Request
{
    public:
        ChronoRequest(size_t index);
        virtual ~ChronoRequest(void) override = default;

        size_t getIndex(void) const;

        virtual void addEvent(std::string modelname, double time, std::string event) = 0;

    private:
        const size_t index;
};

class ChronoRequestModifier : public RequestModifier
{
    public:
        virtual ~ChronoRequestModifier(void) override = default;
        virtual void modify(std::shared_ptr<Request> request,
                            const Model &modifier,
                            std::string event) override;
        void setTime(const double &time);

    private:
        const double *time = nullptr;
};

#endif

