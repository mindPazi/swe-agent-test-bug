from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import time


class JobScheduler:
    def __init__(self, timezone_name="Europe/Rome"):
        self.timezone = ZoneInfo(timezone_name)
        self.jobs = []
    
    def add_job(self, name, hour, minute, interval_hours=24):
        job = {
            "name": name,
            "hour": hour,
            "minute": minute,
            "interval_hours": interval_hours,
            "last_run": None
        }
        self.jobs.append(job)
        return job
    
    def get_next_run(self, job, current_time=None):
        if current_time is None:
            current_time = datetime.now()
        
        target = current_time.replace(
            hour=job["hour"],
            minute=job["minute"],
            second=0,
            microsecond=0
        )
        
        if current_time >= target:
            target = target + timedelta(hours=job["interval_hours"])
        
        return target
    
    def should_run(self, job, current_time=None):
        if current_time is None:
            current_time = datetime.now()
        
        if job["last_run"] is None:
            next_run = self.get_next_run(job, current_time)
            if current_time >= next_run:
                return True
            return False
        
        time_since_last = current_time - job["last_run"]
        expected_interval = timedelta(hours=job["interval_hours"])
        
        return time_since_last >= expected_interval
    
    def execute_job(self, job, current_time=None):
        if current_time is None:
            current_time = datetime.now()
        
        job["last_run"] = current_time
        return f"Executed {job['name']} at {current_time}"
    
    def run_pending(self, current_time=None):
        if current_time is None:
            current_time = datetime.now()
        
        executed = []
        for job in self.jobs:
            if self.should_run(job, current_time):
                result = self.execute_job(job, current_time)
                executed.append(result)
        
        return executed


def measure_execution_time(func):
    start = time.time()
    result = func()
    end = time.time()
    duration = end - start
    return result, duration

