import os.path
import tempfile

from fabric.api import *
from fabric.contrib.console import confirm

env.hosts = ['matija@tyrion.fmf.uni-lj.si']

FIXTURES = [
    # 'auth.User',
    'tomo.Course',
    'tomo.ProblemSet',
    # 'tomo.Language',
    'tomo.Problem',
    'tomo.Part',
    # 'tomo.Submission',
    # 'tomo.Attempt',
]

env.srv_directory = '/srv/'
env.project_repository = 'git@git.fmf.uni-lj.si:matijapretnar/projekt-tomo.git'
env.tomo_repository = 'git@github.com:matijapretnar/tomo.git'

@task
def setup():
    with cd(env.srv_directory):
        sudo('git clone {project_repository} {project_name}'.format(**env))
    with cd(env.home):
        sudo('virtualenv --no-site-packages virtualenv')
        with prefix('source virtualenv/bin/activate'):
            sudo('pip install -r requirements/{project_name}.txt'.format(**env))
        sudo('git clone {tomo_repository}'.format(**env))
        sudo('mkdir static')
        with cd('static'):
            sudo('git clone https://github.com/mathjax/MathJax')
    update()

@task
def production():
    set_project('tomoprod')

@task
def std_production():
    set_project('tomostd')

@task
def lock():
    with cd(env.home):
        sudo('touch lock')
    restart()

@task
def unlock():
    with cd(env.home):
        sudo('rm lock')
    restart()

@task
def update():
    lock()
    with cd(env.home):
        sudo('git pull')
        with cd('tomo'):
            sudo('git pull')
    manage('collectstatic --noinput')
    manage('syncdb')
    manage('migrate')
    unlock()

@task
def update_all():
    lock()
    with cd(env.home):
        with prefix('source virtualenv/bin/activate'):
            sudo('pip install -r requirements/{project_name}.txt'.format(**env))
        with cd('static/MathJax'):
            sudo('git pull')
    unlock()

@task
def get_dump():
    for fixture in FIXTURES:
        with hide('stdout'):
            json = manage('dumpdata --indent=2 {0}'.format(fixture))
        with open('fixtures/{0}.json'.format(fixture), 'w') as f:
            f.write(json)

@task
def edit_apache():
    edit('/etc/apache2/sites-available/tomo.fmf.uni-lj.si', use_sudo=True)

@task
def restart_apache():
    sudo('apache2ctl graceful')

@task
def reset_tomodev():
    if confirm('Are you sure you want to reset the staging database?',
               default=False):
        postgres("dropdb tomodev")
        postgres("createdb -T tomo tomodev")

@task
def reset_local():
    local('touch tomo.db')
    local('rm tomo.db')
    local('./manage.py syncdb --noinput')
    local('./manage.py migrate')
    local('./manage.py loaddata fixtures/*.json')

# Auxiliary commands

def set_project(project_name):
    env.project_name = project_name
    env.home = os.path.join(env.srv_directory, project_name)

def manage(command):
    with cd(env.home):
        with prefix('source virtualenv/bin/activate'):
            return sudo('./manage.py {0}'.format(command))

def postgres(command):
    sudo('su -c "{0}" postgres'.format(command))

def restart():
    with cd(env.home):
        sudo('touch project/wsgi.py')

def edit(remote_file, use_sudo=False):
    _, temporary_filename = tempfile.mkstemp(suffix=os.path.splitext(remote_file)[1])
    print temporary_filename
    get(remote_file, temporary_filename)
    local('$EDITOR {0}'.format(temporary_filename))
    put(temporary_filename, remote_file, use_sudo=use_sudo)
    local('rm {0}'.format(temporary_filename))

set_project('tomodev')
