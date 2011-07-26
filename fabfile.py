from fabric.api import *
from fabric.contrib.console import confirm

env.hosts = ['matija@tyrion.fmf.uni-lj.si']
production = '/srv/tomo/'
staging = '/srv/dev/tomo/'

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
    migrate_database(staging)
    restart_apache()

def deploy():
    intermediate = '/srv/dev/_tomo/'
    sudo('cp -r {0} {1}'.format(staging, intermediate))
    sudo('rm -r {0}'.format(production))
    sudo('mv {0} {1}'.format(intermediate, production))
    migrate_database(production)
    restart_apache()

def manage(destination, command):
    settings = 'settings-tyrion' if destination == production else 'settings-dev'
    sudo('./manage.py {1} --settings={0}'.format(settings, command))

def migrate_database(destination):
    with cd(destination):
        with prefix('source virtualenv/bin/activate'):
            manage(destination, 'syncdb')
            manage(destination, 'migrate')

def reset_staging_database():
    confirm('Are you sure you want to reset the staging database?', default=False)
    sudo('''su -c "psql --dbname=tomo --command='DROP DATABASE tomodev;'" postgres''')
    sudo('''su -c "psql --dbname=tomo --command='CREATE DATABASE tomodev WITH TEMPLATE tomo;'" postgres''')

def restart_apache():
    sudo('apache2ctl graceful')

def get_dump():
    dumps = ['problem.Problem', 'problem.Part']
    with cd('/srv/tomo/'):
        with prefix('source virtualenv/bin/activate'):
            for dump in dumps:
                sudo('./manage.py dumpdata --settings=settings-tyrion '
                     '--indent=2 {0} > {0}.json'.format(dump))
        get('*.json', 'fixtures/')
        sudo('rm *.json')

def reset_local():
    local('touch tomo.db')
    local('rm tomo.db')
    local('./manage.py syncdb --noinput')
    local('./manage.py migrate')
    local('./manage.py loaddata fixtures/*.json')
