import requests
import os
import json
from urllib.parse import urljoin


class NotFound(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class KClient:
    def __init__(self, url, token, namespaces=[]):
        self.url = url
        self.token = token
        self.namespaces = namespaces
        self.check_include = len(self.namespaces) > 0
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer %s" % self.token
        }

    @staticmethod
    def configmap_template(name, data):
        template = {
            "kind": "ConfigMap",
            "apiVersion": "v1",
            "metadata": {
                "name": name
            },
            "data": data
        }
        return template

    def namespace_exist(self, namespace):
        url = urljoin(self.url, "/api/v1/namespaces/%s" % namespace)
        r = requests.get(url, verify=False, headers=self.headers)
        if r.status_code == 404:
            return False
        elif r.status_code == 200:
            return True
        else:
            raise Exception("namespace_exist %s failed" % namespace)

    def configmap_get(self, namespace, configmap):
        url = urljoin(self.url, "/api/v1/namespaces/%s/configmaps/%s" % (namespace, configmap))
        r = requests.get(url, verify=False, headers=self.headers)
        if r.status_code == 200:
            return r.json()
        elif r.status_code == 404:
            raise NotFound(r.text)
        else:
            raise Exception("namespace_exist %s failed" % namespace)

    def configmap_create(self, namespace, configmap, data):
        data_new = KClient.configmap_template(name=configmap, data=data)
        url = urljoin(self.url, "/api/v1/namespaces/%s/configmaps" % (namespace))
        r = requests.post(url, verify=False, headers=self.headers, data=json.dumps(data_new))
        if r.status_code == 201:
            return True
        else:
            raise Exception(r.text)

    def configmap_update(self, namespace, configmap, data):
        data_new = KClient.configmap_template(name=configmap, data=data)
        url = urljoin(self.url, "/api/v1/namespaces/%s/configmaps/%s" % (namespace, configmap))
        r = requests.put(url, verify=False, headers=self.headers, data=json.dumps(data_new))
        if r.status_code == 200:
            return True
        else:
            raise Exception(r.text)

    def configmap_sync(self, namespace, configmap, data):
        try:
            self.configmap_get(namespace, configmap)
        except NotFound:
            self.configmap_create(namespace, configmap, data)
        else:
            self.configmap_update(namespace, configmap, data)

    def configmap_delete(self):
        raise NotImplementedError

    def list_namespace_dir(self, file_dir="."):
        r = []
        for directory in os.listdir(file_dir):
            new_path = os.path.join(file_dir, directory)
            if os.path.isdir(new_path):
                if self.check_include and directory not in self.namespaces:
                    continue
                r.append(directory)
        return r

    def list_configmap_dir(self, namespace_dir):
        r = []
        for directory in os.listdir(namespace_dir):
            new_path = os.path.join(namespace_dir, directory)
            if os.path.isdir(new_path):
                r.append(directory)
        return r

    def list_file(self, directory):
        r = []
        for filename in os.listdir(directory):
            new_path = os.path.join(directory, filename)
            if os.path.isfile(new_path):
                r.append(filename)
        return r

    def sync(self):
        for namespace in k.list_namespace_dir():
            for configmap in k.list_configmap_dir(namespace):
                new_path = os.path.join(namespace, configmap)
                configmap_data = KClient.convert_dir_to_configmap_data(new_path)
                self.configmap_sync(namespace, configmap, configmap_data)

    @staticmethod
    def convert_dir_to_configmap_data(configmap_path):
        data = {}
        files = k.list_file(configmap_path)
        for fn in files:
            tmp_file_path = os.path.join(configmap_path, fn)
            with open(tmp_file_path, 'r') as fd:
                data[fn] = fd.read()
        return data


if __name__ == '__main__':
    url = "https://10.115.5.158:6443"
    token = "eyJhbGciOiJSUzI1NiIsImtpZCI6IiJ9.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJrdWJlLXN5c3RlbSIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VjcmV0Lm5hbWUiOiJhZG1pbi11c2VyLXRva2VuLXZzeHA2Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQubmFtZSI6ImFkbWluLXVzZXIiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC51aWQiOiIzM2FjZGU2Zi0zMTk1LTRiMmItYjBhMi1hNTg2YzJlY2E1YWEiLCJzdWIiOiJzeXN0ZW06c2VydmljZWFjY291bnQ6a3ViZS1zeXN0ZW06YWRtaW4tdXNlciJ9.n6ki73kgQaMwVb5c5R7baIznUs-90Fej5oxN1UUNcPERjBqmJI4FDPfSbyeKz0OMv6IrbyXooJbew3YDIcunUC1-fn2V1Fka2eJ-zWuQlBHSTUzSpowR-M_4uS5KsF-pTr2CqSymF_Ohx0f5gNHptLygUqUdryfyb6cACX68mZYIfMZyi_dWA9lkP3g2__Lb-k6h9YebSwBU-ZWf0QfIXJOt-LKNDYeKrjAnueCxy9Xe0IpVAeKQwwyvg3I5Zdr0QTmhBmgQeFlzo9FFdHgACDh53H9ckPCgY5tTdlaqGXL28Vn137Iu90OeZPJ4A5sNCqFbPObge08uX8hrb7eQAw"
    ns = ['test-namespace']
    k = KClient(url=url, token=token, namespaces=ns)
    k.sync()
