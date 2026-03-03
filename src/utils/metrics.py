from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time

# Define metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP Requests', ['method', 'endpoint', 'status'])# used to count endpoinds and methods(get,post)
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP Request Latency', ['method', 'endpoint'])# used to measure latency 

class PrometheusMiddleware(BaseHTTPMiddleware):   #define medilwere to connect with fastapi 
    async def dispatch(self, request: Request, call_next): # work with each request
        start_time= time.time()
        response = await call_next(request) # call next call the function in the endpoint in routes
        duration = time.time() - start_time 
        endpoint = request.url.path #the name of end point like (process/1)

        REQUEST_COUNT.labels(method=request.method,endpoint=endpoint,status=response.status_code).inc()
        REQUEST_LATENCY.labels(method=request.method,endpoint=endpoint).observe(duration)

        return response

    # a function which fastapi use to setup middleware 
def setup_metrics(app: FastAPI):# take the app to inject thr middlewre in it and it well create new end point call metrices for pomesus
        """
        Setup Prometheus metrics middleware and endpoint
        """
        # Add Prometheus middleware
        app.add_middleware(PrometheusMiddleware)
        @app.get("/for_sec", include_in_schema=False)
        def metrics():
            return Response(generate_latest(),media_type=CONTENT_TYPE_LATEST)#generate_latest get the last included statics from promesus_clint,generate_latest mean i need latest content