import os
import re

def set_new_interval(directory, new_interval):
    for filename in os.listdir(directory):
        if filename.endswith(".js"):
            with open(os.path.join(directory, filename), 'r+') as file:
                content = file.read()
                content_new = re.sub(r'setInterval\(updateData, \d+\)', f'setInterval(updateData, {new_interval})', content)

                if content != content_new:
                    file.seek(0)
                    file.write(content_new)
                    file.truncate()

set_new_interval('./code/static', 10000)  # Replace './' with your directory and 10000 with your new interval