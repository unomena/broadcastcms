from setuptools import setup, find_packages

setup(
    name='broadcastcms',
    #version='dev',
    version='goodhopefm.1.1.1',
    description='Broadcast CMS Django Applications',
    author='Praekelt Consulting',
    author_email='sysadmin@praekeltconsulting.com',
    url='http://www.broadcastcms.com',
    packages = find_packages(),
    dependency_links = [
        'http://dist.repoze.org/',
    ],
    install_requires = [
        'django-debug-toolbar==0.8.0',
        'Django_FacebookConnect==0.2',
        'django-friends==0.2alpha',
        'django-haystack',
        'django-voting==0.1-pre',
        'mysql-python==1.2.3c1',
        'pexpect==2.4',
        'pyfacebook==0.1',
        'python-dateutil==1.4.1',
        'python-memcached==1.44',
        'python-twitter==0.6',
        'PIL>=1.1.6',
        'simplejson==2.0.9',
        'user-messages==0.1-dev1',
        'whoosh==0.3.5',
        'windmill==1.3',
    ],
    include_package_data=True,
)
