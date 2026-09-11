import time

class PipelineProfiler:
    """
    High-precision multi-stage performance profiler and logger for document OCR requests.
    Measures and logs all 14 execution steps in milliseconds.
    """
    def __init__(self, name="Document Pipeline"):
        self.name = name
        self.timings = {}
        self.t_start = time.perf_counter()

    def record(self, stage_name, duration_ms):
        self.timings[stage_name] = round(duration_ms, 2)

    def log_summary(self, extra_info=None):
        total_ms = round((time.perf_counter() - self.t_start) * 1000, 2)
        print(f"\n{'='*56}")
        print(f" {self.name} Performance Profiling:")
        print(f"{'-'*56}")
        step_idx = 1
        for stage, duration in self.timings.items():
            print(f"  {step_idx:2d}. {stage:<28}: {duration:8.2f} ms")
            step_idx += 1
        print(f"  {step_idx:2d}. {'Total API response time':<28}: {total_ms:8.2f} ms")
        if extra_info:
            print(f"{'-'*56}")
            for k, v in extra_info.items():
                print(f"  * {k:<28}: {v}")
        print(f"{'='*56}\n", flush=True)
        return total_ms
