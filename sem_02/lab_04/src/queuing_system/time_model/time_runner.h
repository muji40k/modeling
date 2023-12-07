#ifndef _TIME_RUNNER_H_
#define _TIME_RUNNER_H_

#include <map>

#include "base.h"
#include "time_model.h"

class TimeRunner : public Runner
{
    public:
        TimeRunner(size_t requests, double time, double step,
                   std::shared_ptr<TimeRequestModifier> modifier,
                   std::list<std::shared_ptr<TimeModel>> items);
        virtual ~TimeRunner(void) override = default;

        virtual void run(void) override;

    private:
        const size_t requests;
        const double end;
        const double step;
        std::shared_ptr<TimeRequestModifier> modifier;
        std::map<size_t, std::list<std::shared_ptr<TimeModel>>> items;
};

#endif

