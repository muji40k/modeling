#ifndef _BLOCK_STATISTICS_H_
#define _BLOCK_STATISTICS_H_

#include <memory>
#include <string>

#include "base.h"

class StatatisticsBlock : public Model
{
    public:
        class Strategy
        {
            public:
                virtual ~Strategy(void) = default;
                virtual void execute(void) = 0;
        };

    public:
        StatatisticsBlock(std::string name);
        virtual ~StatatisticsBlock(void) override = default;

        virtual void registerStrategy(std::shared_ptr<Strategy> strategy);
        virtual void write(void);

    private:
        std::list<std::shared_ptr<Strategy>> strategies;
};

#endif

