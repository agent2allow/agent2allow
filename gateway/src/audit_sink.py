import json
import logging
from collections.abc import Mapping
from datetime import UTC, datetime
from logging.handlers import SysLogHandler
from uuid import uuid4

logger = logging.getLogger(__name__)


class AuditSinkContract:
    def emit(self, event: Mapping[str, object]) -> None:
        raise NotImplementedError


class NoopAuditSink(AuditSinkContract):
    def emit(self, event: Mapping[str, object]) -> None:
        _ = event
        return


class SyslogAuditSink(AuditSinkContract):
    _facilities = {
        "kern": SysLogHandler.LOG_KERN,
        "user": SysLogHandler.LOG_USER,
        "mail": SysLogHandler.LOG_MAIL,
        "daemon": SysLogHandler.LOG_DAEMON,
        "auth": SysLogHandler.LOG_AUTH,
        "lpr": SysLogHandler.LOG_LPR,
        "news": SysLogHandler.LOG_NEWS,
        "uucp": SysLogHandler.LOG_UUCP,
        "cron": SysLogHandler.LOG_CRON,
        "local0": SysLogHandler.LOG_LOCAL0,
        "local1": SysLogHandler.LOG_LOCAL1,
        "local2": SysLogHandler.LOG_LOCAL2,
        "local3": SysLogHandler.LOG_LOCAL3,
        "local4": SysLogHandler.LOG_LOCAL4,
        "local5": SysLogHandler.LOG_LOCAL5,
        "local6": SysLogHandler.LOG_LOCAL6,
        "local7": SysLogHandler.LOG_LOCAL7,
    }

    def __init__(self, *, host: str, port: int, facility: str):
        facility_code = self._facilities.get(facility.lower())
        if facility_code is None:
            raise ValueError(f"unsupported syslog facility: {facility}")
        self._logger = logging.getLogger("agent2allow.audit_sink.syslog")
        self._logger.setLevel(logging.INFO)
        self._logger.propagate = False
        self._handler = SysLogHandler(address=(host, port), facility=facility_code)
        self._logger.handlers.clear()
        self._logger.addHandler(self._handler)

    def emit(self, event: Mapping[str, object]) -> None:
        self._logger.info(json.dumps(dict(event), sort_keys=True, separators=(",", ":")))


class S3JsonAuditSink(AuditSinkContract):
    def __init__(self, *, bucket: str, prefix: str):
        if not bucket:
            raise ValueError("audit_sink_s3_bucket must be set when audit_sink=s3")
        self.bucket = bucket
        self.prefix = prefix
        try:
            import boto3  # type: ignore
        except ImportError as exc:
            raise RuntimeError("boto3 is required for audit_sink=s3") from exc
        self.client = boto3.client("s3")

    def emit(self, event: Mapping[str, object]) -> None:
        key = f"{self.prefix}{datetime.now(UTC).strftime('%Y%m%d')}/{uuid4()}.json"
        payload = json.dumps(dict(event), sort_keys=True, separators=(",", ":")).encode("utf-8")
        self.client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=payload,
            ContentType="application/json",
        )


class AzureBlobAuditSink(AuditSinkContract):
    def __init__(self, *, connection_string: str, container: str, prefix: str):
        if not connection_string:
            raise ValueError("audit_sink_blob_connection_string must be set when audit_sink=blob")
        if not container:
            raise ValueError("audit_sink_blob_container must be set when audit_sink=blob")
        self.container = container
        self.prefix = prefix
        try:
            from azure.storage.blob import BlobServiceClient  # type: ignore
        except ImportError as exc:
            raise RuntimeError("azure-storage-blob is required for audit_sink=blob") from exc
        self.client = BlobServiceClient.from_connection_string(connection_string)

    def emit(self, event: Mapping[str, object]) -> None:
        key = f"{self.prefix}{datetime.now(UTC).strftime('%Y%m%d')}/{uuid4()}.json"
        payload = json.dumps(dict(event), sort_keys=True, separators=(",", ":"))
        blob_client = self.client.get_blob_client(container=self.container, blob=key)
        blob_client.upload_blob(payload, overwrite=True)


def build_audit_sink(
    *,
    sink_type: str,
    syslog_host: str,
    syslog_port: int,
    syslog_facility: str,
    s3_bucket: str,
    s3_prefix: str,
    blob_container: str,
    blob_prefix: str,
    blob_connection_string: str,
) -> AuditSinkContract:
    normalized = sink_type.lower().strip()
    if normalized in {"", "none"}:
        return NoopAuditSink()
    if normalized == "syslog":
        return SyslogAuditSink(
            host=syslog_host,
            port=syslog_port,
            facility=syslog_facility,
        )
    if normalized == "s3":
        return S3JsonAuditSink(bucket=s3_bucket, prefix=s3_prefix)
    if normalized == "blob":
        return AzureBlobAuditSink(
            connection_string=blob_connection_string,
            container=blob_container,
            prefix=blob_prefix,
        )
    raise ValueError(f"unsupported audit sink type: {sink_type}")


def safe_emit(sink: AuditSinkContract, event: Mapping[str, object]) -> None:
    try:
        sink.emit(event)
    except Exception as exc:  # pragma: no cover
        logger.warning("failed to emit audit event to external sink: %s", exc)
