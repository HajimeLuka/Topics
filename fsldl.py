#!/usr/bin/env python
#
# fsldl.py - Script to download FSL course data
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#


import os
import os.path as op
import sys
import math
import zlib
import shutil
import hashlib
import argparse
import tempfile
import textwrap
import contextlib
import                   urllib
import urllib.parse   as urlparse
import urllib.request as urlrequest

import progressbar


class DownloadFailed(Exception):
    pass

class ExtractFailed(Exception):
    pass


MANIFEST_URL = 'http://fsl.fmrib.ox.ac.uk/fslcourse/downloads/manifest.txt'

MSGINFO     = '\033[37m'
MSGINFOEMPH = '\033[37;1m'
MSGEMPH     = '\033[92m\033[1m'
MSGWARN     = '\033[93m'
MSGERROR    = '\033[91m'
MSGQUESTION = '\033[36;1m'
MSGRESET    = '\033[0m'


def colourprint(colour, msg, *a, **kwa):
    print(f'{colour}{msg}{MSGRESET}', *a, **kwa)

def info(    msg, *a, **kwa): colourprint(MSGINFO,     msg, *a, **kwa)
def infoemph(msg, *a, **kwa): colourprint(MSGINFOEMPH, msg, *a, **kwa)
def warn(    msg, *a, **kwa): colourprint(MSGWARN,     msg, *a, **kwa)
def error(   msg, *a, **kwa): colourprint(MSGERROR,    msg, *a, **kwa)
def question(msg, *a, **kwa): colourprint(MSGQUESTION, msg, *a, **kwa)
def emph(    msg, *a, **kwa): colourprint(MSGEMPH,     msg, *a, **kwa)

def readInput(prompt):
    question(prompt, end='')
    return input()


class MockProgressBar:
    def __init__(self, *args, **kwargs):
        pass
    def update(self, *args, **kwargs):
        pass
    def __enter__(self, *args, **kwargs):
        return self
    def __exit__(self, *args, **kwargs):
        pass


def downloadFile(url, destination, progress=True):

    # Download/write out 1MB blocks at a time, so
    # we can display a progress bar, and resume
    # failed downloads.
    blockSize = 1048576

    # all files are saved to a temporary location
    # alongside the final destination. If a download
    # fails or is interrupted, the user can re-run
    # the program. We then check to see if this
    # temporary file exists, check its size if it
    # does, and attempt to resume the download from
    # that point.
    destdir  = op.dirname(destination)
    destname = op.basename(destination)
    tempdest = op.join(destdir, f'.{destname}.part')

    # start downloading from this offest
    if op.exists(tempdest):
        offset     = op.getsize(tempdest)
        writeflags = 'ab'
        request    = urlrequest.Request(
            url, headers={'Range' : f'bytes={offset}-'})

    # or download the entire file
    else:
        writeflags = 'wb'
        request    = url

    with urlrequest.urlopen(request) as inf, \
         open(tempdest, writeflags) as outf:

        # try and get the download size, so we
        # can display an accurate progress bar
        try:
            nbytes = int(inf.headers['content-length'])
            nmb    = math.ceil(nbytes / 1048576)
        except Exception:
            nmb = progressbar.UnknownLength

        if progress: progress = progressbar.ProgressBar
        else:        progress = MockProgressBar

        mbcount = 0
        with progress(max_value=nmb) as bar:
            bar.update(0)
            while True:
                block = inf.read(blockSize)
                if len(block) == 0:
                    break
                mbcount += len(block) / 1048576
                bar.update(int(mbcount))
                outf.write(block)
    shutil.move(tempdest, destination)


def calcChecksum(path):

    # 128MB blocks
    blockSize = 134217728
    hashobj   = hashlib.sha256()
    with open(path, 'rb') as f:
        block = f.read(blockSize)
        while block != b'':
            hashobj.update(block)
            block = f.read(blockSize)
    return hashobj.hexdigest()


def downloadManifest(url):
    info(f'Downloading manifest file from {url}...')

    with tempfile.TemporaryDirectory() as d:
        dest = op.join(d, 'manifest.txt')
        downloadFile(url, dest, progress=False)
        manifest = open(dest, 'rt').read()

    datasets = {}

    for line in manifest.split('\n'):

        line = line.strip()

        if line == '' or line.startswith('#'):
            continue

        tkns                   = [t.strip() for t in line.split(',', 3)]
        key, shasum, url, desc = tkns

        # support paths to local files
        if op.exists(url):
            url = urlparse.urljoin(
                'file:', urllib.pathname2url(op.abspath(url)))

        datasets[key]  = (desc, shasum, url)

    return datasets


def selectDataSets(manifest):

    dskeys = list(manifest.keys())

    emph('Datasets available for download:')
    for i, key in enumerate(dskeys, 1):
        desc = manifest[key][0]
        key  = f'[{key}]'
        infoemph(f'  {i:2d} {key:25s}')
        info(textwrap.indent(textwrap.fill(desc), '     '))

    while True:
        emph('Which data sets would you like to download?')
        info(textwrap.indent(textwrap.fill(
            'Type "all" to download all of the data sets. Alternately, '
            'enter the numbers of each data set you would like to '
            'download, separated by spaces. For example, if you would '
            f'like to download the [{dskeys[0]}] and [{dskeys[1]}] data '
            'sets, enter "1 2". Type "q" or "quit" to cancel the '
            'download.'), '  '))

        datasets = readInput('Enter data sets to download: ')
        datasets = datasets.strip()

        if datasets.lower() in ('q', 'quit'):
            raise SystemExit()

        if datasets.lower() == 'all':
            datasets = dskeys
            break

        try:
            datasets = [int(t) for t in datasets.split()]
        except Exception:
            error(f'Specified data set(s) {datasets} not understood')
            continue
        if len(datasets) == 0:
            warn(f'No data sets specified! Type "all" to download all data sets.')
            continue
        if any([d <= 0 or d > len(manifest) for d in datasets]):
            error(f'One of the data set(s) {datasets} does not exist')
            continue
        datasets = [dskeys[ds - 1] for ds in datasets]
        break

    return [(ds, manifest[ds][1], manifest[ds][2]) for ds in datasets]


