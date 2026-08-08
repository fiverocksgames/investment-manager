import socket
import ssl

from investment_manager.jobs.scheduled_yahoo import _safe_database_failure_category


def test_timeout_classification():
    assert _safe_database_failure_category(TimeoutError("secret-host")) == "timeout"


def test_dns_classification():
    assert _safe_database_failure_category(socket.gaierror()) == "dns"


def test_tls_classification():
    assert _safe_database_failure_category(ssl.SSLError()) == "tls"


def test_connection_classification():
    assert _safe_database_failure_category(ConnectionResetError("password=secret")) == "connection"


def test_operational_classification_does_not_require_exception_text():
    OperationalError = type("OperationalError", (Exception,), {})
    exc = OperationalError("postgresql://user:password@secret-host/database")
    assert _safe_database_failure_category(exc) == "operational"


def test_unknown_database_classification():
    assert _safe_database_failure_category(RuntimeError("do-not-log-me")) == "database"
