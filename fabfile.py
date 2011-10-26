from fabric.api import *
from fabric.contrib.console import confirm

env.hosts = ['matija@tyrion.fmf.uni-lj.si']
production = '/srv/tomo/'
staging = '/srv/dev/tomo/'

fixtures = [
    # 'auth.User',
    'course.Course',
    'course.ProblemSet',
    'problem.Language',
    'problem.Problem',
    'problem.Part',
    # 'problem.Submission',
    # 'problem.Attempt',
]

def stage():
    local('hg archive tomo.tgz')
    put('tomo.tgz', '/srv/dev/', use_sudo=True)
    local('rm tomo.tgz')
    with cd('/srv/dev/'):
        sudo('mv tomo/virtualenv _virtualenv')
        sudo('rm -r tomo')
        sudo('tar -xzf tomo.tgz')
        sudo('mv _virtualenv tomo/virtualenv')
        sudo('rm tomo.tgz')
    # migrate_database(staging)
    restart(staging)

def deploy():
    intermediate = '/srv/dev/_tomo/'
    sudo('cp -r {0} {1}'.format(staging, intermediate))
    sudo('rm -r {0}'.format(production))
    sudo('mv {0} {1}'.format(intermediate, production))
    # migrate_database(production)
    restart(production)

def manage(destination, command, options=""):
    settings = 'settings.production' if destination == production else 'settings.dev'
    with cd(destination):
        with prefix('source virtualenv/bin/activate'):
            sudo('./manage.py {1} --settings={0} {2}'.format(settings, command, options))

def dump(destination, application):
    manage(destination, 'dumpdata', '--indent=2 {0}'.format(application))

def migrate_database(destination):
    manage(destination, 'syncdb')
    manage(destination, 'loaddata fixtures/auth.json')
    # manage(destination, 'migrate')

def reset_staging_database():
    confirm('Are you sure you want to reset the staging database?', default=False)
    sudo('''su -c "psql --dbname=tomo --command='DROP DATABASE tomodev;'" postgres''')
    sudo('''su -c "psql --dbname=tomo --command='CREATE DATABASE tomodev WITH TEMPLATE tomo;'" postgres''')

def restart(destination):
    sudo('apache2ctl graceful')


def get_dump():
    with cd('/srv/tomo/'):
        with prefix('source virtualenv/bin/activate'):
            for fixture in fixtures:
                with hide('stdout'):
                    json = run('./manage.py dumpdata --settings=settings.production '
                         '--indent=2 {0}'.format(fixture))
                with open('fixtures/{0}.json'.format(fixture), 'w') as f:
                    f.write(json)

def save_dump():
    dumps = ['problem.Language', 'problem.Problem', 'problem.Part', 'course.Course', 'course.ProblemSet']
    for dump in dumps:
        local('./manage.py dumpdata --indent=2 {0} > fixtures/{0}.json'.format(dump))

def reset_local():
    local('touch tomo.db')
    local('rm tomo.db')
    local('./manage.py syncdb --noinput')
    # local('./manage.py migrate')
    local('./manage.py loaddata fixtures/*.json')
