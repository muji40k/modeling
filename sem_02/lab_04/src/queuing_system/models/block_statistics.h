#ifndef _BLOCK_STATISTICS_H_
#define _BLOCK_STATISTICS_H_

#include <memory>
#include <string>
#include <unordered_map>

#include "base.h"

class StatatisticsBlock : public Model
{
    public:
        using ModelMap = std::unordered_map<std::string, std::shared_ptr<Model>>;
        class Strategy
        {
            public:
                virtual ~Strategy(void) = default;
                virtual void execute(const ModelMap &model) = 0;
        };

    public:
        StatatisticsBlock(std::string name, std::list<std::shared_ptr<Model>> targets);
        virtual ~StatatisticsBlock(void) override = default;

        virtual void registerStrategy(std::shared_ptr<Strategy> strategy);
        virtual void write(void);

    private:
        std::list<std::shared_ptr<Strategy>> strategies;
        ModelMap map;
};

#endif

