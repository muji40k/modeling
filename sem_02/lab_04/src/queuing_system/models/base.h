#ifndef _BASE_H_
#define _BASE_H_

#include <memory>
#include <string>
#include <list>

class RequestModifier;

class Model
{
    public:
        Model(std::string name);
        virtual ~Model(void) = 0;

        virtual const std::string &getName(void) const;

        virtual void setModifier(std::shared_ptr<RequestModifier> modifier);
        virtual std::shared_ptr<RequestModifier> getModifier(void) const;

    private:
        const std::string name;
        std::shared_ptr<RequestModifier> modifier;
};

class Request
{
    public:
        virtual ~Request(void) = 0;
};

class RequestModifier
{
    public:
        virtual ~RequestModifier(void) = default;
        virtual void modify(std::shared_ptr<Request> request,
                            const Model &modifier,
                            std::string event) = 0;
};

class Pipe : public Model
{
    public:
        Pipe(std::string name);
        virtual ~Pipe(void) = default;

        virtual bool empty(void) const = 0;
        virtual bool push(std::shared_ptr<Request>) = 0;
        virtual std::shared_ptr<Request> pop(void) = 0;

        virtual void newSet(void) = 0;
        virtual void dropCurrentSet(void) = 0;
        virtual void clear(void) = 0;
};

class Sender;

class Receiver
{
    public:
        Receiver(std::shared_ptr<Pipe> pipe);
        virtual ~Receiver(void) = 0;

        void connectInPipe(std::shared_ptr<Pipe> pipe);
        std::shared_ptr<Pipe> inpipe(void);
        void askSender(void);

        void registerSender(std::shared_ptr<Sender> sender);

    private:
        std::shared_ptr<Pipe> _inpipe;
        std::list<std::shared_ptr<Sender>> _senders;
};

class Sender
{
    public:
        Sender(std::shared_ptr<Pipe> pipe);
        virtual ~Sender(void) = 0;

        void connectOutPipe(std::shared_ptr<Pipe> pipe);
        std::shared_ptr<Pipe> outpipe(void);

        virtual void callback(void) = 0;

    private:
        std::shared_ptr<Pipe> _outpipe;
};

class Runner
{
    public:
        virtual ~Runner(void) = default;
        virtual void run(void) = 0;
};

#endif

