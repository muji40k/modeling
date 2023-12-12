#include "constant_screen.h"

#include "constant.h"

ConstantScreen::ConstantScreen(double value,  QWidget *parent)
    : Screen(parent), ui(QSharedPointer<Ui_constant_screen>::create())
{
    this->ui->setupUi(this);
    this->ui->doubleSpinBox_val->setValue(value);
}

std::shared_ptr<Random> ConstantScreen::parseRandom(void)
{
    return std::make_shared<ConstantRandom>(this->ui->doubleSpinBox_val->value());
}

#include "moc_constant_screen.cpp"

