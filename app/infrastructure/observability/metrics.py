from collections import defaultdict
from math import inf
from threading import Lock
from time import perf_counter

from fastapi import FastAPI, Request, Response


EXCLUDED_PATHS = frozenset({"/metrics"})
CONTENT_TYPE = "text/plain; version=0.0.4; charset=utf-8"
HISTOGRAM_BUCKETS = (0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, inf)


class HttpMetrics:
    def __init__(self) -> None:
        self._lock = Lock()
        self._requests: dict[tuple[str, str, str], int] = defaultdict(int)
        self._in_progress: dict[str, int] = defaultdict(int)
        self._duration_count: dict[tuple[str, str], int] = defaultdict(int)
        self._duration_sum: dict[tuple[str, str], float] = defaultdict(float)
        self._duration_buckets: dict[tuple[str, str, float], int] = defaultdict(int)

    def start_request(self, method: str) -> None:
        with self._lock:
            self._in_progress[method] += 1

    def finish_request(
        self,
        method: str,
        route: str,
        status_code: int,
        duration: float,
    ) -> None:
        with self._lock:
            self._in_progress[method] -= 1
            self._requests[(method, route, str(status_code))] += 1
            self._duration_count[(method, route)] += 1
            self._duration_sum[(method, route)] += duration
            for bucket in HISTOGRAM_BUCKETS:
                if duration <= bucket:
                    self._duration_buckets[(method, route, bucket)] += 1

    def render(self) -> str:
        with self._lock:
            lines = [
                "# HELP http_requests_total Total number of HTTP requests.",
                "# TYPE http_requests_total counter",
            ]
            for labels, value in sorted(self._requests.items()):
                method, route, status_code = labels
                lines.append(
                    "http_requests_total"
                    f'{{method="{method}",route="{route}",status_code="{status_code}"}} {value}'
                )

            lines.extend(
                [
                    "# HELP http_request_duration_seconds HTTP request duration in seconds.",
                    "# TYPE http_request_duration_seconds histogram",
                ]
            )
            for method, route in sorted(self._duration_count):
                labels = f'method="{method}",route="{route}"'
                for bucket in HISTOGRAM_BUCKETS:
                    upper_bound = "+Inf" if bucket == inf else str(bucket)
                    value = self._duration_buckets[(method, route, bucket)]
                    lines.append(
                        "http_request_duration_seconds_bucket"
                        f'{{{labels},le="{upper_bound}"}} {value}'
                    )
                lines.append(
                    f"http_request_duration_seconds_count{{{labels}}} "
                    f"{self._duration_count[(method, route)]}"
                )
                lines.append(
                    f"http_request_duration_seconds_sum{{{labels}}} "
                    f"{self._duration_sum[(method, route)]}"
                )

            lines.extend(
                [
                    "# HELP http_requests_in_progress Number of HTTP requests currently in progress.",
                    "# TYPE http_requests_in_progress gauge",
                ]
            )
            for method, value in sorted(self._in_progress.items()):
                lines.append(f'http_requests_in_progress{{method="{method}"}} {value}')

            return "\n".join(lines) + "\n"


HTTP_METRICS = HttpMetrics()


def _route_template(request: Request) -> str:
    route = request.scope.get("route")
    return getattr(route, "path", "unmatched")


def instrument_app(app: FastAPI) -> None:
    @app.middleware("http")
    async def record_http_metrics(request: Request, call_next):
        if request.url.path in EXCLUDED_PATHS:
            return await call_next(request)

        method = request.method
        started_at = perf_counter()
        status_code = 500
        HTTP_METRICS.start_request(method)

        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception:
            raise
        finally:
            route = _route_template(request)
            HTTP_METRICS.finish_request(
                method=method,
                route=route,
                status_code=status_code,
                duration=perf_counter() - started_at,
            )

        return response


async def metrics_response() -> Response:
    return Response(content=HTTP_METRICS.render(), headers={"Content-Type": CONTENT_TYPE})
