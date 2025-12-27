class MetricsStore: 
    def __init__(self):
        self.total_requests = 0
        self.total_errors = 0
        self.total_domain_errors = 0
        self.total_internal_errors = 0
        self.total_response_time = 0 # accumulated in ms

    def record_request(self):
        self.total_requests += 1

    def record_domain_error(self):
        self.total_domain_errors += 1
        self.total_errors +=1

    def record_internal_error(self):
        self.total_internal_errors += 1
        self.total_errors +=1
    
    def record_response_time(self, duration_ms: float):
        self.total_response_time += duration_ms

    @property
    def average_response_time(self) -> float:
        if self.total_requests == 0:
            return 0
        return self.total_response_time / self.total_requests

metrics = MetricsStore()