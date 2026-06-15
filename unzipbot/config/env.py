import sys
import tomllib
from importlib.metadata import PackageMetadata, metadata, version
from os import environ
from pathlib import Path

PACKAGE_ROOT: Path = Path(__file__).resolve().parents[1]
PROJECT_ROOT: Path = PACKAGE_ROOT.parent
pkg_name: str = PACKAGE_ROOT.name
pyproject = PROJECT_ROOT / "pyproject.toml"


def _package_metadata() -> PackageMetadata:
    try:
        return metadata("pyrofork")
    except Exception:
        return PackageMetadata()


def _package_version(package_name: str, fallback: str) -> str:
    try:
        return version(package_name)
    except Exception:
        return fallback


def _project_version() -> str:
    try:
        with pyproject.open("rb") as file:
            return tomllib.load(file)["project"]["version"]
    except Exception:
        return "7.4.0"


class Env:
    APP_ID: str | None = environ.get("APP_ID")
    API_HASH: str | None = environ.get("API_HASH")
    AUTO_MIGRATE_ATLAS_SCHEMA: str | None = environ.get("AUTO_MIGRATE_ATLAS_SCHEMA")
    BASE_LANGUAGE: str | None = environ.get("BASE_LANGUAGE")
    BOT_TOKEN: str | None = environ.get("BOT_TOKEN")
    BOT_OWNER: str | None = environ.get("BOT_OWNER")
    DYNO: str | None = environ.get("DYNO")
    FRAMEWORK_METADATA: PackageMetadata = _package_metadata()
    LOGS_CHANNEL: str | None = environ.get("LOGS_CHANNEL")
    MONGODB_DBNAME: str | None = environ.get("MONGODB_DBNAME")
    MONGODB_URL: str | None = environ.get("MONGODB_URL")
    PACKAGE_NAME: str = pkg_name
    ROOT_DIR = str(PROJECT_ROOT)

    class Versions:
        PYROFORK: str = _package_version("pyrofork", "2.3.69")
        PYTHON: str = ".".join(str(part) for part in sys.version_info[:3])
        UNZIPBOT: str = _project_version()
