import codecs
from setuptools import setup, find_packages

entry_points = {
}


TESTS_REQUIRE = [
    'nti.testing',
    'pyhamcrest',
    'zope.testing',
]


def _read(fname):
    with codecs.open(fname, encoding='utf-8') as f:
        return f.read()


setup(
    name='nti.futures',
    version=_read('version.txt').strip(),
    author='Jason Madden',
    author_email='jason@nextthought.com',
    description="NTI Futures Utils",
    long_description=(_read('README.rst') + '\n\n' + _read("CHANGES.rst")),
    license='Proprietary',
    keywords='Futures',
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
    zip_safe=True,
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['nti'],
    tests_require=TESTS_REQUIRE,
    install_requires=[
        'setuptools',
        'zope.exceptions'
    ],
    extras_require={
        'test': TESTS_REQUIRE,
        ':python_version == "2.7"': [
            'futures',
        ],
    },
    dependency_links=[],
    entry_points=entry_points,
    test_suite="nti.futures.tests",
)
