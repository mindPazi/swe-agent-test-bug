# Solution: Ambiguous Rome Bug

## Root Causes

### 1. Naive Datetime Arithmetic
The scheduler uses naive datetime objects (without timezone information) and performs arithmetic with `timedelta`. During DST transitions, this causes incorrect calculations because:
- When clocks fall back (DST → standard time), the hour 02:30 occurs twice
- Naive datetime arithmetic doesn't account for the actual elapsed time in the timezone
- Using `datetime.now()` without timezone info creates ambiguous timestamps

### 2. Missing tzdata in Docker
The official Python slim images don't include timezone database files. When code tries to use `ZoneInfo("Europe/Rome")`, it fails with `ZoneInfoNotFoundError` in the container while working locally (if tzdata is installed on the host).

### 3. time.time() During DST Transition
The `measure_execution_time` function uses `time.time()` which returns UNIX timestamps. During DST transitions, if the system clock is adjusted backward, `end - start` can become negative or incorrect, causing flaky test behavior.

## Complete Fix

### Step 1: Fix Dockerfile - Add tzdata
```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends tzdata && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-m", "pytest", "test_scheduler.py", "-v"]
```

### Step 2: Fix scheduler.py - Use Timezone-Aware Datetimes

Replace the entire `scheduler.py` with timezone-aware implementation:

```python
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
            current_time = datetime.now(self.timezone)
        elif current_time.tzinfo is None:
            current_time = current_time.replace(tzinfo=self.timezone)
        
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
            current_time = datetime.now(self.timezone)
        elif current_time.tzinfo is None:
            current_time = current_time.replace(tzinfo=self.timezone)
        
        if job["last_run"] is None:
            next_run = self.get_next_run(job, current_time)
            if current_time >= next_run:
                return True
            return False
        
        last_run_aware = job["last_run"]
        if last_run_aware.tzinfo is None:
            last_run_aware = last_run_aware.replace(tzinfo=self.timezone)
        
        time_since_last = current_time - last_run_aware
        expected_interval = timedelta(hours=job["interval_hours"])
        
        return time_since_last >= expected_interval
    
    def execute_job(self, job, current_time=None):
        if current_time is None:
            current_time = datetime.now(self.timezone)
        elif current_time.tzinfo is None:
            current_time = current_time.replace(tzinfo=self.timezone)
        
        job["last_run"] = current_time
        return f"Executed {job['name']} at {current_time}"
    
    def run_pending(self, current_time=None):
        if current_time is None:
            current_time = datetime.now(self.timezone)
        elif current_time.tzinfo is None:
            current_time = current_time.replace(tzinfo=self.timezone)
        
        executed = []
        for job in self.jobs:
            if self.should_run(job, current_time):
                result = self.execute_job(job, current_time)
                executed.append(result)
        
        return executed


def measure_execution_time(func):
    start = time.monotonic()
    result = func()
    end = time.monotonic()
    duration = end - start
    return result, duration
```

### Step 3: Fix test_scheduler.py - Use Timezone-Aware Test Times

Update tests to use timezone-aware datetimes:

