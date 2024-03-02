import subprocess
import time

def maintain_connection():
    while True:
        try:
            subprocess.check_call([
                'ssh',
                '-R',
                'technikag:80:127.0.0.1:5000',
                '-i',
                '\\new\\mykey',
                '-o',
                'ServerAliveInterval=600',
                '-o',
                'TCPKeepAlive=no',
                'serveo.net'
            ])
        except subprocess.CalledProcessError as e:
            print(f"Connection lost. Reason: {str(e)}. Retrying...")
            time.sleep(5)  # Wait for 5 seconds before retrying

maintain_connection()