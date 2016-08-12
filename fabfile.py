from fabric.api import run, sudo, env, put
import subprocess


### LINUX PACKAGES TO INSTALL ###

INSTALL_PACKAGES = [
   'apache2',
   'libapache2-mod-wsgi',
   'openssl',
   'libxml2-dev',
   'libxslt1-dev',
   'libssl-dev',
   'libatlas-base-dev',
   'libblas-dev',
   'libffi-dev',
   'gfortran',
   'g++',
   'python2.7-dev',
   'python-pip',
   'build-essential',
   'python-scipy'
]


### ENVIRONMENTS ###
def vagrant():
    """Defines the Vagrant virtual machine's environment variables.
    
    Environments define and contain the information need to SSH into a server,
    e.g. IP address, SSH key, username, and possibly password.
    """
    # Use Python's subprocess to run 'vagrant ssh-config' and parse results
    raw_ssh_config = subprocess.Popen(['vagrant', 'ssh-config'],
                                      stdout=subprocess.PIPE).communicate()[0]
    ssh_config = dict([l.strip().split() for l in raw_ssh_config.split("\n")
                       if l])
    env.hosts = ['127.0.0.1:%s' % (ssh_config['Port'])]
    env.user = ssh_config['User']
    env.key_filename = ssh_config['IdentityFile'].replace('"', '')
    env.virtualenv = {'dir': '/server', 'name': 'venv'}


def aws():
    """Defines the AWS server's environmnet variables."""
    env.hosts = 'ec2-54-187-201-203.us-west-2.compute.amazonaws.com'
    env.user = 'ubuntu'
    env.key_filename = '/Users/jenniferchen/Downloads/hs698v2.pem'
    env.virtualenv = {'dir': '/server', 'name': 'venv'}


def bootstrap():
    """Set up and configure Vagrant to be able to serve the web app.

    Runs commands on the command line to configure the Ubuntu server.
    """
    sub_install_packages()
    sub_install_virtualenv()
    sub_create_virtualenv()
    sub_install_python_requirements()


def bootstrap_aws():
    """Set up and configure AWS(EC2) to be able to serve the web app.

    Runs commands on the command line to configure the Ubuntu server.
    Run the Flask development server on the EC2 server.
    """
    sub_install_packages()
    sub_install_virtualenv()
    sub_create_virtualenv()
    sub_install_python_requirements_aws()


def sub_install_packages():
    """Install Ubuntu packages using apt-get, Ubuntu's package manager."""
    sudo('apt-get update')  # Update repository links
    sudo('apt-get -y upgrade')  # Upgrade the system
    package_str = ' '.join(INSTALL_PACKAGES)
    sudo('apt-get -y install ' + package_str)  # Install the packages


def sub_install_virtualenv():
    """Install the Python package 'virtualenv' so we can install Python
    packages safely into a virtualenv and not the system Python.
    """
    sudo('pip install virtualenv')  # Need sudo b/c installing to system Python


def sub_create_virtualenv():
    """Creates a Python virtualenv within which application requirements will
    be installed.
    """
    # Create folder to put virtualenv within
    mkdir = 'mkdir -p {0}; chown {1} {0}'.format(
       env.virtualenv['dir'], env.user)
    sudo(mkdir)
    # Create the virtualenv if it doesn't exist
    mkvenv = 'if [ ! -d {0}/{1} ]; then virtualenv {0}/{1}; fi'.format(    
       env.virtualenv['dir'], env.virtualenv['name'])
    run(mkvenv)


def sub_install_python_requirements():
    """Install the Flask apps' Python requirements into the virtualenv.

    We need to activate the virtualenv before installing into it. We do that
    with the command 'source /server/bin/activate'. The application requirements
    live in the requirements.txt file shared with the VM. This file lives at
    /vagrant/flask_ml/requirements.txt.
    """
    # Activate the virtualenv
    activate = 'source {0}/{1}/bin/activate'.format(
        env.virtualenv['dir'], env.virtualenv['name'])
    run(activate)

    # Install Python requirements
    install = 'pip install -r /vagrant/Flask_app/requirements.txt'

    # Join and execute the commands
    run(activate + '; ' + install)


def dev_server():
    """Run the Flask development server on the VM."""
    # Activate the virtualenv
    activate = 'source {0}/{1}/bin/activate'.format(
        env.virtualenv['dir'], env.virtualenv['name'])
    # Run the file app.py to start the Flask app
    dev_server = 'python vagrant/Flask_app/app.py'
    run(activate + '; ' + dev_server)


def sub_install_python_requirements_aws():
    """Install the Flask apps' Python requirements into the aws.

    We need to activate the virtualenv before installing into it. We do that
    with the command 'source /server/bin/activate'. We copy the Flask apps'
    directory using Fabric's copy mechanism to /home/ubuntu. The application
    requirements live in the requirements.txt file. This file lives at
    /HS698-project/Flask_app/requirements.txt.

    Run the Flask development server on the AWS(EC2) server. The Flask app can
    be reached at http://EC2_IP:5000/
    (EC2_IP = 54.187.201.203)
    """
    # Activate the virtualenv
    activate = 'source {0}/{1}/bin/activate'.format(
        env.virtualenv['dir'], env.virtualenv['name'])
    run(activate)

    # make sure the directory is there
    run('mkdir -p /home/ubuntu')

    # put the local directory '/Users/jenniferchen/github/HS698-project'
    # - it contains files or subdirectories
    # to the ubuntu server
    put('/Users/jenniferchen/github/HS698-project',
        '/home/ubuntu')

    # Install Python requirements
    install = 'pip install -r ' \
              '/home/ubuntu/HS698-project/Flask_app/requirements.txt'

    # Join and execute the commands
    sudo(install)
    # Run the file app.py to start the Flask app
    dev_server = 'python HS698-project/Flask_app/app.py'
    run(dev_server)