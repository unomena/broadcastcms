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
        'PIL==1.1.6',
        'django-voting==0.1-pre',
        'mysql-python==1.2.3c1',
        'pexpect==2.4',
        'simplejson==2.0.9',
        'django-debug-toolbar==0.8.0',
    ],
    include_package_data=True,    
)
