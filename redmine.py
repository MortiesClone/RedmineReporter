import httplib
import json

def read_params():
    raw_params = file('params.json', 'r').read()
    return json.loads(raw_params)

def decode_resp(response):
    data = response.read()
    # print data
    return json.loads(data)

class HTTP(object):
    def __init__(self, url):
        self._clear()
        self.conn = httplib.HTTPSConnection(url)

    def set_headers(self, headers):
        self.headers = headers

    def set_queryparams(self, queryparams):
        self.queryparams = queryparams

    def set_body(self, body):
        self.body = body

    def set_method(self, method):
        self.method = method

    def set_path(self, path):
        self.path = path

    def request(self):
        path = self.path
        if self.queryparams:
            path += self._query_params_to_str()
        self.conn.request(self.method, path, self.body or {}, self.headers or {})
        response = self.conn.getresponse()
        print self.method, path, response.status

        self._clear()
        
        return response

    def _clear(self):
        self.headers = None
        self.queryparams = None
        self.body = None
        self.method = None
        self.path = None

    def _query_params_to_str(self):
        result_str = '?'
        for key in self.queryparams:
            result_str += key + '=' + self.queryparams[key] + '&'
        return result_str


class RedmineAPI(object):
    def __init__(self, url, api_key):
        self.api_key = api_key
        self.http = HTTP(url)

    def _set_queryparams(self, params):
        base = {'key': self.api_key}
        base.update(params)
        self.http.set_queryparams(base)

    def current_user(self):
        self.http.set_method('GET')
        self.http.set_path('/users/current.json')
        self._set_queryparams({})
        return self.http.request()

    def time_entries(self, user_id, from_time, to_time):
        self.http.set_method('GET')
        self.http.set_path('/time_entries.json')
        self._set_queryparams({
            'user_id': str(user_id),
            'from': from_time,
            'to': to_time
        })
        return self.http.request()

    def issues(self, ids, status_id):
        self.http.set_method('GET')
        self.http.set_path('/issues.json')
        self._set_queryparams({
            'issue_id': self._ids_to_str(ids),
            'status_id': status_id
        })
        return self.http.request()

    def _ids_to_str(self, ids):
        result_str = ''
        for i in range(len(ids)):
            result_str += str(ids[i])
            if i != len(ids) - 1:
                result_str += ','
        return result_str

params = read_params()
redmine = RedmineAPI(params['url'], params['api_key'])

current_user = decode_resp(redmine.current_user())

# time entries
teresponse = redmine.time_entries(current_user['user']['id'], params['from'], params['to'])
time_entries = decode_resp(teresponse)

# issues
issues_ids = [time_entrie['issue']['id'] for time_entrie in time_entries['time_entries']]
issues = decode_resp(redmine.issues(issues_ids, '*'))

# print report
print 'Done:'
for issue in issues['issues']:
    print '#' + str(issue['id']), issue['subject']

