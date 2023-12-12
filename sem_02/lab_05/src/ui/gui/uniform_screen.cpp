#include "uniform_screen.h"

#include "uniform.h"

UniformScreen::UniformScreen(double min, double max, QWidget *parent)
    : Screen(parent), ui(QSharedPointer<Ui_uniform_screen>::create())
{
    this->ui->setupUi(this);
    this->ui->doubleSpinBox_min->setValue(min);
    this->ui->doubleSpinBox_max->setValue(max);
}

std::shared_ptr<Random> UniformScreen::parseRandom(void)
{
    return std::make_shared<UniformRandom>(this->ui->doubleSpinBox_min->value(),
                                           this->ui->doubleSpinBox_max->value());
}

#include "moc_uniform_screen.cpp"

