#!/usr/bin/env python3
"""Simple test for distributed computing framework"""

from synapse_lang.distributed import *
import time

def main():
    print("Synapse Distributed Computing - Simple Test")
    print("=" * 40)

    # Create scheduler and add workers
    scheduler = TaskScheduler()

    # Add workers
    for i in range(3):
        worker = WorkerNode(
            id=f"worker_{i}",
            host="localhost",
            port=8889 + i
        )
        scheduler.add_worker(worker)

    print(f"Created scheduler with {len(scheduler.workers)} workers")

    # Test task creation
    def test_func(x):
        return x * 2

    task = Task(
        id="test_task_1",
        func=test_func,
        args=(5,)
    )

    print(f"Created task: {task.id}")

    # Test scheduling
    scheduler.submit_task(task)
    print(f"Task status: {task.status}")

    # Test worker selection
    next_assignment = scheduler.schedule_next()
    if next_assignment:
        task, worker = next_assignment
        print(f"Assigned task {task.id} to worker {worker.id}")

        # Simulate completion
        scheduler.complete_task(task.id, 10)
        print(f"Task completed with result: {task.result}")

    # Show worker stats
    print("\n--- Worker Status ---")
    for worker in scheduler.workers.values():
        print(f"- {worker.id}: Load {worker.load}, "
              f"Completed {worker.completed_tasks}, "
              f"Utilization {worker.utilization():.1f}%")

    print("\n✅ Distributed framework basic test completed!")

if __name__ == "__main__":
    main()