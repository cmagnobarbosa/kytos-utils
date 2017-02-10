"""Setup script.

Run "python3 setup --help-commands" to list all available commands and their
descriptions.
"""
import os
import sys
from subprocess import CalledProcessError, call, check_call
from pip.req import parse_requirements
from setuptools import Command, find_packages, setup
from setuptools.command.develop import develop
from setuptools.command.test import test as TestCommand

if 'VIRTUAL_ENV' in os.environ:
    BASE_ENV = os.environ['VIRTUAL_ENV']
else:
    BASE_ENV = '/'

SKEL_PATH = 'etc/skel'
KYTOS_SKEL_PATH = os.path.join(SKEL_PATH,'kytos')
AUTHOR_PATH = os.path.join(KYTOS_SKEL_PATH,'napp-structure/author')
NAPP_PATH = os.path.join(AUTHOR_PATH, 'napp')
ETC_FILES = [(os.path.join(BASE_ENV, AUTHOR_PATH),
              [os.path.join(AUTHOR_PATH, '__init__.py')]),
             (os.path.join(BASE_ENV, NAPP_PATH),
              [os.path.join(NAPP_PATH, '__init__.py'),
               os.path.join(NAPP_PATH, 'kytos.json.template'),
               os.path.join(NAPP_PATH, 'main.py.template'),
               os.path.join(NAPP_PATH, 'README.rst.template'),
               os.path.join(NAPP_PATH, 'settings.py.template')])
             ]

class Linter(Command):
    """Code linters."""

    description = 'run Pylama on Python files'
    user_options = []

    def run(self):
        """Run linter."""
        self.lint()

    @staticmethod
    def lint():
        """Run pylama and radon."""
        files = 'tests setup.py kytos_utils'
        print('Pylama is running. It may take several seconds...')
        cmd = 'pylama {}'.format(files)
        try:
            check_call(cmd, shell=True)
        except CalledProcessError as e:
            print('FAILED: please, fix the error(s) above.')
            sys.exit(e.returncode)

    def initialize_options(self):
        """Set defa ult values for options."""
        pass

    def finalize_options(self):
        """Post-process options."""
        pass


class Test(TestCommand):
    """Run doctest and linter besides tests/*."""

    def run(self):
        """First, tests/*."""
        super().run()
        Linter.lint()

class DevelopMode(develop):
    """Recommended setup for kytos-utils developers.

    Instead of copying the files to the expected directories, a symlink is
    created on the system aiming the current source code.
    """

    def run(self):
        """Install the package in a developer mode."""
        super().run()
        self._create_data_files_directory()

    def _create_data_files_directory(self):
        current_directory = os.path.abspath(os.path.dirname(__file__))

        dst_dir = os.path.join(BASE_ENV, SKEL_PATH)
        os.mkdir(dst_dir)

        src = os.path.join(current_directory, KYTOS_SKEL_PATH)
        dst = os.path.join(BASE_ENV, KYTOS_SKEL_PATH)

        os.symlink(src, dst)

# parse_requirements() returns generator of pip.req.InstallRequirement objects
requirements = parse_requirements('requirements.txt', session=False)

setup(name='kytos-utils',
      version='0.1.0',
      description=' Command line utilities to use with Kytos.',
      url='http://github.com/kytos/kytos-utils',
      author='Kytos Team',
      author_email='of-ng-dev@ncc.unesp.br',
      license='MIT',
      test_suite='tests',
      scripts=['bin/kytos'],
      data_files=ETC_FILES,
      packages=find_packages(exclude=['tests']),
      cmdclass={
          'develop': DevelopMode,
          'lint': Linter,
          'test': Test
      },
      zip_safe=False)
