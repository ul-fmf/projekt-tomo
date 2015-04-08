import os
from fabric.api import *

LOCAL_ROOT = os.path.dirname(os.path.realpath(__file__))
TOMO_HOST = 'tomo.fmf.uni-lj.si'
TOMO_DIR = '/srv/tomodev/'
TOMO_VIRTUALENV = '/srv/tomodev/virtualenv'

env.hosts = [TOMO_HOST]


# MAIN TASKS

@task
def test():
    with prefix('source ~/.virtualenv/tomo/bin/activate'):
        with lcd(LOCAL_ROOT):
            with lcd('web'):
                local('./manage.py test')


@task
def deploy():
    test()
    transfer_code()
    update_requirements()
    manage('collectstatic --noinput')
    manage('migrate')
    restart()


@task
def reset():
    manage('flush')
    manage('loaddata web/fixtures/*.json')


# AUXILLIARY FUNCTIONS

def activate_virtualenv():
    return prefix('source {}/bin/activate'.format(TOMO_VIRTUALENV))


def manage(command):
    with cd(TOMO_DIR), activate_virtualenv():
        return sudo('web/manage.py {} --settings=web.settings.dev'.format(command))


def transfer_code():
    with lcd(LOCAL_ROOT):
        local('rsync -chavzP --rsync-path="sudo rsync" --exclude-from=.gitignore '
              '--delete web {}:{}'.format(TOMO_HOST, TOMO_DIR))


def update_requirements():
    with cd(TOMO_DIR), activate_virtualenv():
        sudo('pip install -r web/requirements/dev.txt'.format(TOMO_VIRTUALENV))


def restart():
    with cd(TOMO_DIR):
        sudo('touch web/web/wsgi/dev.py')
