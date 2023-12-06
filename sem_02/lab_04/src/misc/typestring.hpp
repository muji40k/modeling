#ifndef _TYPESTRING_HPP_
#define _TYPESTRING_HPP_

#include "typestring.h"

#include <typeinfo>

template <typename Type>
const std::string &TypeName::get(void)
{
    static const std::string name = typeid(Type).name();

    return name;
}

template <typename Type>
std::string TypeName::getAttribute(const std::string attribute)
{
    return TypeName::get<Type>() + "." + attribute;
}

#endif

