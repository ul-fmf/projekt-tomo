import os

from fabric.api import *

LOCAL_ROOT = os.path.dirname(os.path.realpath(__file__))
LOCAL_VIRTUALENV = "~/.virtualenv/tomo"
TOMO_HOST = "www.projekt-tomo.si"

env.hosts = [TOMO_HOST]


# MAIN TASKS


@task
def test():
    with lcd(LOCAL_ROOT), activate_virtualenv():
        with lcd("web"):
            local("./manage.py test")


@task
def deploy():
    with cd("/home/gregor/docker/"):
        sudo("docker-compose pull")
        sudo("docker-compose up -d")
    migrate()


@task
def quick_deploy():
    tomo_docker('bash -c "cd projekt-tomo && git pull"')
    migrate()
    manage("collectstatic --noinput")
    tomo_docker("uwsgi --reload /tmp/project-master.pid")


@task
def migrate():
    manage("migrate")


@task
def ls():
    manage("help")


# AUXILLIARY FUNCTIONS


def activate_virtualenv():
    return prefix("source {}/bin/activate".format(LOCAL_VIRTUALENV))


def manage(command):
    tomo_docker("python3 projekt-tomo/web/manage.py {}".format(command))


def tomo_docker(command):
    sudo("docker exec docker_tomo_1 {}".format(command))
