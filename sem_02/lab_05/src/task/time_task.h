#ifndef _TIME_TASK_H_
#define _TIME_TASK_H_

#include <memory>

#include "chrono_request.h"
#include "time_model.h"

class TaskTimeRequestModifier : public TimeRequestModifier
{
    public:
        TaskTimeRequestModifier(std::shared_ptr<ChronoRequestModifier> modifier);
        virtual ~TaskTimeRequestModifier(void) override = default;

        virtual void setTime(const double &time) override;
        virtual size_t getPassed(void) override;
        virtual std::shared_ptr<RequestModifier> getModifier(void) override;

    private:
        class Wrap : public RequestModifier
        {
            public:
                Wrap(std::shared_ptr<ChronoRequestModifier> wrapped);
                virtual ~Wrap(void) override = default;

                virtual void modify(std::shared_ptr<Request> request,
                                    const Model &modifier,
                                    std::string event) override;

            public:
                size_t passed = 0;
                std::shared_ptr<ChronoRequestModifier> wrapped;
        };

    private:
        std::shared_ptr<Wrap> modifier;
};

#endif

