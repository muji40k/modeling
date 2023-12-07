#ifndef _BUILDER_H_
#define _BUILDER_H_

#include "base.h"

class RunnerBuilder
{
    public:
        virtual ~RunnerBuilder(void) = default;
        virtual void create(void) = 0;
        virtual RunnerBuilder &addModel(std::shared_ptr<Model> model) = 0;
        virtual std::shared_ptr<Runner> result(void) = 0;
};

#endif

