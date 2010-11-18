from setuptools import setup, find_packages

setup(
    name='broadcastcms',
    description='Broadcast CMS Django App',
    version='sabc3.1.0.6',
    author=' Praekelt Consulting',
    license='Propriatory',
    packages = find_packages(),
    include_package_data=True,
    zip_safe=False,
)
