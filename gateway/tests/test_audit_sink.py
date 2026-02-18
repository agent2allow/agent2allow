import pytest

from src.audit_sink import NoopAuditSink, SyslogAuditSink, build_audit_sink


def test_build_audit_sink_none():
    sink = build_audit_sink(
        sink_type="none",
        syslog_host="localhost",
        syslog_port=514,
        syslog_facility="user",
        s3_bucket="",
        s3_prefix="agent2allow/audit/",
        blob_container="",
        blob_prefix="agent2allow/audit/",
        blob_connection_string="",
    )
    assert isinstance(sink, NoopAuditSink)


def test_build_audit_sink_syslog():
    sink = build_audit_sink(
        sink_type="syslog",
        syslog_host="localhost",
        syslog_port=514,
        syslog_facility="user",
        s3_bucket="",
        s3_prefix="agent2allow/audit/",
        blob_container="",
        blob_prefix="agent2allow/audit/",
        blob_connection_string="",
    )
    assert isinstance(sink, SyslogAuditSink)


def test_build_audit_sink_rejects_unknown_type():
    with pytest.raises(ValueError):
        build_audit_sink(
            sink_type="unknown",
            syslog_host="localhost",
            syslog_port=514,
            syslog_facility="user",
            s3_bucket="",
            s3_prefix="agent2allow/audit/",
            blob_container="",
            blob_prefix="agent2allow/audit/",
            blob_connection_string="",
        )
