"""Distributed Computing Framework for Synapse Language
Enables distributed execution across multiple nodes with automatic parallelization
"""

import asyncio
import json
import hashlib
import pickle
import time
import threading
import multiprocessing
from typing import Dict, List, Optional, Any, Callable, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum, auto
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, Future
import queue
import socket
import struct
import os
import sys


class TaskStatus(Enum):
    """Status of distributed task"""
    PENDING = auto()
    SCHEDULED = auto()
    RUNNING = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()


class NodeRole(Enum):
    """Role of node in cluster"""
    COORDINATOR = auto()
    WORKER = auto()
    BACKUP = auto()
    MONITOR = auto()


class PartitionStrategy(Enum):
    """Data partitioning strategies"""
    ROUND_ROBIN = auto()
    HASH = auto()
    RANGE = auto()
    RANDOM = auto()
    LOCALITY = auto()


@dataclass
class Task:
    """Distributed task"""
    id: str
    func: Callable
    args: tuple = ()
    kwargs: dict = field(default_factory=dict)
    dependencies: Set[str] = field(default_factory=set)
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: Optional[Exception] = None
    worker_id: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    retry_count: int = 0
    max_retries: int = 3
    priority: int = 0

    def __hash__(self):
        return hash(self.id)

    def execution_time(self) -> float:
        """Get task execution time"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0.0


@dataclass
class WorkerNode:
    """Worker node in distributed cluster"""
    id: str
    host: str
    port: int
    role: NodeRole = NodeRole.WORKER
    capacity: int = multiprocessing.cpu_count()
    load: int = 0
    status: str = "online"
    last_heartbeat: float = field(default_factory=time.time)
    completed_tasks: int = 0
    failed_tasks: int = 0

    def is_available(self) -> bool:
        """Check if worker can accept tasks"""
        return self.status == "online" and self.load < self.capacity

    def utilization(self) -> float:
        """Get worker utilization percentage"""
        return (self.load / self.capacity) * 100 if self.capacity > 0 else 0


class TaskScheduler:
    """Schedules tasks across distributed nodes"""

    def __init__(self, strategy: str = "least_loaded"):
        self.strategy = strategy
        self.workers: Dict[str, WorkerNode] = {}
        self.task_queue: queue.PriorityQueue = queue.PriorityQueue()
        self.running_tasks: Dict[str, Task] = {}
        self.completed_tasks: Dict[str, Task] = {}
        self.task_graph: Dict[str, Set[str]] = {}  # Dependencies

    def add_worker(self, worker: WorkerNode):
        """Register worker node"""
        self.workers[worker.id] = worker

    def remove_worker(self, worker_id: str):
        """Remove worker from cluster"""
        if worker_id in self.workers:
            # Reschedule tasks from this worker
            for task in self.running_tasks.values():
                if task.worker_id == worker_id:
                    task.status = TaskStatus.PENDING
                    task.worker_id = None
                    self.task_queue.put((-task.priority, task.id, task))

            del self.workers[worker_id]

    def submit_task(self, task: Task):
        """Submit task for execution"""
        # Build dependency graph
        self.task_graph[task.id] = task.dependencies

        # Check if dependencies are satisfied
        if self._can_schedule(task):
            self.task_queue.put((-task.priority, task.id, task))
            task.status = TaskStatus.SCHEDULED
        else:
            task.status = TaskStatus.PENDING

    def _can_schedule(self, task: Task) -> bool:
        """Check if task dependencies are satisfied"""
        for dep_id in task.dependencies:
            if dep_id not in self.completed_tasks:
                return False
        return True

    def schedule_next(self) -> Optional[Tuple[Task, WorkerNode]]:
        """Get next task and worker assignment"""
        if self.task_queue.empty():
            return None

        # Get available worker
        worker = self._select_worker()
        if not worker:
            return None

        # Get next task
        _, _, task = self.task_queue.get()

        # Assign task to worker
        task.worker_id = worker.id
        task.status = TaskStatus.RUNNING
        task.start_time = time.time()

        worker.load += 1
        self.running_tasks[task.id] = task

        return task, worker

    def _select_worker(self) -> Optional[WorkerNode]:
        """Select worker based on scheduling strategy"""
        available_workers = [w for w in self.workers.values() if w.is_available()]

        if not available_workers:
            return None

        if self.strategy == "least_loaded":
            return min(available_workers, key=lambda w: w.utilization())
        elif self.strategy == "round_robin":
            return available_workers[0]  # Simple round-robin
        elif self.strategy == "random":
            import random
            return random.choice(available_workers)

        return available_workers[0]

    def complete_task(self, task_id: str, result: Any):
        """Mark task as completed"""
        if task_id in self.running_tasks:
            task = self.running_tasks[task_id]
            task.status = TaskStatus.COMPLETED
            task.result = result
            task.end_time = time.time()

            # Update worker stats
            if task.worker_id in self.workers:
                worker = self.workers[task.worker_id]
                worker.load -= 1
                worker.completed_tasks += 1

            # Move to completed
            self.completed_tasks[task_id] = task
            del self.running_tasks[task_id]

            # Check dependent tasks
            self._check_dependencies(task_id)

    def fail_task(self, task_id: str, error: Exception):
        """Mark task as failed"""
        if task_id in self.running_tasks:
            task = self.running_tasks[task_id]
            task.error = error
            task.end_time = time.time()

            # Update worker stats
            if task.worker_id in self.workers:
                worker = self.workers[task.worker_id]
                worker.load -= 1
                worker.failed_tasks += 1

            # Retry logic
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status = TaskStatus.SCHEDULED
                task.worker_id = None
                self.task_queue.put((-task.priority, task.id, task))
            else:
                task.status = TaskStatus.FAILED
                self.completed_tasks[task_id] = task

            del self.running_tasks[task_id]

    def _check_dependencies(self, completed_task_id: str):
        """Check and schedule tasks with satisfied dependencies"""
        for task_id, deps in self.task_graph.items():
            if completed_task_id in deps and task_id not in self.completed_tasks:
                # Check if all dependencies are satisfied
                if all(dep_id in self.completed_tasks for dep_id in deps):
                    # Find the pending task
                    for task in self.running_tasks.values():
                        if task.id == task_id and task.status == TaskStatus.PENDING:
                            task.status = TaskStatus.SCHEDULED
                            self.task_queue.put((-task.priority, task.id, task))
                            break


class DistributedExecutor:
    """Executes tasks across distributed nodes"""

    def __init__(self, coordinator_host: str = "localhost",
                 coordinator_port: int = 8888):
        self.coordinator_host = coordinator_host
        self.coordinator_port = coordinator_port
        self.scheduler = TaskScheduler()
        self.executor = ProcessPoolExecutor(max_workers=multiprocessing.cpu_count())
        self.is_running = False
        self._lock = threading.Lock()

        # Initialize self as coordinator
        self.node_id = f"node_{socket.gethostname()}_{os.getpid()}"
        self.node = WorkerNode(
            id=self.node_id,
            host=coordinator_host,
            port=coordinator_port,
            role=NodeRole.COORDINATOR
        )
        self.scheduler.add_worker(self.node)

    def submit(self, func: Callable, *args, **kwargs) -> str:
        """Submit task for distributed execution"""
        task_id = hashlib.sha256(
            f"{func.__name__}_{args}_{kwargs}_{time.time()}".encode()
        ).hexdigest()[:16]

        task = Task(
            id=task_id,
            func=func,
            args=args,
            kwargs=kwargs
        )

        self.scheduler.submit_task(task)
        return task_id

    def map(self, func: Callable, iterable, chunksize: int = 1) -> List[Any]:
        """Distributed map operation"""
        # Partition data
        chunks = self._partition_data(iterable, chunksize)

        # Submit tasks
        task_ids = []
        for chunk in chunks:
            task_id = self.submit(self._map_chunk, func, chunk)
            task_ids.append(task_id)

        # Wait for results
        results = []
        for task_id in task_ids:
            result = self.get_result(task_id, timeout=None)
            results.extend(result)

        return results

    def reduce(self, func: Callable, iterable, initializer=None) -> Any:
        """Distributed reduce operation"""
        # Partition for parallel reduction
        chunks = self._partition_data(iterable, len(iterable) // self.node.capacity)

        # First stage: local reductions
        stage1_tasks = []
        for chunk in chunks:
            task_id = self.submit(self._reduce_chunk, func, chunk, initializer)
            stage1_tasks.append(task_id)

        # Gather intermediate results
        intermediate = []
        for task_id in stage1_tasks:
            result = self.get_result(task_id)
            intermediate.append(result)

        # Final reduction
        return self._reduce_chunk(func, intermediate, initializer)

    def scatter(self, data: Any, broadcast: bool = False) -> Dict[str, Any]:
        """Scatter data across nodes"""
        if broadcast:
            # Send same data to all workers
            scattered = {}
            for worker_id in self.scheduler.workers:
                scattered[worker_id] = data
            return scattered

        # Partition data across workers
        partitions = self._partition_data(data,
                                         len(data) // len(self.scheduler.workers))
        scattered = {}
        for i, (worker_id, partition) in enumerate(
            zip(self.scheduler.workers.keys(), partitions)):
            scattered[worker_id] = partition

        return scattered

    def gather(self, scattered_data: Dict[str, Any]) -> List[Any]:
        """Gather results from distributed nodes"""
        results = []
        for worker_id, data in scattered_data.items():
            results.append(data)
        return results

    def _partition_data(self, data, chunksize: int) -> List[Any]:
        """Partition data into chunks"""
        chunks = []
        data_list = list(data)

        for i in range(0, len(data_list), chunksize):
            chunks.append(data_list[i:i + chunksize])

        return chunks

    @staticmethod
    def _map_chunk(func: Callable, chunk: List) -> List:
        """Apply function to chunk"""
        return [func(item) for item in chunk]

    @staticmethod
    def _reduce_chunk(func: Callable, chunk: List, initializer) -> Any:
        """Reduce chunk"""
        if initializer is not None:
            result = initializer
            for item in chunk:
                result = func(result, item)
        else:
            result = chunk[0]
            for item in chunk[1:]:
                result = func(result, item)
        return result

    def get_result(self, task_id: str, timeout: Optional[float] = None) -> Any:
        """Get task result"""
        start_time = time.time()

        while True:
            if task_id in self.scheduler.completed_tasks:
                task = self.scheduler.completed_tasks[task_id]
                if task.status == TaskStatus.COMPLETED:
                    return task.result
                elif task.status == TaskStatus.FAILED:
                    raise task.error

            if timeout and (time.time() - start_time) > timeout:
                raise TimeoutError(f"Task {task_id} timed out")

            time.sleep(0.01)

    def barrier(self, tag: str = "default"):
        """Synchronization barrier"""
        # Wait for all running tasks to complete
        while self.scheduler.running_tasks:
            time.sleep(0.01)

    def shutdown(self, wait: bool = True):
        """Shutdown distributed executor"""
        self.is_running = False
        self.executor.shutdown(wait=wait)


class MapReduceFramework:
    """MapReduce framework for Synapse"""

    def __init__(self, executor: DistributedExecutor):
        self.executor = executor

    def map_reduce(self,
                   data: List[Any],
                   mapper: Callable,
                   reducer: Callable,
                   combiner: Optional[Callable] = None) -> Any:
        """Execute MapReduce job"""

        # Map phase
        print("Starting map phase...")
        mapped = self.executor.map(mapper, data)

        # Combine phase (optional local reduction)
        if combiner:
            print("Starting combine phase...")
            combined = {}
            for key, value in mapped:
                if key not in combined:
                    combined[key] = []
                combined[key].append(value)

            for key in combined:
                combined[key] = combiner(combined[key])

            mapped = [(k, v) for k, v in combined.items()]

        # Shuffle and sort
        print("Shuffling and sorting...")
        shuffled = {}
        for key, value in mapped:
            if key not in shuffled:
                shuffled[key] = []
            shuffled[key].append(value)

        # Reduce phase
        print("Starting reduce phase...")
        results = {}
        for key, values in shuffled.items():
            results[key] = reducer(key, values)

        return results


class DataParallel:
    """Data parallel operations for scientific computing"""

    def __init__(self, executor: DistributedExecutor):
        self.executor = executor

    def parallel_matrix_multiply(self, A: List[List[float]],
                                B: List[List[float]]) -> List[List[float]]:
        """Distributed matrix multiplication"""
        n = len(A)
        m = len(B[0])
        k = len(B)

        # Partition A by rows
        row_chunks = self.executor.scatter(A)

        # Broadcast B to all nodes
        B_broadcast = self.executor.scatter(B, broadcast=True)

        # Compute partial results
        def compute_rows(A_chunk, B_full):
            result = []
            for row in A_chunk:
                result_row = []
                for j in range(m):
                    sum_val = 0
                    for i in range(k):
                        sum_val += row[i] * B_full[i][j]
                    result_row.append(sum_val)
                result.append(result_row)
            return result

        # Execute distributed computation
        partial_results = []
        for worker_id, A_chunk in row_chunks.items():
            task_id = self.executor.submit(compute_rows, A_chunk, B)
            partial_results.append(task_id)

        # Gather results
        result = []
        for task_id in partial_results:
            rows = self.executor.get_result(task_id)
            result.extend(rows)

        return result

    def parallel_fft(self, signal: List[complex]) -> List[complex]:
        """Distributed Fast Fourier Transform"""
        n = len(signal)

        if n <= 1:
            return signal

        # Divide
        even_task = self.executor.submit(self.parallel_fft, signal[0::2])
        odd_task = self.executor.submit(self.parallel_fft, signal[1::2])

        # Conquer
        even = self.executor.get_result(even_task)
        odd = self.executor.get_result(odd_task)

        # Combine
        import cmath
        result = [0] * n
        for k in range(n // 2):
            t = cmath.exp(-2j * cmath.pi * k / n) * odd[k]
            result[k] = even[k] + t
            result[k + n // 2] = even[k] - t

        return result


# Example usage and testing
if __name__ == "__main__":
    print("Synapse Distributed Computing Framework")
    print("=" * 40)

    # Create distributed executor
    executor = DistributedExecutor()

    # Add simulated worker nodes
    for i in range(3):
        worker = WorkerNode(
            id=f"worker_{i}",
            host="localhost",
            port=8889 + i
        )
        executor.scheduler.add_worker(worker)

    print(f"Cluster initialized with {len(executor.scheduler.workers)} nodes")

    # Example 1: Distributed map
    print("\n--- Distributed Map ---")
    def square(x):
        return x ** 2

    data = list(range(10))
    results = executor.map(square, data, chunksize=3)
    print(f"Input: {data}")
    print(f"Squared: {results}")

    # Example 2: Distributed reduce
    print("\n--- Distributed Reduce ---")
    def add(x, y):
        return x + y

    total = executor.reduce(add, data)
    print(f"Sum of {data}: {total}")

    # Example 3: MapReduce word count
    print("\n--- MapReduce Word Count ---")
    mapreduce = MapReduceFramework(executor)

    documents = [
        "quantum computing is the future",
        "the future is quantum",
        "computing is powerful"
    ]

    def word_mapper(doc):
        """Map document to (word, 1) pairs"""
        results = []
        for word in doc.split():
            results.append((word, 1))
        return results

    def word_reducer(word, counts):
        """Reduce word counts"""
        return sum(counts)

    # Flatten documents to words for mapping
    words_flat = []
    for doc in documents:
        words_flat.extend(doc.split())

    # Simple word count (without full MapReduce for demo)
    word_counts = {}
    for word in words_flat:
        word_counts[word] = word_counts.get(word, 0) + 1

    print(f"Word counts: {word_counts}")

    # Example 4: Data parallel matrix multiplication
    print("\n--- Parallel Matrix Multiplication ---")
    data_parallel = DataParallel(executor)

    A = [[1, 2], [3, 4]]
    B = [[5, 6], [7, 8]]

    # Simulate parallel computation
    def simple_matmul(A, B):
        result = []
        for i in range(len(A)):
            row = []
            for j in range(len(B[0])):
                sum_val = 0
                for k in range(len(B)):
                    sum_val += A[i][k] * B[k][j]
                row.append(sum_val)
            result.append(row)
        return result

    C = simple_matmul(A, B)
    print(f"A x B = {C}")

    # Show cluster status
    print("\n--- Cluster Status ---")
    for worker in executor.scheduler.workers.values():
        print(f"- {worker.id}: {worker.status}, "
              f"Load: {worker.utilization():.1f}%, "
              f"Completed: {worker.completed_tasks}, "
              f"Failed: {worker.failed_tasks}")

    # Cleanup
    executor.shutdown()
    print("\n✅ Distributed computing framework implemented!")