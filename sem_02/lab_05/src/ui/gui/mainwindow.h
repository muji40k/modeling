#ifndef _MAINWINDOW_H_
#define _MAINWINDOW_H_

#include <list>

#include <QObject>
#include <QSharedPointer>
#include <QMainWindow>

#include "builder.h"
#include "common_task.h"

#include "screen.h"

#include "ui_mainwindow.h"

class MainWindow : public QMainWindow
{
    Q_OBJECT

    public:
        MainWindow(QWidget *parent = nullptr);

    private slots:
        void onButtonClicked(void);

    public:
        using Method = std::shared_ptr<RunnerBuilder> (MainWindow::*)(std::list<std::shared_ptr<StatatisticsBlock::Strategy>>) const;

    private:
        void runSimulation(void);
        std::shared_ptr<RunnerBuilder> getBuilder(std::list<std::shared_ptr<StatatisticsBlock::Strategy>>) const;
        std::shared_ptr<RunnerBuilder> makeEventBuilder(std::list<std::shared_ptr<StatatisticsBlock::Strategy>>) const;
        std::shared_ptr<RunnerBuilder> makeTimeBuilder(std::list<std::shared_ptr<StatatisticsBlock::Strategy>>) const;


    private:
        QSharedPointer<Ui_MainWindow> ui = nullptr;
        QSharedPointer<Screen> genscreen = nullptr;
        QSharedPointer<Screen> op1screen = nullptr;
        QSharedPointer<Screen> op2screen = nullptr;
        QSharedPointer<Screen> op3screen = nullptr;
        QSharedPointer<Screen> proc1screen = nullptr;
        QSharedPointer<Screen> proc2screen = nullptr;
};

Q_DECLARE_METATYPE(MainWindow::Method)

#endif

