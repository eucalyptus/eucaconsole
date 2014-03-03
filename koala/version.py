
import os.path
import subprocess


__version__ = 'devel'


if '__file__' in globals():
    # Check if this is a git repo; maybe we can get more precise version info
    try:
        repo_path = os.path.join(os.path.dirname(__file__), '..')
        git = subprocess.Popen(['git', 'describe'], stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               env={'GIT_DIR': os.path.join(repo_path, '.git')})
        git.wait()
        git.stderr.read()
        if git.returncode == 0:
            __version__ = git.stdout.read().strip()
            if type(__version__).__name__ == 'bytes':
                __version__ = __version__.decode()
    except:
        # Not really a bad thing; we'll just use what we had
        pass
