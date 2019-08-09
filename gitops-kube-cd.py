import argparse
import subprocess
import os
from jinja2 import Template

parser = argparse.ArgumentParser(description="Kxubernets devops tool")
parser.add_argument("--commit-sha", '-c', help="commit sha id", type=str, required=True)
parser.add_argument("--name",  '-n', help="project name represent in k8s service", type=str, required=True)
parser.add_argument("--base-registry-dir", '-b', help="base registry directory of your image", type=str, required=True)
parser.add_argument("--mode", '-m', help="build or push image", type=str, required=False, choices=['push', 'build', 'build-push'], default="build-push")
parser.add_argument("--branch", '-B', help="branch name", type=str, required=True)


args = parser.parse_args()
try:
    ENV = __import__("gitops-kube-env")
except Exception as err:
    print(err)
    ENV = None


def short_sha(x):
    return x[:8]


def render_yaml(fs, env):
    template = Template(fs)
    return template.render(**env)


def generate_tag(base_registry_dir, name, short_commit_sha):
    return "%s:%s" % (os.path.join(base_registry_dir,name), short_commit_sha)


def get_env():
    env = {
        'APP_NAME': args.name,
        'BRANCH_NAME': args.branch,
        'IMAGE_PATH': generate_tag(args.base_registry_dir, args.name, short_sha(args.commit_sha))
    }
    for x in args.__dict__:
        env[x] = args.__getattribute__(x)
    if ENV:
        for x in dir(ENV):
            if not x.startswith("_"):
                env[x] = getattr(ENV, x)
    return env


def get_deployment_tmpl(fn="gitops-kube-config/deployment.yaml"):
    with open(fn) as fd:
        fs = fd.read()
    return fs


def kubctl_apply(fn):
    print("kubectl apply -f %s" % fn)
    print(subprocess.call("pwd"))
    assert subprocess.call("kubectl apply -f %s" % fn, shell=True) == 0
    assert subprocess.call("kubectl rollout status -f %s" % fn, shell=True) == 0


def deploy():
    env = get_env()
    tf = render_yaml(get_deployment_tmpl(), env)
    tmp_yaml_name = '%s_deployment.yaml' % args.name
    with open(tmp_yaml_name, 'w') as fd:
        fd.write(tf.encode())
        fd.flush()
    kubctl_apply(tmp_yaml_name)
    os.remove(tmp_yaml_name)


if __name__ == "__main__":
    deploy()