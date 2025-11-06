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
        
        base_time = datetime(2025, 10, 26, 1, 0, 0)
        
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
        
        before_dst = datetime(2025, 10, 26, 1, 0, 0)
        next_run = scheduler.get_next_run(job, before_dst)
        
        self.assertEqual(next_run.hour, 2)
        self.assertEqual(next_run.minute, 30)
        
        after_execution = datetime(2025, 10, 26, 3, 0, 0)
        job["last_run"] = datetime(2025, 10, 26, 2, 30, 0)
        
        next_run_2 = scheduler.get_next_run(job, after_execution)
        expected = datetime(2025, 10, 27, 2, 30, 0)
        
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
        
        start_time = datetime(2025, 10, 26, 0, 30, 0)
        
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
        
        day_before = datetime(2025, 10, 25, 8, 0, 0)
        scheduler.execute_job(job, day_before)
        
        day_after_dst = datetime(2025, 10, 26, 8, 0, 0)
        
        should_run = scheduler.should_run(job, day_after_dst)
        
        self.assertTrue(should_run, 
                       "Job should run 24 hours after last execution, even across DST")


if __name__ == "__main__":
    unittest.main()

