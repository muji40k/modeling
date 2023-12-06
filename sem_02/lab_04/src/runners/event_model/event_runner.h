#ifndef _EVENT_RUNNER_H_
#define _EVENT_RUNNER_H_

#include <map>

#include "base.h"
#include "event_model.h"

class EventRunner : public Runner
{
    public:
        EventRunner(size_t requests, double time,
                   std::list<std::shared_ptr<EventModel>> items);
        virtual ~EventRunner(void) override = default;

        virtual void run(void) override;

    private:
        const size_t requests;
        const double end;
        std::list<std::shared_ptr<EventModel>> items;
};


#endif

