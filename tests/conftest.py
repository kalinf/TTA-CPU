import pytest
from pathlib import Path
from core.generate_core import gen_core

CONFTEST_DIR = Path(__file__).resolve().parent
DEFAULT_CORE_PATH = (CONFTEST_DIR / ".." / "examples" / "basic_core").resolve()


def pytest_addoption(parser):
    parser.addoption(
        "--core-directory",
        action="store",
        default=str(DEFAULT_CORE_PATH),
        help="Path to directory containing functional units and core configuration files.",
    )
    parser.addoption("--waveform", action="store_true", default=False, help="Generate waveforms while running tests.")


@pytest.fixture(scope="session")
def dir_path(request):
    dir_path = Path(request.config.getoption("--core-directory")).resolve()
    if not dir_path.exists():
        raise FileNotFoundError(f"Invalid core directory path: {dir_path}")
    return dir_path


@pytest.fixture(scope="session")
def core(dir_path):
    dut = gen_core(dir_path)
    return dut


@pytest.fixture
def vcd_file(dir_path, request):

    if not request.config.getoption("--waveform"):
        return None

    vcd_dir = dir_path / "waveforms"
    vcd_dir.mkdir(exist_ok=True)

    name = request.node.name
    file_path = vcd_dir / f"{name}.vcd"

    return file_path
