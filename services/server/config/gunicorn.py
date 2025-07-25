#! /usr/bin/env python3
import os
import multiprocessing

workers = int(os.environ.get("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1))
threads = int(os.environ.get("GUNICORN_THREADS", "4"))
bind = os.environ.get("GUNICORN_BIND", "0.0.0.0:8080")

forwarded_allow_ips = os.environ.get("GUNICORN_FORWARDED_ALLOW_IPS", "127.0.0.1")

secure_scheme_headers = {"X-Forwarded-Proto": "https"}

timeout = int(os.environ.get("GUNICORN_TIMEOUT", "120"))
