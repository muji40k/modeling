#ifndef _SCREEN_H_
#define _SCREEN_H_

#include <QObject>
#include <QWidget>

#include <memory>

#include "random.h"

class Screen : public QWidget
{
    Q_OBJECT

    public:
        Screen(QWidget *parent = nullptr);
        virtual ~Screen(void) = default;
        virtual std::shared_ptr<Random> parseRandom(void) = 0;
};

#endif

