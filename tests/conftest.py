import json
import sys
import time
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

# #region agent log
_AGENT_LOG_PRIMARY = Path(__file__).resolve().parents[1] / ".cursor" / "debug-39292b.log"
_AGENT_LOG_FALLBACK = Path(__file__).resolve().parents[1] / "debug-39292b.log"


def _agent_dbg(message: str, hypothesis_id: str, **data: object) -> None:
    payload = {
        "sessionId": "39292b",
        "runId": data.pop("run_id", "pre-fix"),
        "hypothesisId": hypothesis_id,
        "location": "tests/conftest.py",
        "message": message,
        "data": data,
        "timestamp": int(time.time() * 1000),
    }
    line = json.dumps(payload) + "\n"
    for path in (_AGENT_LOG_PRIMARY, _AGENT_LOG_FALLBACK):
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("a", encoding="utf-8") as f:
                f.write(line)
            break
        except OSError:
            continue


# #endregion

_agent_dbg("conftest_imported", "H3", run_id="import-check")


def pytest_addoption(parser: pytest.Parser) -> None:
    # #region agent log
    _agent_dbg("pytest_addoption_enter", "H1", run_id="hook")
    # #endregion
    parser.addoption(
        "--gpu",
        action="store_true",
        default=False,
        help="Only run tests marked @pytest.mark.gpu.",
    )
    parser.addoption(
        "--slow",
        action="store_true",
        default=False,
        help="Only run tests marked @pytest.mark.slow.",
    )
    # #region agent log
    _agent_dbg("pytest_addoption_registered_cli_flags", "H1", flags=("--gpu", "--slow"))
    # #endregion


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    want_gpu = config.getoption("--gpu")
    want_slow = config.getoption("--slow")
    # #region agent log
    _agent_dbg(
        "pytest_collection_modifyitems",
        "H2",
        run_id="hook",
        want_gpu=want_gpu,
        want_slow=want_slow,
        n_items=len(items),
    )
    # #endregion
    if not want_gpu and not want_slow:
        return
    selected: list[pytest.Item] = []
    deselected: list[pytest.Item] = []
    for item in items:
        marks = {m.name for m in item.iter_markers()}
        if want_gpu and "gpu" not in marks:
            deselected.append(item)
            continue
        if want_slow and "slow" not in marks:
            deselected.append(item)
            continue
        selected.append(item)
    if deselected:
        config.hook.pytest_deselected(items=deselected)
    items[:] = selected
    # #region agent log
    _agent_dbg(
        "pytest_collection_modifyitems_done",
        "H2",
        run_id="hook",
        kept=len(items),
        deselected=len(deselected),
    )
    # #endregion
