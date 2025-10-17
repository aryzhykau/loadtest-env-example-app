"""
Locust load test scenarios for LoadTest Demo Application
Run with: locust -f locustfile.py --host=http://loadtest-{branch}.local
"""

from locust import HttpUser, task, between
import random
import json


class LoadTestUser(HttpUser):
    """Simulates a user interacting with the LoadTest application."""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    
    def on_start(self):
        """Called when a simulated user starts."""
        # Check if backend is healthy before starting
        response = self.client.get("/api/health")
        if response.status_code != 200:
            print(f"Warning: Health check failed with status {response.status_code}")
    
    @task(5)
    def get_health(self):
        """Health check endpoint - most frequent task."""
        self.client.get("/api/health", name="/api/health")
    
    @task(3)
    def get_metrics(self):
        """Get application metrics."""
        self.client.get("/api/metrics", name="/api/metrics")
    
    @task(2)
    def create_data_entry(self):
        """Create a new data entry."""
        payload = {
            "name": f"test-entry-{random.randint(1000, 9999)}",
            "description": "Load test generated entry",
            "value": random.randint(1, 1000),
            "status": random.choice(["active", "inactive"])
        }
        response = self.client.post(
            "/api/data",
            json=payload,
            name="/api/data [POST]"
        )
        if response.status_code == 200:
            # Store the ID for potential updates/deletes
            data = response.json()
            if hasattr(self, 'created_ids'):
                self.created_ids.append(data.get('_id'))
            else:
                self.created_ids = [data.get('_id')]
    
    @task(4)
    def list_data_entries(self):
        """List data entries with pagination."""
        params = {
            "skip": random.randint(0, 20),
            "limit": 10
        }
        self.client.get(
            "/api/data",
            params=params,
            name="/api/data [GET]"
        )
    
    @task(1)
    def create_task(self):
        """Create a Celery task."""
        task_types = ["heavy_compute", "data_processing", "report_generation"]
        payload = {
            "task_type": random.choice(task_types),
            "params": {
                "iterations": random.randint(10, 100),
                "delay": random.uniform(0.1, 1.0)
            }
        }
        response = self.client.post(
            "/api/tasks",
            json=payload,
            name="/api/tasks [POST]"
        )
        if response.status_code == 200:
            data = response.json()
            task_id = data.get('task_id')
            # Check task status
            if task_id:
                self.client.get(
                    f"/api/tasks/{task_id}",
                    name="/api/tasks/{id} [GET]"
                )
    
    @task(1)
    def update_data_entry(self):
        """Update an existing data entry if we have created any."""
        if hasattr(self, 'created_ids') and self.created_ids:
            entry_id = random.choice(self.created_ids)
            payload = {
                "value": random.randint(1, 1000),
                "status": random.choice(["active", "inactive", "archived"])
            }
            self.client.put(
                f"/api/data/{entry_id}",
                json=payload,
                name="/api/data/{id} [PUT]",
                catch_response=True
            )


class HighLoadUser(HttpUser):
    """Simulates high-load user with more aggressive patterns."""
    
    wait_time = between(0.1, 0.5)  # Faster interactions
    
    @task(10)
    def rapid_health_checks(self):
        """Rapid fire health checks."""
        self.client.get("/api/health", name="[HighLoad] /api/health")
    
    @task(5)
    def rapid_data_creation(self):
        """Create data entries rapidly."""
        payload = {
            "name": f"highload-{random.randint(1000, 9999)}",
            "value": random.randint(1, 100),
            "status": "active"
        }
        self.client.post("/api/data", json=payload, name="[HighLoad] /api/data [POST]")
    
    @task(3)
    def rapid_task_creation(self):
        """Create tasks rapidly."""
        payload = {
            "task_type": "heavy_compute",
            "params": {"iterations": 5}
        }
        self.client.post("/api/tasks", json=payload, name="[HighLoad] /api/tasks [POST]")
