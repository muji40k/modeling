#include "constant.h"

ConstantRandom::ConstantRandom(double value) : value(value) {}
double ConstantRandom::generate(void) { return this->value; }

