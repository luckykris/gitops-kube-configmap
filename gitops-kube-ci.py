import argparse
import subprocess
import os
import sys
parser = argparse.ArgumentParser(description="Kxubernets devops tool")
parser.add_argument("--commit-sha", '-c', help="commit sha id", type=str, required=True)
parser.add_argument("--name",  '-n', help="project name represent in k8s service", type=str, required=True)
parser.add_argument("--base-registry-dir", '-b', help="base registry directory of your image", type=str, required=True)
parser.add_argument("--mode", '-m', help="build or push image", type=str, required=False, choices=['push', 'build', 'build-push'], default="build-push")
parser.add_argument("--user",  '-u', help="registry user", type=str, required=True)
parser.add_argument("--password",  '-p', help="registry password", type=str, required=True)

args = parser.parse_args()


def login(t, u, p):
    r = t.split('/')[0]
    print("docker login %s -u %s -p %s" % (r, u, p))
    assert subprocess.call("docker login %s -u %s -p %s" % (r, u, p), shell=True) == 0


def check_exist(t):
    return subprocess.call("docker pull %s" % t, shell=True) == 0


def generate_tag(base_registry_dir, name, short_commit_sha):
    return "%s:%s" % (os.path.join(base_registry_dir,name), short_commit_sha)


def short_sha(x):
    return x[:8]


def build(t):
    assert subprocess.call("docker build . -t %s" % t, shell=True) == 0


def push(t):
    assert subprocess.call("docker push %s" % t, shell=True) == 0


if __name__ == '__main__':
    tag = generate_tag(args.base_registry_dir, args.name, short_sha(args.commit_sha))
    if check_exist(tag):
        print("image is exist, skip this step")
        sys.exit(0)
    if args.mode == 'build':
        build(tag)
    elif args.mode == 'push':
        login(tag,args.user, args.password)
        push(tag)
    else:
        login(tag, args.user, args.password)
        build(tag)
        push(tag)
