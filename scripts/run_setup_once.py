import sys
from pathlib import Path

# Ensure project root on sys.path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from financial_launcher import LauncherLogger, DependencyManager


def main():
    log = LauncherLogger()
    dm = DependencyManager(log)
    print("VENV:", dm.venv_path)
    ok = dm.check_python_version()
    print("check_python_version:", ok)
    ok = dm.create_virtual_environment()
    print("create_virtual_environment:", ok)
    ok = dm.install_dependencies()
    print("install_dependencies:", ok)


if __name__ == "__main__":
    sys.exit(main() or 0)
