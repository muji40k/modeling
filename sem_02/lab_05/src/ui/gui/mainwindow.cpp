#include "mainwindow.h"

#include "uniform_screen.h"
#include "constant_screen.h"

#include "uniform.h"
#include "normal.h"

#include "time_task.h"
#include "event_task.h"

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent),
      ui(QSharedPointer<Ui_MainWindow>::create())
{
    this->ui->setupUi(this);

    this->genscreen = QSharedPointer<UniformScreen>::create(8, 12, this);
    this->op1screen = QSharedPointer<UniformScreen>::create(15, 25, this);
    this->op2screen = QSharedPointer<UniformScreen>::create(30, 50, this);
    this->op3screen = QSharedPointer<UniformScreen>::create(20, 60, this);
    this->proc1screen = QSharedPointer<ConstantScreen>::create(15, this);
    this->proc2screen = QSharedPointer<ConstantScreen>::create(30, this);

    this->ui->verticalLayout_4->addWidget(this->genscreen.get());
    this->ui->verticalLayout_3->addWidget(this->op1screen.get());
    this->ui->verticalLayout_7->addWidget(this->op2screen.get());
    this->ui->verticalLayout_10->addWidget(this->op3screen.get());
    this->ui->verticalLayout_8->addWidget(this->proc1screen.get());
    this->ui->verticalLayout_9->addWidget(this->proc2screen.get());

    this->ui->tableWidget_result->setItem(0, 0, new QTableWidgetItem());
    this->ui->tableWidget_result->setItem(1, 0, new QTableWidgetItem());
    this->ui->tableWidget_result->setItem(2, 0, new QTableWidgetItem());
    this->ui->tableWidget_result->setItem(3, 0, new QTableWidgetItem());
    this->ui->tableWidget_result->setItem(4, 0, new QTableWidgetItem());

    this->ui->comboBox_mode->addItem(QString("Дельта t"),
                                     QVariant::fromValue(&MainWindow::makeTimeBuilder));
    this->ui->comboBox_mode->addItem(QString("Событийный"),
                                     QVariant::fromValue(&MainWindow::makeEventBuilder));

    QObject::connect(this->ui->pushButton_process, SIGNAL(clicked()),
                     this, SLOT(onButtonClicked()));
}

void MainWindow::onButtonClicked(void)
{
    this->runSimulation();
}

void MainWindow::runSimulation(void)
{
    const size_t iter = this->ui->spinBox_measures->value();
    const double tick = this->ui->doubleSpinBox_time_step->value();

    double sum_total = 0, sum_await = 0, sum_lost = 0, max_lost = 0;
    double sum_lost_amount = 0;

    for (size_t i = 0; iter > i; i++)
    {
        auto terminatorstrat = std::make_shared<TerminatorStrategy>(std::list<std::string>({"terminator1", "terminator2"}), std::list<std::string>({"terminator2"}));
        auto tickstrat = std::make_shared<TickCountStrategy>();

        run_task(this->getBuilder({terminatorstrat, tickstrat}));

        sum_total += tick * tickstrat->getTicks();
        sum_await += terminatorstrat->getAvgAwait();
        sum_lost += terminatorstrat->getLostProbability();
        max_lost = std::max(max_lost, terminatorstrat->getLostProbability());
        sum_lost_amount += terminatorstrat->getLost();
    }

    this->ui->tableWidget_result->item(0, 0)->setText(QString::number(sum_total / iter));
    this->ui->tableWidget_result->item(1, 0)->setText(QString::number(sum_await / iter));
    this->ui->tableWidget_result->item(2, 0)->setText(QString::number(sum_lost / iter));
    this->ui->tableWidget_result->item(3, 0)->setText(QString::number(max_lost));
    this->ui->tableWidget_result->item(4, 0)->setText(QString::number(sum_lost_amount / iter));
}