```python
import unittest
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from scheduler import JobScheduler, measure_execution_time
import time


class TestJobScheduler(unittest.TestCase):
    
    def test_dst_transition_october_2025(self):
        scheduler = JobScheduler("Europe/Rome")
        job = scheduler.add_job("daily_report", hour=2, minute=30, interval_hours=24)
        
        rome_tz = ZoneInfo("Europe/Rome")
        
        base_time = datetime(2025, 10, 26, 1, 0, 0, tzinfo=rome_tz)
        
        executions = []
        current = base_time
        
        for i in range(48):
            results = scheduler.run_pending(current)
            if results:
                executions.append((current, results))
            current = current + timedelta(hours=1)
        
        self.assertEqual(len(executions), 2, 
                        f"Expected exactly 2 executions in 48 hours, got {len(executions)}")
        
        if len(executions) >= 2:
            first_exec = executions[0][0]
            second_exec = executions[1][0]
            
            time_diff = second_exec - first_exec
            self.assertEqual(time_diff, timedelta(hours=24),
                           f"Expected 24 hours between executions, got {time_diff}")
    
    def test_next_run_calculation_during_dst(self):
        scheduler = JobScheduler("Europe/Rome")
        job = scheduler.add_job("backup", hour=2, minute=30)
        
        rome_tz = ZoneInfo("Europe/Rome")
        before_dst = datetime(2025, 10, 26, 1, 0, 0, tzinfo=rome_tz)
        next_run = scheduler.get_next_run(job, before_dst)
        
        self.assertEqual(next_run.hour, 2)
        self.assertEqual(next_run.minute, 30)
        
        after_execution = datetime(2025, 10, 26, 3, 0, 0, tzinfo=rome_tz)
        job["last_run"] = datetime(2025, 10, 26, 2, 30, 0, tzinfo=rome_tz)
        
        next_run_2 = scheduler.get_next_run(job, after_execution)
        expected = datetime(2025, 10, 27, 2, 30, 0, tzinfo=rome_tz)
        
        self.assertEqual(next_run_2, expected)
    
    def test_execution_timing_stability(self):
        scheduler = JobScheduler("Europe/Rome")
        
        def quick_job():
            time.sleep(0.01)
            return "done"
        
        durations = []
        
        for i in range(5):
            result, duration = measure_execution_time(quick_job)
            durations.append(duration)
        
        for d in durations:
            self.assertGreater(d, 0, "Duration should always be positive")
            self.assertLess(d, 1.0, "Duration should be less than 1 second")
    
    def test_hourly_job_during_dst_transition(self):
        scheduler = JobScheduler("Europe/Rome")
        job = scheduler.add_job("hourly_sync", hour=2, minute=0, interval_hours=1)
        
        rome_tz = ZoneInfo("Europe/Rome")
        start_time = datetime(2025, 10, 26, 0, 30, 0, tzinfo=rome_tz)
        
        executions = []
        current = start_time
        
        for i in range(6):
            if scheduler.should_run(job, current):
                scheduler.execute_job(job, current)
                executions.append(current)
            current = current + timedelta(hours=1)
        
        self.assertEqual(len(executions), 5,
                        f"Expected 5 executions for hourly job, got {len(executions)}")
    
    def test_job_not_skipped_after_dst(self):
        scheduler = JobScheduler("Europe/Rome")
        job = scheduler.add_job("morning_task", hour=8, minute=0, interval_hours=24)
        
        rome_tz = ZoneInfo("Europe/Rome")
        day_before = datetime(2025, 10, 25, 8, 0, 0, tzinfo=rome_tz)
        scheduler.execute_job(job, day_before)
        
        day_after_dst = datetime(2025, 10, 26, 8, 0, 0, tzinfo=rome_tz)
        
        should_run = scheduler.should_run(job, day_after_dst)
        
        self.assertTrue(should_run, 
                       "Job should run 24 hours after last execution, even across DST")


if __name__ == "__main__":
    unittest.main()
```

## Key Changes Summary

1. **tzdata installation**: Added `tzdata` package to Dockerfile so `ZoneInfo` works in container
2. **Timezone-aware datetimes**: All datetime operations now use timezone-aware objects with `tzinfo=self.timezone`
3. **time.monotonic()**: Replaced `time.time()` with `time.monotonic()` for duration measurement (monotonic clock is never adjusted)
4. **Consistent timezone handling**: All methods check if incoming datetime is naive and convert it to timezone-aware

## Why This Was Hard for an Agent

1. **Multi-layered problem**: Three separate issues (naive datetime, missing tzdata, time.time()) that interact
2. **Environment-dependent**: Works locally but fails in Docker, making it hard to diagnose
3. **DST edge case**: Only manifests during specific dates (DST transitions)
4. **Subtle timezone semantics**: Understanding fold parameter and ambiguous times requires domain knowledge
5. **Testing complexity**: Need to simulate specific dates and understand timezone behavior

