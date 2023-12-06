#ifndef _TYPESTRING_H_
#define _TYPESTRING_H_

#include <string>

namespace TypeName
{
    template <typename Type>
    const std::string &get(void);

    template <typename Type>
    std::string getAttribute(const std::string attribute);
}

#include "typestring.hpp"

#endif

