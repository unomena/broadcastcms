from setuptools import setup, find_packages

setup(
    name='broadcastcms',
    #version='dev',
    version='1.1.1_trufm',
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
    ],
    include_package_data=True,    
)
