from setuptools import setup

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

with open('README.md', encoding='utf-8') as readme:
    long_description = readme.read()

setup(
    name='prometheus_ncs2_exporter',
    version='0.0.1',
    packages=['prometheus_ncs2_exporter'],
    url='https://github.com/adaptant-labs/prometheus_ncs2_exporter',
    license='Apache 2.0',
    author='Adaptant Labs',
    author_email='labs@adaptant.io',
    description='Prometheus Exporter for Intel NCS2 Metrics',
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords=['prometheus', 'movidius', 'ncs2', 'myriadx', 'monitoring', 'exporter'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Topic :: System :: Monitoring',
        'License :: OSI Approved :: Apache Software License',
    ],
    install_requires=requirements,
    entry_points={
      'console_scripts': [ 'prometheus_ncs2_exporter = prometheus_ncs2_exporter.main:main']
    },
)
