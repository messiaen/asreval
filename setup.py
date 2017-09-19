from setuptools import setup

setup(
    name='asreval',
    description='Tool for evaluation asr and kws systems',
    version='0.1.0',
    packages=['asreval'],
    author='BBN',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing :: Linguistic',
        'Topic :: Utilities',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Scientific/Engineering :: Information Analysis'
    ],
    tests_require=['pytest'],
    setup_requires=['pytest-runner'],
    install_requires=[],
    entry_points={
        'console_scripts': [
            'compute_map = asreval.compute_map:main',
        ]
    }
)

