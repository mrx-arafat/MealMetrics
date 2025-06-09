#!/usr/bin/env python3
"""
SSH Tunnel setup for MySQL connection
"""

import subprocess
import sys
import time
import socket
from utils.config import Config

def check_port_open(host, port):
    """Check if a port is open"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

def setup_ssh_tunnel():
    """Setup SSH tunnel for MySQL connection"""
    config = Config()
    
    print("🔧 Setting up SSH Tunnel for MySQL...")
    print("=" * 50)
    
    # Check if local port is already in use
    if check_port_open('localhost', int(config.MYSQL_PORT)):
        print(f"⚠️  Port {config.MYSQL_PORT} is already in use!")
        print("This might mean the tunnel is already running.")
        return True
    
    # SSH tunnel command
    ssh_command = [
        'ssh',
        '-N',  # Don't execute remote command
        '-L', f"{config.MYSQL_PORT}:localhost:{config.SSH_MYSQL_PORT}",  # Local port forwarding
        f"{config.SSH_USER}@{config.SSH_HOST}",
        '-o', 'StrictHostKeyChecking=no',
        '-o', 'UserKnownHostsFile=/dev/null'
    ]
    
    print(f"🔄 Creating SSH tunnel...")
    print(f"   Local port: {config.MYSQL_PORT}")
    print(f"   Remote: {config.SSH_HOST}:{config.SSH_MYSQL_PORT}")
    print(f"   SSH User: {config.SSH_USER}")
    print()
    print("📝 Command to run manually:")
    print(f"ssh -N -L {config.MYSQL_PORT}:localhost:{config.SSH_MYSQL_PORT} {config.SSH_USER}@{config.SSH_HOST}")
    print()
    print("⚠️  You'll need to enter your SSH password when prompted.")
    print("⚠️  Keep this terminal open while using the bot!")
    print()
    
    try:
        # Start SSH tunnel
        process = subprocess.Popen(ssh_command, 
                                 stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
        
        # Wait a moment for tunnel to establish
        time.sleep(3)
        
        # Check if tunnel is working
        if check_port_open('localhost', int(config.MYSQL_PORT)):
            print("✅ SSH tunnel established successfully!")
            print(f"✅ MySQL is now accessible on localhost:{config.MYSQL_PORT}")
            return True
        else:
            print("❌ SSH tunnel failed to establish")
            return False
            
    except FileNotFoundError:
        print("❌ SSH command not found!")
        print("🔧 Please install OpenSSH client or use PuTTY")
        return False
    except Exception as e:
        print(f"❌ SSH tunnel failed: {e}")
        return False

if __name__ == "__main__":
    success = setup_ssh_tunnel()
    if success:
        print("\n🎉 SSH tunnel is ready!")
        print("🚀 Now you can run: python test_mysql_connection.py")
        print("🚀 Or start the bot with: python main.py")
        print("\n⚠️  Keep this terminal open while using the bot!")
        
        # Keep the script running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 SSH tunnel closed.")
    else:
        print("\n❌ Failed to setup SSH tunnel")
        sys.exit(1)
