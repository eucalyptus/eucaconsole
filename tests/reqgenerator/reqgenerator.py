# dependencies
# pip install requests cachecontrol beautifulsoup4

from datetime import datetime
import random
import requests
import sys
import time
from threading import Thread
from bs4 import BeautifulSoup
from cachecontrol import CacheControl

# note, when using localhost and port, cache never filled.
URL = 'http://dak-logging-elb-000562685431.lb.a-02.autoqa.qa1.eucalyptus-systems.com/'
NUM_USERS = 50
NUM_ITERATIONS = 100


class UserSession(object):
    """
    Class representing a user session. Meant to be extended for actual user behavior
    """
    session_active = False

    def __init__(self, url, session, name='', iterations=10):
        self.url = url
        self.session = session
        self.name = name
        self.iterations = iterations

    def get_csrf_token_from_page(self, page):
        idx1 = page.text.find('csrf_token')
        idx2 = page.text[idx1:].find('value')
        return page.text[idx1 + idx2 + 7:idx1 + idx2 + 47]

    def get_page_completely(self, url):
        start = datetime.now()
        page = self.session.get(url, verify=False)
        if self.session_active and page.text.find("login-form") > -1:
            self.session_active = False
            self.login('ui-test-acct-00', 'admin', 'mypassword0')
        # now find img, link, script tags
        soup = BeautifulSoup(page.text, 'html.parser')
        images = [img['src'] for img in soup.findAll('img') if img.has_attr('src')]
        scripts = [script['src'] for script in soup.findAll('script') if script.has_attr('src')]
        links = [link['href'] for link in soup.findAll('link') if link.has_attr('href')]
        # fetch resources
        url = self.url
        if url.endswith('/'):
            url = url[:len(url)-1]
        for i in images:
            self.session.get(url + i, verify=False)
        for s in scripts:
            self.session.get(url + s, verify=False)
        for l in links:
            self.session.get(url + l, verify=False)
        end = datetime.now()
        page.elapsed = end - start
        # print "cache size = "+str(len(self.session.adapters['http://'].cache.data))
        return page

    def login(self, account, user, password):
        login_fields = {
            'account': account,
            'username': user,
            'password': password,
            'came_from': '/'
        }
        # TODO: switch to requests.auth ?
        page = self.get_page_completely(self.url)
        csrf_token = self.get_csrf_token_from_page(page)
        login_fields['csrf_token'] = csrf_token
        self.session.post(self.url + 'login?login_type=Eucalyptus', data=login_fields)
        # TODO: return login status
        self.session_active = True

    def logout(self):
        pass

    def __call__(self):
        pass


class BrowsingUser(UserSession):
    pages = [
        'images',
        'instances',
        'volumes',
        'snapshots',
        'keypairs',
        'securitygroups',
        'scalinggroups',
        'users',
        'stacks'
    ]

    def __call__(self):
        for i in range(self.iterations):
            page_name = self.pages[random.randrange(len(self.pages))]
            page = self.get_page_completely(self.url + page_name)
            load_time = page.elapsed.total_seconds()
            csrf_token = self.get_csrf_token_from_page(page)
            page = self.session.post(self.url + page_name + '/json', data={'csrf_token': csrf_token})
            load_time = load_time + page.elapsed.total_seconds()
            print "{0} loading page: {1} took {2} seconds".format(self.name, page_name, load_time)
            time.sleep(random.randrange(1, 20))


class VolumeManipulatorUser(UserSession):
    def __call__(self):
        for i in range(self.iterations):
            # create volume
            page = self.session.get(self.url + 'volumes/new')
            csrf_token = self.get_csrf_token_from_page(page)
            create_fields = {
                'name': 'testvolfor{0}'.format(self.name),
                'size': '1',
                'zone': 'one'
            }
            create_fields['csrf_token'] = csrf_token
            self.session.post(self.url + 'volumes/create', data=create_fields)

if __name__ == "__main__":
    requests.packages.urllib3.disable_warnings()
    url = URL
    num_users = NUM_USERS
    num_iterations = NUM_ITERATIONS
    if len(sys.argv) > 1:
        url = sys.argv[1]
        if len(sys.argv) > 2:
            num_users = int(sys.argv[2])
            if len(sys.argv) > 3:
                num_iterations = int(sys.argv[3])
    else:
        print "usage: reqgenerator.py <console-url> [num sessions] [num iterations/session]"
        sys.exit()
    # start a bunch of users
    for i in range(0, num_users):
        s = requests.Session()
        s = CacheControl(s)
        print "Starting user: " + str(i)
        u = BrowsingUser(url, s, 'user' + str(i), num_iterations)
        u.login('ui-test-acct-00', 'admin', 'mypassword0')
        Thread(target=u).start()
        time.sleep(2)

