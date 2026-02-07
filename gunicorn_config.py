import multiprocessing
import os

# Bind to the port provided by Render
bind = f"0.0.0.0:{os.environ.get('PORT', '5000')}"

# Worker configuration - OPTIMIZED FOR RENDER FREE TIER (512MB RAM)
workers = 1              # CHANGED: Reduced from 2 to prevent out-of-memory errors
worker_class = 'sync'
worker_connections = 1000
timeout = 300            # CHANGED: Increased from 120 to 300 for image processing
keepalive = 5

# Memory management - PREVENT MEMORY LEAKS
max_requests = 100       # NEW: Restart worker after 100 requests
max_requests_jitter = 20 # NEW: Add randomness to prevent all workers restarting together

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
    print(f"✅ Workers: {workers} (optimized for free tier)")
    print(f"✅ Timeout: {timeout}s (for image processing)")
    print("=" * 60)

def on_exit(server):
    print("=" * 60)
    print("👋 Server shutting down...")
    print("=" * 60)
