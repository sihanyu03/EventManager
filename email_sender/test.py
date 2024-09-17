import yaml
import os


project_path = '/Users/sihanyu/Documents/Programming/Github/EventManager'

try:
    with open(os.path.join(project_path, 'database_details.yaml'), 'r') as file:
        d = yaml.safe_load(file)
    print(d)
except yaml.YAMLError:
    print('caught')
