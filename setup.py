from setuptools import setup, find_packages

setup(
    name='broadcastcms',
    version='1.0.9.unomena.4',
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
        'django-voting==0.1',
        'psycopg2==2.2.2',
        'pexpect==2.4',
        'python-memcached==1.44',
        'PIL==1.1.6',
        'simplejson==2.0.9',
        'windmill==1.3',
        'whoosh==0.3.5',
        'django-haystack'
    ],
    include_package_data=True,
)
