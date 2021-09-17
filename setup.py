from setuptools import setup

setup(
    name='ff_bot',

    packages=['ff_bot'],

    include_package_data=True,

    version='0.3.0',

    description='Fantasy football Chat Bot',

    author='Chris Bevard',

    author_email='cbevard1@gmail.com',

    install_requires=['tzlocal~=2.0', 'requests>=2.0.0,<3.0.0', 'apscheduler>3.0.0', 'beautifulsoup4~=4.9.3', 'aiohttp<3.8.0,>=3.6.0', 'cchardet', 'lxml', 'discord', 'aiocron', 'nest-asyncio'],

    #test_suite='nose.collector',

    #tests_require=['nose', 'requests_mock'],

    url='https://github.com/cbevard1/fantasy_football_chat_bot',

    classifiers=[
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
