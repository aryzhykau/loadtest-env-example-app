"""
Celery tasks for background processing.
"""
from celery_app import celery_app
import time
import random
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@celery_app.task(name="tasks.process_data", bind=True)
def process_data(self, data_id: str = None, processing_time: int = 5):
    """
    Process a data entry.
    
    Args:
        data_id: ID of the data entry to process
        processing_time: Time to simulate processing (seconds)
    """
    logger.info(f"Processing data entry: {data_id}")
    
    # Simulate processing
    for i in range(processing_time):
        time.sleep(1)
        self.update_state(
            state="PROGRESS",
            meta={
                "current": i + 1,
                "total": processing_time,
                "status": f"Processing step {i + 1}/{processing_time}"
            }
        )
    
    result = {
        "data_id": data_id,
        "processed_at": datetime.utcnow().isoformat(),
        "items_processed": random.randint(100, 1000),
        "success": True
    }
    
    logger.info(f"Completed processing data entry: {data_id}")
    return result


@celery_app.task(name="tasks.generate_report", bind=True)
def generate_report(self, report_type: str = "summary", params: dict = None):
    """
    Generate a report.
    
    Args:
        report_type: Type of report to generate (summary, detailed, analytics)
        params: Additional parameters for report generation
    """
    logger.info(f"Generating {report_type} report")
    
    params = params or {}
    
    # Simulate report generation
    steps = ["Collecting data", "Analyzing", "Formatting", "Finalizing"]
    for i, step in enumerate(steps):
        time.sleep(2)
        self.update_state(
            state="PROGRESS",
            meta={
                "current": i + 1,
                "total": len(steps),
                "status": step
            }
        )
    
    result = {
        "report_type": report_type,
        "generated_at": datetime.utcnow().isoformat(),
        "pages": random.randint(5, 50),
        "file_size_kb": random.randint(100, 5000),
        "download_url": f"/reports/{report_type}_{int(time.time())}.pdf"
    }
    
    logger.info(f"Completed generating {report_type} report")
    return result


@celery_app.task(name="tasks.simulate_load", bind=True)
def simulate_load(self, duration: int = 10, intensity: str = "medium"):
    """
    Simulate load for testing purposes.
    
    Args:
        duration: Duration of the load test in seconds
        intensity: Intensity of the load (low, medium, high)
    """
    logger.info(f"Starting load simulation: {intensity} intensity for {duration}s")
    
    # Map intensity to operations per second
    intensity_map = {
        "low": 10,
        "medium": 50,
        "high": 100
    }
    
    ops_per_second = intensity_map.get(intensity, 50)
    total_operations = 0
    start_time = time.time()
    
    while time.time() - start_time < duration:
        # Simulate work
        for _ in range(ops_per_second):
            # Perform some CPU-bound work
            _ = sum([i ** 2 for i in range(100)])
            total_operations += 1
        
        time.sleep(1)
        
        elapsed = int(time.time() - start_time)
        self.update_state(
            state="PROGRESS",
            meta={
                "current": elapsed,
                "total": duration,
                "operations": total_operations,
                "status": f"Running ({elapsed}/{duration}s)"
            }
        )
    
    result = {
        "duration": duration,
        "intensity": intensity,
        "total_operations": total_operations,
        "ops_per_second": total_operations / duration,
        "completed_at": datetime.utcnow().isoformat()
    }
    
    logger.info(f"Completed load simulation: {total_operations} operations")
    return result


@celery_app.task(name="tasks.long_running_task", bind=True)
def long_running_task(self, iterations: int = 100):
    """
    A long-running task for testing.
    
    Args:
        iterations: Number of iterations to perform
    """
    logger.info(f"Starting long-running task with {iterations} iterations")
    
    results = []
    for i in range(iterations):
        # Simulate work
        time.sleep(0.5)
        results.append(random.randint(1, 100))
        
        # Update progress every 10 iterations
        if (i + 1) % 10 == 0:
            self.update_state(
                state="PROGRESS",
                meta={
                    "current": i + 1,
                    "total": iterations,
                    "status": f"Completed {i + 1}/{iterations} iterations"
                }
            )
    
    result = {
        "iterations": iterations,
        "sum": sum(results),
        "average": sum(results) / len(results),
        "min": min(results),
        "max": max(results),
        "completed_at": datetime.utcnow().isoformat()
    }
    
    logger.info(f"Completed long-running task")
    return result
