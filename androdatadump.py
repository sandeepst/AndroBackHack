import os
import sys
from subprocess import Popen, PIPE, STDOUT
from sys import argv
import zlib
import shutil
import contextlib
import tarfile

cmds = {'backup': 'adb backup -f {} {}', # back up file name, package name being backed up
        'dd': 'dd skip=24 bs=1 if={} of={}', # back up file name, raw output file name
        'pname': 'adb shell pm list packages'
        }

raw_data = 'data'


def run_cmd(cmd, *args):
    print('command being executed "{}"'.format(str(cmd).format(*args)))
    try:
        res = Popen(str(cmd).format(*args), stdout=PIPE, stderr=STDOUT, shell=True)
    except Exception as ex:
        print(ex)
        exit(1)
    out = res.communicate()[0]
    if res.returncode != 0:
        print(f"Failed {res.returncode} : {out.decode('utf-8')}")
        exit(1)
    return


def extract_backup(pkg):
    pkg_rep = pkg.replace('.', '_')
    pkg_ab = pkg_rep + '.ab'
    tar = pkg_rep + '.tar'
    extract_path = os.path.join(os.curdir, 'files')
    try:
        run_cmd(cmds['backup'], pkg_ab, pkg)
        if (sz := os.path.getsize(pkg_ab)) < 1024:
            raise Exception(f'Failed to read backup : {sz} bytes!')
        run_cmd(cmds['dd'], pkg_ab, raw_data)
        print(f'Creating a tar file and ultimately Files being extracted to {os.path.abspath(extract_path)}')
        with open(raw_data, 'rb') as fr, open(tar, 'wb') as ft:
            tar_content = fr.read()
            ft.write(zlib.decompress(tar_content))
        with tarfile.open(tar, "r") as tf:
            tf.extractall(path=extract_path)
    except Exception as ex:
        print('Failed : ', ex)
    finally:
        with contextlib.suppress(FileNotFoundError):
            os.remove(pkg_ab)
            os.remove(raw_data)
    return


if __name__ == '__main__':
    pkg = sys.argv[1]
    print(f'The package {pkg} being processed for backup extraction')
    tmpdir = os.path.join(os.curdir, 'tmp', pkg.replace('.','_'))
    shutil.rmtree(tmpdir, ignore_errors=True)
    os.makedirs(tmpdir, exist_ok=True)
    os.chdir(tmpdir)
    extract_backup(pkg)



