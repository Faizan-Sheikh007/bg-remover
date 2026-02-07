import multiprocessing
import os

# Bind to the port provided by Render
bind = f"0.0.0.0:{os.environ.get('PORT', '5000')}"

# Worker configuration
workers = 2
worker_class = 'sync'
worker_connections = 1000
timeout = 120
keepalive = 5

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# Process naming
proc_name = 'background-removal-api'

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# Preload app for faster worker spawn
preload_app = True

# Server hooks
def on_starting(server):
    print("=" * 60)
    print("🚀 Background Removal API Server Starting...")
    print("=" * 60)

def when_ready(server):
    print("=" * 60)
    print("✅ Server is ready and accepting connections!")
    print(f"✅ Listening on: {bind}")
    print("=" * 60)

def on_exit(server):
    print("=" * 60)
    print("👋 Server shutting down...")
    print("=" * 60)
