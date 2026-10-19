import json
import os
import sys
import tempfile
import time
import pytest

from app import create_app
from database import init_db

_test_results = {}
_start_time = None

def pytest_sessionstart(session):
    global _start_time
    _start_time = time.time()

def pytest_report_teststatus(report, config):
    # Suppress pytest's default single-character progress symbols
    return report.outcome, "", ""

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" or (report.when == "setup" and report.failed):
        test_name = item.name
        exec_ms = max(1, int(round(report.duration * 1000)))
        
        if report.passed:
            _test_results[test_name] = {
                "Status": "passed",
                "Execution time": f"{exec_ms}ms"
            }
        elif report.failed:
            error_msg = ""
            raw_text = ""
            if hasattr(report, "longreprtext") and report.longreprtext:
                raw_text = report.longreprtext
            elif hasattr(report, "longrepr") and report.longrepr:
                raw_text = str(report.longrepr)

            if raw_text:
                for line in raw_text.splitlines():
                    cleaned = line.strip()
                    if "AssertionError:" in cleaned:
                        error_msg = cleaned.split("AssertionError:", 1)[1].strip()
                        break
                    elif cleaned.startswith("E   "):
                        error_msg = cleaned[4:].strip()
                if not error_msg:
                    non_empty = [l.strip() for l in raw_text.splitlines() if l.strip()]
                    if non_empty:
                        error_msg = non_empty[-1]

            if not error_msg:
                error_msg = "Test failed"

            _test_results[test_name] = {
                "Status": "failed",
                "Execution time": f"{exec_ms}ms",
                "Error": error_msg
            }

def pytest_terminal_summary(terminalreporter, exitstatus, config):
    terminalreporter.summary_stats = lambda: None
    terminalreporter.summary_failures = lambda: None
    terminalreporter.summary_errors = lambda: None
    terminalreporter.short_test_summary = lambda: None

    passed_count = sum(1 for r in _test_results.values() if r.get("Status") == "passed")
    failed_count = sum(1 for r in _test_results.values() if r.get("Status") == "failed")
    total_time_ms = int(round((time.time() - (_start_time or time.time())) * 1000))

    output = dict(_test_results)
    output["Passed"] = passed_count
    output["Failed"] = failed_count
    output["Total bugs"] = passed_count + failed_count
    output["Total Execution time"] = f"{total_time_ms}ms"

    sys.stdout.write(json.dumps(output, indent=2) + "\n")
    sys.stdout.flush()

@pytest.fixture
def app_instance():
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)
    
    flask_app = create_app({
        "TESTING": True,
        "DATABASE": db_path
    })

    yield flask_app

    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except OSError:
            pass

@pytest.fixture
def client(app_instance):
    return app_instance.test_client()
