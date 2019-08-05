import argparse
parser = argparse.ArgumentParser(description="Kxubernets devops tool")
parser.add_argument("commit-sha", help="commit sha id", type=str, required=True)
parser.add_argument("name",  help="project name represent in k8s service", type=str, required=True)
parser.add_argument("namespace",  help="project name represent in k8s service", type=str, required=True)
parser.add_argument("name",  help="project name represent in k8s service", type=str, required=True)

args = parser.parse_args()
