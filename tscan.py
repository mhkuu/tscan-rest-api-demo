from lxml import etree
import requests
from requests.auth import HTTPDigestAuth
import time

USERNAME = ''
PASSWORD = ''
PROJECT_NAME = 'tscantest'

auth = HTTPDigestAuth(USERNAME, PASSWORD)

# Create a new project
BASE_URL = 'https://webservices-lst.science.ru.nl/tscan/{}/'
requests.put(BASE_URL.format(PROJECT_NAME), auth=auth)

# Add an input file
data = {
    'inputtemplate': 'textinput',
    'contents': 'Dit is een test.',
}
requests.post((BASE_URL + 'input/{}').format(PROJECT_NAME, 'test.txt'), data, auth=auth)

# Start running the project with some options (turning off Wopr because that takes some time)
data = {
    'useWopr': 'no',
}
requests.post(BASE_URL.format(PROJECT_NAME), data, auth=auth)

# Retrieve the status, poll every 10 seconds
finished = False
while not finished:
    print('Polling...')
    r = requests.get(BASE_URL.format(PROJECT_NAME), auth=auth)
    if r.status_code == 200:
        tree = etree.fromstring(r.content)
        if int(tree.xpath('/clam/status/@code')[0]) == 2:
            print('Finished!')
            finished = True
            break
        else:
            time.sleep(10)
    else:
        print('Polling failed! Status code: {}'.format(r.status_code))
        break

# Retrieve the output, write to file
if finished:
    r = requests.get((BASE_URL + 'output/{}').format(PROJECT_NAME, 'total.word.csv'), auth=auth)
    with open('out.csv', 'wb') as out:
        out.write(r.content)

# Delete the project
requests.delete(BASE_URL.format(PROJECT_NAME), auth=auth)