std::shared_ptr<RunnerBuilder> MainWindow::getBuilder(std::list<std::shared_ptr<StatatisticsBlock::Strategy>> list) const
{
    Method method = this->ui->comboBox_mode->currentData().value<Method>();

    if (nullptr == method)
        return nullptr;

    return (this->*method)(list);
}

std::shared_ptr<RunnerBuilder> MainWindow::makeEventBuilder(std::list<std::shared_ptr<StatatisticsBlock::Strategy>> list) const
{
    EventRunnerBuilderMisc::RandomMap random =
    {
        {"generator", this->genscreen->parseRandom()},
        {"operator1", this->op1screen->parseRandom()},
        {"operator2", this->op2screen->parseRandom()},
        {"operator3", this->op3screen->parseRandom()},
        {"processor1", this->proc1screen->parseRandom()},
        {"processor2", this->proc2screen->parseRandom()}
    };

    EventRunnerBuilderMisc::RedirectMap redirect = {};
    const double step = this->ui->doubleSpinBox_time_step->value();
    const double sustep = 0.1 * step;

    EventRunnerBuilderMisc::IntervalMap interval =
    {
        {"pipe1", LinearIntervals(step - sustep, step)},
        {"pipe2", LinearIntervals(step - sustep, step)},
        {"pipe3", LinearIntervals(step - sustep, step)},
        {"pipe4", LinearIntervals(step - sustep, step)},
        {"pipe5", LinearIntervals(step - sustep, step)},
        {"pipe6", LinearIntervals(step - sustep, step)},
        {"generator", LinearIntervals(step, step)},
        {"buffer1", LinearIntervals(step, step)},
        {"buffer2", LinearIntervals(step, step)},
        {"processor1", LinearIntervals(step, step)},
        {"processor2", LinearIntervals(step, step)},
        {"operator1", LinearIntervals(step, step)},
        {"operator2", LinearIntervals(step, step)},
        {"operator3", LinearIntervals(step, step)},
        {"terminator1", LinearIntervals(step + sustep, step)},
        {"terminator2", LinearIntervals(step + sustep, step)},
        {"stats", LinearIntervals(step + 2 * sustep, step)}
    };

    EventRunnerBuilderMisc::StatisticsMap statistics = {{"stats", list}};

    event_setup setup =
    {
        std::make_shared<TaskRequestCreator>(),
        (size_t)this->ui->spinBox_reqeusts->value(),
        this->ui->doubleSpinBox_time_limit->value(),
        std::make_shared<TaskEventRequestModifier>(std::make_shared<ChronoRequestModifier>()),
        interval,
        random,
        redirect,
        statistics
    };

    return getEventBuilder(setup);
}

std::shared_ptr<RunnerBuilder> MainWindow::makeTimeBuilder(std::list<std::shared_ptr<StatatisticsBlock::Strategy>> list) const
{
    TimeRunnerBuilderMisc::RandomMap random =
    {
        {"generator", this->genscreen->parseRandom()},
        {"operator1", this->op1screen->parseRandom()},
        {"operator2", this->op2screen->parseRandom()},
        {"operator3", this->op3screen->parseRandom()},
        {"processor1", this->proc1screen->parseRandom()},
        {"processor2", this->proc2screen->parseRandom()}
    };

    TimeRunnerBuilderMisc::RedirectMap redirect = {};
    TimeRunnerBuilderMisc::StatisticsMap statistics = {{"stats", list}};

    time_setup setup =
    {
        std::make_shared<TaskRequestCreator>(),
        (size_t)this->ui->spinBox_reqeusts->value(),
        this->ui->doubleSpinBox_time_limit->value(),
        this->ui->doubleSpinBox_time_step->value(),
        std::make_shared<TaskTimeRequestModifier>(std::make_shared<ChronoRequestModifier>()),
        random,
        redirect,
        statistics
    };

    return getTimeBuilder(setup);
}

#include "moc_mainwindow.cpp"

