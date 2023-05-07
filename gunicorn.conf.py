import os

workers = int(os.environ.get("WORKERS", 4))
threads = int(os.environ.get("THREADS", 2))

bind = "0.0.0.0:5000"
worker_class = "gevent"
worker_connections = 1000
timeout = 30
keepalive = 2
