from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
import pytest
from colmi_r02_client.cli import cli_client
from unittest.mock import patch, MagicMock
from asyncclick.testing import CliRunner
import anyio
from threading import Thread
from colmi_r02_client.instrumentation.cli import (
    uninstrument_cli,
)
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource


class SyncCliRunner(CliRunner):
    def invoke(self, *a, _sync=False, **k):
        fn = super().invoke
        if _sync:
            return fn(*a, **k)
        result = None

        def f():
            nonlocal result, fn

            async def r():
                try:
                    return await fn(*a, **k)
                except SystemExit as e:
                    # Capture SystemExit and store exit code
                    return type("Result", (), {"exit_code": e.code})

            result = anyio.run(r)

        t = Thread(target=f, name="TEST")
        t.start()
        t.join()
        return result


@pytest.fixture(scope="function")
def runner():
    """Return a synchronous CLI runner."""
    return SyncCliRunner()


@pytest.fixture(scope="module")
def span_exporter():
    """Return an in-memory span exporter."""
    return InMemorySpanExporter()


@pytest.fixture(autouse=True)
def clear_spans(span_exporter):
    """Clear spans before each test."""
    span_exporter.clear()
    yield


@pytest.fixture(autouse=True)
def uninstrument():
    """Uninstrument the CLI before each test."""
    uninstrument_cli()
    yield


@pytest.fixture(autouse=True)
def colmi_client():
    with patch("colmi_r02_client.cli.Client", autospec=True):
        yield


@pytest.fixture(scope="module", autouse=True)
def patch_otel_provider(span_exporter: InMemorySpanExporter):
    with patch("colmi_r02_client.instrumentation.cli._configure_tracer_provider", return_value=MagicMock()):
        tracer_provider = TracerProvider(resource=Resource({}))
        trace.set_tracer_provider(tracer_provider)

        processor = SimpleSpanProcessor(span_exporter)
        tracer_provider.add_span_processor(processor)
        yield


@pytest.mark.parametrize(
    "command,args",
    [
        ("info", []),
        ("get-heart-rate-log", ["--target", "2023-01-01"]),
        ("set-time", []),
        ("get-heart-rate-log-settings", []),
        ("set-heart-rate-log-settings", ["--enable"]),
        ("get-real-time", ["heart-rate"]),
        ("get-steps", []),
        ("reboot", []),
        ("raw", ["--command", "1", "--replies", "1"]),
        ("sync", []),
    ],
)
def test_command_spans(command, args, span_exporter, runner):
    cmd_args = ["--otel", "--address", "test", command, *args]
    runner.invoke(cli_client, cmd_args)

    # Verify spans
    spans = span_exporter.get_finished_spans()
    assert len(spans) == 1, f"Expected 1 span, got {[span.name for span in spans]}"

    # Verify span details
    span = spans[0]
    assert span.name == command, f"Expected span name '{command}', got {span.name}"
