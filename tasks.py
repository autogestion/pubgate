import os
import sys
from distutils.util import strtobool

from invoke import task

HERE = os.path.dirname(os.path.abspath(__file__))
SHELL = os.environ.get('SHELL', '/bin/bash')

@task
def requirements(ctx):
    """
    Install requirements
    """
    bin_path = os.path.dirname(sys.executable)
    for req in ['requirements/base.txt', 'requirements/extensions.txt']:
        requirements_file = os.path.join(HERE, req)
        cmd = os.path.join(
            bin_path,
            f'pip install --no-cache-dir --exists-action w '
            f'--upgrade -r {requirements_file}'
        )
        ctx.run(cmd, pty=True, shell=SHELL)


@task
def server(ctx):
    cmd = f'python run_api.py'
    ctx.run(cmd, pty=True, shell=SHELL)


@task
def clean(ctx, verbose=False):
    """
    Clean *.pyc.
    """
    cmd = 'find . -name "*.pyc" -delete'
    if verbose:
        print(cmd)
    ctx.run(cmd, pty=True, shell=SHELL)
