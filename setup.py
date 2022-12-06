from pathlib import Path

from setuptools import setup


def __get_install_requires(rtype):
    requirements = Path(f'{rtype}-requirements.txt').read_text()
    return requirements.split()

setup(
    name='xtremcache',
    version='2.0.0',
    author='xtrembuffalo',
    author_email='tristan.cladet@gmail.com',
    description='Handle generic file and directories caching',
    long_description=Path('README.md').read_text(),
    long_description_content_type='text/markdown',
    license='GPL-3.0',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: Plugins',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: Unix',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development',
        'Topic :: System :: Archiving',
        'Typing :: Typed',
    ],
    keywords='cache caching store storage file files folder folders archive archives rep repertory repertories',
    project_urls={
        'Documentation': 'https://github.com/xtrembuffalo/xtremcache/blob/main/README.md',
        'Source': 'https://github.com/xtrembuffalo/xtremcache',
        'Tracker': 'https://github.com/xtrembuffalo/xtremcache/issues',
    },
    install_requires=__get_install_requires('dist'),
    entry_points={
        'console_scripts': ['xtremcache=xtremcache.__main__:main']
    },
    python_requires='>=3.8',
    tests_require=__get_install_requires('test'),
    test_suite='tests')
