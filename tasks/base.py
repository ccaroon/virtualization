"""
Zeta Virtual Machine Manager (zvm)

Top-level ZVM Commands
"""
from invoke import task


@task
def init(ctx, spec):
    """
    Initialize a VM

    spec (str): Path to a ZVM specification file
    """

    # TODO: read VMfile

    # TODO: build image

    # TODO: create `tasks.py`
    #     - start, up, run
    #     - stop, halt
    #     - ssh

    # TODO: ????