def createDestination(destination):

    emph(textwrap.fill('Would you like the FSL course practical data '
                       'to be saved to your home directory?'))
    info(textwrap.indent(textwrap.fill(
        'If you press enter without typing anything, the data '
        'will be saved to your home directory. Otherwise, feel '
        'free to enter the directory to which you would like the '
        'data to be downloaded. Type "q" or "quit" to cancel the '
        'download.'), '  '))
    result = readInput('Download directory '
                       '[press Enter to save to home directory]: ')

    if result.lower() in ('q', 'quit'):
        raise SystemExit()

    if result.lower() not in ('', 'y', 'yes'):
        destination = result

    destination = op.abspath(destination)

    info(f'Downloading data to {destination}')

    archiveDir = op.join(destination, '.fsl_course_data_archives')
    os.makedirs(archiveDir, exist_ok=True)
    return destination, archiveDir


def downloadDataSet(name, checksum, url, archiveDir):

    fname        = op.basename(urlparse.urlparse(url).path)
    archiveFile  = op.join(archiveDir, fname)
    skipDownload = False

    infoemph(f'{name}...')

    if op.exists(archiveFile):
        info(f'  {fname} already exists - calculating SHA256 checksum...')
        destchecksum = calcChecksum(archiveFile)
        if destchecksum == checksum:
            info('  Checksums match - skipping download')
            skipDownload = True
        else:
            info('  Checksums do not match - re-downloading file')
            info(f'    manifest checksum:      {checksum}')
            info(f'    existing file checksum: {destchecksum}')

    if not skipDownload:
        info(f'  Downloading {url}')
        info(f'  saving to {archiveFile}')
        try:
            downloadFile(url, archiveFile)
        except urllib.error.HTTPError as e:
            raise DownloadFailed(f'A network error has occurred while trying '
                                 f'to download the [{name}] data set: {e}')

    return archiveFile, skipDownload


def extractDataSet(archiveFile, destination, deleteIfFailed=False):
    fname = op.basename(archiveFile)
    info(f'  Extracting {fname} to {destination}...')
    try:
        shutil.unpack_archive(archiveFile, destination)

    # If we get a decompress error, the archive may
    # be corrupt. We delete the file, and propagate
    # the error - the main function will tell the
    # user what to do.
    except (zlib.error, EOFError) as e:
        if deleteIfFailed:
            os.remove(archiveFile)
        raise ExtractFailed(str(e))

def parseArgs():

    parser = argparse.ArgumentParser(
        'fsldl', 'Download FSL course practical datasets')
    parser.add_argument('-m', '--manifest',
                        default=MANIFEST_URL,
                        help='URL to dataset manifest file')
    parser.add_argument('-sc', '--skip_checksum',
                        action='store_true',
                        help='Skip checksum check')
    parser.add_argument('-e', '--extract_if_exist',
                        action='store_true',
                        help='Extract archive files even if they '
                        'already exist')
    parser.add_argument('-d', '--destination',
                        default=op.expanduser('~'),
                        help='URL to dataset manifest file')

    args = parser.parse_args()

    if op.exists(args.manifest):
        args.manifest = urlparse.urljoin(
            'file:', urlrequest.pathname2url(op.abspath(args.manifest)))

    return args


def main():
    try:
        args                    = parseArgs()
        destination, archiveDir = createDestination(args.destination)
        manifest                = downloadManifest(args.manifest)
        datasets                = selectDataSets(manifest)

        info(textwrap.indent(textwrap.fill(
            'If you would like to stop the download, you '
            'can press "CTRL+C" to exit. You can re-run this '
            'script at a later point in time to resume the '
            'download.'), '  '))

        for name, shasum, url in datasets:

            try:
                archiveFile, skipped = downloadDataSet(
                    name, shasum, url, archiveDir)
            except DownloadFailed as e:
                error(str(e))
                continue

            checksumPass = args.skip_checksum
            if not (args.skip_checksum or skipped):
                info(f'  Downloaded archive file for {name} - calculating '
                     'SHA256 checksum to verify download...')
                checksum     = calcChecksum(archiveFile)
                checksumPass = checksum == shasum
                if checksumPass:
                    info(f'  Checksums match - download succeeded')
                else:
                    error(f'Downloaded archive file for {name} data set '
                          'does not match checksum in manifest! This '
                          'probably means that the download failed. I\'ll '
                          'try to continue, but the file may be corrupt, '
                          'so the next step might fail.')
                    info(f'  manifest checksum:        {shasum}')
                    info(f'  downloaded file checksum: {checksum}')

            if not (skipped and (not args.extract_if_exist)):
                try:
                    extractDataSet(archiveFile, destination, not checksumPass)
                except ExtractFailed as e:
                    error(f'Could not extract archive file for {name}: {e}')
                    if not checksumPass:
                        error(f'The {name} dataset  may not have been '
                              'downloaded correctly - try re-running '
                              'this script to re-download it.')
                    continue

    except Exception as e:
        error(f'An error has occurred! {e}')
        raise e


if __name__ == '__main__':
    main()
