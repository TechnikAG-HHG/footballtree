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
                r'code/new/mykey',
                '-o',
                'ServerAliveInterval=600',
                '-o',
                'TCPKeepAlive=no',
                'serveo.net'
            ])
        except subprocess.CalledProcessError as e:
            print(f"Connection lost. Reason: {str(e)}. Retrying...")
            for i in range(5):  # Retry 5 times
                time.sleep(5)  # Wait for 5 seconds before retrying
                try:
                    subprocess.check_call([
                        'ssh',
                        '-R',
                        'technikag:80:127.0.0.1:5000',
                        '-i',
                        r'code/new/mykey',
                        '-o',
                        'ServerAliveInterval=600',
                        '-o',
                        'TCPKeepAlive=no',
                        'serveo.net'
                    ])
                    break  # If connection is successful, break the loop
                except subprocess.CalledProcessError:
                    continue  # If connection is still unsuccessful, continue to the next iteration
            else:
                continue  # If all retries failed, continue to the next iteration of the outer loop

maintain_connection()