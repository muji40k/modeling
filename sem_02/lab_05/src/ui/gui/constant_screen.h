#ifndef _CONSTANT_SCREEN_H_
#define _CONSTANT_SCREEN_H_

#include "screen.h"

#include "ui_constant_screen.h"

class ConstantScreen : public Screen
{
    public:
        ConstantScreen(double value, QWidget *parent = nullptr);
        virtual ~ConstantScreen(void) override = default;
        virtual std::shared_ptr<Random> parseRandom(void) override;

    private:
        QSharedPointer<Ui_constant_screen> ui = nullptr;
};

#endif

