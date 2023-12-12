#ifndef _UNIFORM_SCREEN_H_
#define _UNIFORM_SCREEN_H_

#include "screen.h"

#include "ui_uniform_screen.h"

class UniformScreen : public Screen
{
    public:
        UniformScreen(double min, double max, QWidget *parent = nullptr);
        virtual ~UniformScreen(void) override = default;
        virtual std::shared_ptr<Random> parseRandom(void) override;

    private:
        QSharedPointer<Ui_uniform_screen> ui = nullptr;
};


#endif

