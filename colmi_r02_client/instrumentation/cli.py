from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource, ResourceAttributes
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SpanExporter
from logging import getLogger
import os

from opentelemetry.instrumentation.asyncclick import AsyncClickInstrumentor

tracer = trace.get_tracer(__name__)
_logger = getLogger(__name__)


def _configure_tracer_provider(exporter: SpanExporter) -> TracerProvider:
    """Configure the OTLP exporter with appropriate resource attributes."""
    _logger.debug("Configuring tracer provider")
    resource = Resource(
        attributes={
            ResourceAttributes.SERVICE_NAME: "colmi_r02_client",
        }
    )
    tracer_provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer_provider)

    processor = BatchSpanProcessor(exporter)
    tracer_provider.add_span_processor(processor)
    _logger.debug("Tracer provider configured")
    return tracer_provider


_asyncclick_instrumentor = AsyncClickInstrumentor()


def instrument_cli():
    _logger.debug("Instrumenting CLI")
    if os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT") is None and os.getenv("OTEL_EXPORTER_OTLP_TRACES_ENDPOINT") is None:
        _logger.info("OTEL_EXPORTER_OTLP_ENDPOINT not set, defaulting to http://localhost:4318.")
    exporter = OTLPSpanExporter()
    _configure_tracer_provider(exporter=exporter)
    _asyncclick_instrumentor.instrument()
    _logger.debug("CLI instrumented")


def uninstrument_cli():
    _logger.debug("Uninstrumenting CLI")
    _asyncclick_instrumentor.uninstrument()
    _logger.debug("CLI uninstrumented")
