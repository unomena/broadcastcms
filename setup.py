from setuptools import setup, find_packages

setup(
    name='broadcastcms',
    version='dev',
    #version='1.0.9',
    description='Broadcast CMS Django Applications',
    author='Praekelt Consulting',
    author_email='sysadmin@praekeltconsulting.com',
    url='http://projects.praekelt.com/broadcastcms',
    packages = find_packages(),
    dependency_links = [
        'http://dist.repoze.org/',
    ],
    install_requires = [
        'django-debug-toolbar==0.8.0',
        'django-voting==0.1-pre',
        'MySQL-python==1.2.2',
        'pexpect==2.4',
        'python-memcached==1.44',
        'PIL==1.1.6',
        'simplejson==2.0.9',
        'windmill==1.3',
        'whoosh==0.3.4',
        'django-haystack==1.0.0'
    ],
    include_package_data=True,
)
