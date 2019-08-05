import argparse
import subprocess
import os
parser = argparse.ArgumentParser(description="Kxubernets devops tool")
parser.add_argument("--commit-sha", '-c', help="commit sha id", type=str, required=True)
parser.add_argument("--name",  '-n', help="project name represent in k8s service", type=str, required=True)
parser.add_argument("--base-registry-dir", '-b', help="base registry directory of your image", type=str, required=True)
parser.add_argument("--mode", '-m', help="build or push image", type=str, required=False, choices=['push', 'build', 'build-push'], default="build-push")


args = parser.parse_args()


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
    if args.mode == 'build':
        build(tag)
    elif args.mode == 'push':
        push(tag)
    else:
        build(tag)
        push(tag)
