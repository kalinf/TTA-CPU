import pytest
from pathlib import Path
from core.generate_core import gen_core
from utils.utils import build_addresses_core_model
from tests.utils import mock_resources as _mock_resources

CONFTEST_DIR = Path(__file__).resolve().parent
DEFAULT_CORE_PATH = (CONFTEST_DIR / ".." / "examples" / "example_core").resolve()


def pytest_addoption(parser):
    parser.addoption(
        "--core-directory",
        action="store",
        default=str(DEFAULT_CORE_PATH),
        help="Path to directory containing functional units and core configuration files.",
    )
    parser.addoption("--waveform", action="store_true", default=False, help="Generate waveforms while running tests.")


def pytest_collection_modifyitems(config, items):
    core_dir = Path(config.getoption("--core-directory")).resolve()

    selected = []

    for item in items:
        path = Path(item.fspath).resolve()
        if core_dir in path.parents:
            selected.append(item)

    items[:] = selected


@pytest.fixture(scope="session")
def dir_path(request):
    dir_path = Path(request.config.getoption("--core-directory")).resolve()
    if not dir_path.exists():
        raise FileNotFoundError(f"Invalid core directory path: {dir_path}")
    return dir_path


@pytest.fixture(scope="session")
def mock_resources(dir_path):
    return _mock_resources(dir_path / "config_detail.json")


@pytest.fixture(scope="session")
def core(dir_path, mock_resources):
    dut = gen_core(dir_path, resources=mock_resources)
    return dut


@pytest.fixture(scope="session")
def core_address_model(dir_path):
    model = build_addresses_core_model(dir_path / "config_detail.json")
    return model


@pytest.fixture
def vcd_file(dir_path, request):

    if not request.config.getoption("--waveform"):
        return None

    vcd_dir = dir_path / "waveforms"
    vcd_dir.mkdir(exist_ok=True)

    name = request.node.name
    file_path = vcd_dir / f"{name}.vcd"

    return file_path
