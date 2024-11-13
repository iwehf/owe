# Owe Agent Platform


## Getting Started

### Start the server

```bash
$ python run.py
```

### Start the worker

```bash
$ celery -A owe.owe_agent.worker worker --loglevel=INFO
```
