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
    update(staging)

def update(destination):
    lock(destination)
    with cd(destination):
        sudo('hg fetch')
    migrate_database(destination)
    unlock(destination)

def deploy():
    update(production)

def manage(destination, command, options=""):
    settings = 'settings.production' if destination == production else 'settings.dev'
    with cd(destination):
        with prefix('source virtualenv/bin/activate'):
            sudo('./manage.py {1} --settings={0} {2}'.format(settings, command, options))

def dump(destination, application):
    manage(destination, 'dumpdata', '--indent=2 {0}'.format(application))

def migrate_database(destination):
    # manage(destination, 'syncdb')
    # manage(destination, 'loaddata fixtures/auth.json')
    # manage(destination, 'migrate')
    pass

def reset_staging_database():
    confirm('Are you sure you want to reset the staging database?', default=False)
    sudo('''su -c "psql --dbname=tomo --command='DROP DATABASE tomodev;'" postgres''')
    sudo('''su -c "psql --dbname=tomo --command='CREATE DATABASE tomodev WITH TEMPLATE tomo;'" postgres''')

def restart(destination):
    wsgi = 'tomo' if destination == production else 'tomo-dev'
    sudo('touch {0}apache/{1}.wsgi'.format(destination, wsgi))

def lock(destination):
    lock = 'tomo' if destination == production else 'tomo-dev'
    sudo('touch {0}apache/{1}.lock'.format(destination, lock))
    restart(destination)

def edit_settings(destination):
    server_settings = '{0}settings.py'.format(destination)
    filename = 'settings-temp.py'
    get(server_settings, filename)
    local('$EDITOR {0}'.format(filename))
    put(filename, server_settings, use_sudo=True)

def unlock(destination):
    lock = 'tomo' if destination == production else 'tomo-dev'
    sudo('rm {0}apache/{1}.lock'.format(destination, lock))
    restart(destination)


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

def reset_apache():
    put('apache/tomo.fmf.uni-lj.si', '/etc/apache2/sites-available/', use_sudo=True)
    sudo('apache2ctl graceful')

def reset_local():
    local('touch tomo.db')
    local('rm tomo.db')
    local('./manage.py syncdb --noinput')
    # local('./manage.py migrate')
    local('./manage.py loaddata fixtures/*.json')
