import codecs
from setuptools import setup, find_packages

VERSION = '0.0.0'

entry_points = {
	'console_scripts': [
	],
}

TESTS_REQUIRE = [
	'nose',
	'nose2[coverage_plugin]',
	'nose-timer',
	'nose-progressive',
	'nose-pudb',
	'pyhamcrest',
	'nti.nose_traceback_info',
	'nti.testing'
]

setup(
	name='nti.futures',
	version=VERSION,
	author='Jason Madden',
	author_email='jason@nextthought.com',
	description="NTI Futures Utils",
	long_description=codecs.open('README.rst', encoding='utf-8').read(),
	license='Proprietary',
	keywords='Futures',
	classifiers=[
		'Intended Audience :: Developers',
		'Natural Language :: English',
		'Operating System :: OS Independent',
		'Programming Language :: Python :: 2',
		'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
		'Programming Language :: Python :: Implementation :: CPython',
	],
	packages=find_packages('src'),
	package_dir={'': 'src'},
	namespace_packages=['nti'],
	tests_require=TESTS_REQUIRE,
	install_requires=[
		'setuptools',
		'futures'
	],
	extras_require={
		'test': TESTS_REQUIRE,
	},
	dependency_links=[
		'git+https://github.com/NextThought/nti.nose_traceback_info.git#egg=nti.nose_traceback_info'
	],
	entry_points=entry_points
)
