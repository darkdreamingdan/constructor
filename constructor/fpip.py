# (c) 2016 Continuum Analytics, Inc. / http://continuum.io
# All Rights Reserved
#
# constructor is distributed under the terms of the BSD 3-clause license.
# Consult LICENSE.txt or http://opensource.org/licenses/BSD-3-Clause.
"""
fpip (fetch pip packages) module
"""

import glob
import os
import pip
import sys
from os.path import isdir, join, basename

requirements_name = 'requirements.txt'


def fetch(info, verbose=True):
    download_dir = info['_pip_download_dir']
    if not isdir(download_dir):
        os.makedirs(download_dir)
    else:
        # We clear out the download directory each time -
        # pip has it's own cache that we leverage instead
        if verbose:
            print("Clearing cache directory at ", download_dir)
        try:
            for fn in os.listdir(download_dir):
                os.remove(join(download_dir, fn))
        except Exception as e:
            print(e)
            sys.exit("Error clearing pip cache directory")

    specs = info['pip']

    if verbose:
        print("pip specs: %r" % specs)

    # Generate the requirements file
    requirements_path = join(download_dir, requirements_name)
    with open(requirements_path, "w") as requirements:
        requirements.write('\n'.join(specs))
        requirements.close()
    # execute pip from within python
    pip_cmd = ['wheel',
               '--disable-pip-version-check',
               '-w', download_dir,
               '-r', requirements_path]

    if verbose:
        print("Running pip module with arguments: ", pip_cmd)
    if pip.main(pip_cmd) != 0:
        sys.exit("pip returned an error")

    # For local pip packages and absolute URLs, we take the basename
    offline_specs = []
    for spec in specs:
        # Take the first argument in pip install command, and shape it so that 
        # you have a local path
        # e.g.    "pip download https://asdf.com/somepackage.tar.gz --no-cache"
        # goes to "pip install somepackage-cp36-none-any.whl --no-cache"
        # Note: This assumes the tarfile name is similar to the .whl
        spec_params = spec.split()
        spec_params[0] = spec_params[0].rpartition('/')[-1]
        if spec_params[0].endswith('.tar.gz'):
            parsed_spec = spec_params[0].replace('.tar.gz', '')
            glob_path = join(download_dir, "{}*.whl".format(parsed_spec))
            spec_params[0] = basename(glob.glob(glob_path)[0])

        offline_specs.append(' '.join(spec_params))

    # Modified version of requirements with filenames in place of URLs
    with open(requirements_path, "w") as requirements:
        requirements.write('\n'.join(offline_specs))
        requirements.close()


def main(info, verbose=True):
    if 'pip' in info:
        fetch(info, verbose)

