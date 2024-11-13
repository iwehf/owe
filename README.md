# Owe Agent Platform


## Getting Started

### Start the server

```bash
$ python run.py
```

### Start the workers

```bash
$ celery -A owe.owe_agent.worker worker --loglevel=INFO --queues=llm --pool=threads
$ celery -A owe.owe_agent.worker worker --loglevel=INFO --queues=sd --pool=threads
```
