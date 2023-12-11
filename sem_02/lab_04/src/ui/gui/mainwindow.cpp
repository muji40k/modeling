#include "mainwindow.h"

#include "uniform.h"
#include "normal.h"

#include "time_task.h"
#include "event_task.h"

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent),
      ui(QSharedPointer<Ui_MainWindow>::create())
{
    this->ui->setupUi(this);

    this->ui->tableWidget_result->setItem(0, 0, new QTableWidgetItem());
    this->ui->tableWidget_result->setItem(1, 0, new QTableWidgetItem());
    this->ui->tableWidget_result->setItem(2, 0, new QTableWidgetItem());
    this->ui->tableWidget_result->setItem(3, 0, new QTableWidgetItem());

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

    double sum_total = 0, sum_await = 0,
           sum_buffer = 0;
    size_t max_buffer = 0;

    for (size_t i = 0; iter > i; i++)
    {
        auto bufstrat = std::make_shared<FilledBufferStrategy>("buffer");
        auto awaitstrat = std::make_shared<AwaitBufferStrategy>(std::list<std::string>({"terminator1", "terminator2", "terminator3"}));
        auto tickstrat = std::make_shared<TickCountStrategy>();

        run_task(this->getBuilder({bufstrat, awaitstrat, tickstrat}));

        sum_total += tick * tickstrat->getTicks();
        sum_await += awaitstrat->getAvgAwait();
        sum_buffer += bufstrat->getMaxSize();
        max_buffer = std::max(max_buffer, bufstrat->getMaxSize());
    }

    this->ui->tableWidget_result->item(0, 0)->setText(QString::number(sum_total / iter));
    this->ui->tableWidget_result->item(1, 0)->setText(QString::number(sum_buffer / iter));
    this->ui->tableWidget_result->item(2, 0)->setText(QString::number(max_buffer));
    this->ui->tableWidget_result->item(3, 0)->setText(QString::number(sum_await / iter));
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
        {"generator", std::make_shared<UniformRandom>(this->ui->doubleSpinBox_gen_min->value(), this->ui->doubleSpinBox_gen_max->value())},
        {"processor", std::make_shared<NormalRandom>(this->ui->doubleSpinBox_proc_mean->value(), this->ui->doubleSpinBox_proc_sdev->value())}
    };

    set_probability(this->ui->doubleSpinBox_gate_prob->value());

    EventRunnerBuilderMisc::RedirectMap redirect =
    {
        {"gate", redirect_func}
    };

    const double step = this->ui->doubleSpinBox_time_step->value();
    const double sustep = 0.1 * step;

    EventRunnerBuilderMisc::IntervalMap interval =
    {
        {"pipe1", LinearIntervals(step - sustep, step)},
        {"pipe2", LinearIntervals(step - sustep, step)},
        {"pipe3", LinearIntervals(step - sustep, step)},
        {"pipe4", LinearIntervals(step - sustep, step)},
        {"buffer", LinearIntervals(step, step)},
        {"processor", LinearIntervals(step, step)},
        {"gate", LinearIntervals(step, step)},
        {"terminator1", LinearIntervals(step + sustep, step)},
        {"terminator2", LinearIntervals(step + sustep, step)},
        {"terminator3", LinearIntervals(step + sustep, step)},
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
        {"generator", std::make_shared<UniformRandom>(this->ui->doubleSpinBox_gen_min->value(), this->ui->doubleSpinBox_gen_max->value())},
        {"processor", std::make_shared<NormalRandom>(this->ui->doubleSpinBox_proc_mean->value(), this->ui->doubleSpinBox_proc_sdev->value())}
    };

    TimeRunnerBuilderMisc::RedirectMap redirect =
    {
        {"gate", redirect_func}
    };

    set_probability(this->ui->doubleSpinBox_gate_prob->value());

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

