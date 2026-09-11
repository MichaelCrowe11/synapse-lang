"""
Synapse Quantum Auto-Scaling Service
AWS Auto Scaling equivalent for quantum computing workloads
"""

import asyncio
import math
import statistics
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any


class ScalingPolicy(str, Enum):
    """Auto-scaling policies"""
    TARGET_TRACKING = "target_tracking"        # Scale to maintain target metric
    STEP_SCALING = "step_scaling"              # Scale by steps based on alarms
    PREDICTIVE_SCALING = "predictive_scaling"  # ML-based predictive scaling
    SCHEDULED_SCALING = "scheduled_scaling"    # Time-based scaling

class MetricType(str, Enum):
    """Metrics for auto-scaling decisions"""
    QUEUE_DEPTH = "queue_depth"                # Number of queued jobs
    AVERAGE_WAIT_TIME = "average_wait_time"    # Average job wait time
    QUANTUM_UTILIZATION = "quantum_utilization" # % of quantum resources used
    ERROR_RATE = "error_rate"                  # Job failure rate
    COST_PER_JOB = "cost_per_job"             # Average cost efficiency
    THROUGHPUT = "throughput"                  # Jobs completed per hour

class ScalingDirection(str, Enum):
    """Scaling direction"""
    UP = "up"
    DOWN = "down"

@dataclass
class QuantumMetric:
    """Quantum computing metric for auto-scaling"""
    metric_type: MetricType
    value: float
    timestamp: datetime
    unit: str
    source: str  # Which quantum backend/service

@dataclass
class ScalingTarget:
    """Target for scaling actions"""
    resource_type: str  # "quantum_executors", "job_queue_workers", etc.
    min_capacity: int
    max_capacity: int
    desired_capacity: int
    current_capacity: int

@dataclass
class AutoScalingPolicy:
    """Auto-scaling policy configuration"""
    policy_id: str
    policy_name: str
    policy_type: ScalingPolicy
    target_resource: str

    # Target tracking policy settings
    target_value: float | None = None
    metric_type: MetricType | None = None

    # Step scaling policy settings
    scaling_steps: list[dict[str, Any]] | None = None

    # Predictive scaling settings
    prediction_horizon_minutes: int = 60

    # Scheduled scaling settings
    schedule: dict[str, Any] | None = None

    # General settings
    cooldown_period_seconds: int = 300  # 5 minutes
    enabled: bool = True
    created_at: datetime = None

@dataclass
class ScalingAction:
    """Record of a scaling action taken"""
    action_id: str
    policy_id: str
    resource_type: str
    direction: ScalingDirection
    old_capacity: int
    new_capacity: int
    trigger_metric: QuantumMetric
    timestamp: datetime
    success: bool
    error_message: str | None = None

class QuantumAutoScaler:
    """Main quantum auto-scaling service"""

    def __init__(self):
        self.scaling_targets = {}  # resource_type -> ScalingTarget
        self.scaling_policies = {}  # policy_id -> AutoScalingPolicy
        self.metrics_history = []  # List[QuantumMetric]
        self.scaling_actions = []  # List[ScalingAction]
        self.predictive_models = {}  # metric_type -> ML model

        # Initialize default scaling targets
        self._initialize_default_targets()

        # Initialize default policies
        self._initialize_default_policies()

        # Start monitoring loop
        self.monitoring_task = None

    def _initialize_default_targets(self):
        """Initialize default scaling targets"""

        self.scaling_targets = {
            "quantum_executors": ScalingTarget(
                resource_type="quantum_executors",
                min_capacity=1,
                max_capacity=50,
                desired_capacity=3,
                current_capacity=3
            ),
            "job_queue_workers": ScalingTarget(
                resource_type="job_queue_workers",
                min_capacity=2,
                max_capacity=20,
                desired_capacity=5,
                current_capacity=5
            ),
            "circuit_optimizers": ScalingTarget(
                resource_type="circuit_optimizers",
                min_capacity=1,
                max_capacity=10,
                desired_capacity=2,
                current_capacity=2
            )
        }

    def _initialize_default_policies(self):
        """Initialize default auto-scaling policies"""

        # Queue depth target tracking policy
        queue_policy = AutoScalingPolicy(
            policy_id="queue-depth-target-tracking",
            policy_name="Queue Depth Target Tracking",
            policy_type=ScalingPolicy.TARGET_TRACKING,
            target_resource="quantum_executors",
            target_value=10.0,  # Target 10 jobs in queue
            metric_type=MetricType.QUEUE_DEPTH,
            cooldown_period_seconds=300,
            created_at=datetime.utcnow()
        )

        # Wait time step scaling policy
        wait_time_policy = AutoScalingPolicy(
            policy_id="wait-time-step-scaling",
            policy_name="Wait Time Step Scaling",
            policy_type=ScalingPolicy.STEP_SCALING,
            target_resource="quantum_executors",
            scaling_steps=[
                {"lower_bound": 0, "upper_bound": 30, "scaling_adjustment": 0},    # 0-30s: no action
                {"lower_bound": 30, "upper_bound": 60, "scaling_adjustment": 1},   # 30-60s: +1
                {"lower_bound": 60, "upper_bound": 120, "scaling_adjustment": 2},  # 60-120s: +2
                {"lower_bound": 120, "upper_bound": None, "scaling_adjustment": 5} # >120s: +5
            ],
            cooldown_period_seconds=180,
            created_at=datetime.utcnow()
        )

        # Predictive scaling for peak hours
        predictive_policy = AutoScalingPolicy(
            policy_id="predictive-scaling-peak-hours",
            policy_name="Predictive Scaling for Peak Hours",
            policy_type=ScalingPolicy.PREDICTIVE_SCALING,
            target_resource="quantum_executors",
            prediction_horizon_minutes=60,
            cooldown_period_seconds=600,  # 10 minutes
            created_at=datetime.utcnow()
        )

        # Scheduled scaling for business hours
        scheduled_policy = AutoScalingPolicy(
            policy_id="scheduled-business-hours",
            policy_name="Scheduled Scaling for Business Hours",
            policy_type=ScalingPolicy.SCHEDULED_SCALING,
            target_resource="quantum_executors",
            schedule={
                "timezone": "UTC",
                "rules": [
                    {"time": "08:00", "days": [1,2,3,4,5], "desired_capacity": 10},  # Weekday morning
                    {"time": "18:00", "days": [1,2,3,4,5], "desired_capacity": 5},   # Weekday evening
                    {"time": "08:00", "days": [6,7], "desired_capacity": 3},        # Weekend
                ]
            },
            created_at=datetime.utcnow()
        )

        # Store policies
        for policy in [queue_policy, wait_time_policy, predictive_policy, scheduled_policy]:
            self.scaling_policies[policy.policy_id] = policy

    async def start_monitoring(self):
        """Start the auto-scaling monitoring loop"""
        if self.monitoring_task is None:
            self.monitoring_task = asyncio.create_task(self._monitoring_loop())

    async def stop_monitoring(self):
        """Stop the auto-scaling monitoring loop"""
        if self.monitoring_task:
            self.monitoring_task.cancel()
            self.monitoring_task = None

    async def _monitoring_loop(self):
        """Main monitoring loop that checks metrics and triggers scaling"""

        while True:
            try:
                # Collect current metrics
                current_metrics = await self._collect_metrics()

                # Store metrics for history
                self.metrics_history.extend(current_metrics)

                # Keep only last 24 hours of metrics
                cutoff_time = datetime.utcnow() - timedelta(hours=24)
                self.metrics_history = [
                    m for m in self.metrics_history if m.timestamp > cutoff_time
                ]

                # Evaluate scaling policies
                for policy in self.scaling_policies.values():
                    if policy.enabled:
                        await self._evaluate_policy(policy, current_metrics)

                # Wait before next check
                await asyncio.sleep(30)  # Check every 30 seconds

            except Exception as e:
                print(f"Error in auto-scaling monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait longer on error

    async def _collect_metrics(self) -> list[QuantumMetric]:
        """Collect current quantum computing metrics"""

        now = datetime.utcnow()
        metrics = []

        # Simulate metric collection (in real system, would query actual services)

        # Queue depth metric
        queue_depth = await self._get_queue_depth()
        metrics.append(QuantumMetric(
            metric_type=MetricType.QUEUE_DEPTH,
            value=queue_depth,
            timestamp=now,
            unit="jobs",
            source="quantum_job_queue"
        ))

        # Average wait time metric
        avg_wait_time = await self._get_average_wait_time()
        metrics.append(QuantumMetric(
            metric_type=MetricType.AVERAGE_WAIT_TIME,
            value=avg_wait_time,
            timestamp=now,
            unit="seconds",
            source="quantum_executor_service"
        ))

        # Quantum utilization metric
        utilization = await self._get_quantum_utilization()
        metrics.append(QuantumMetric(
            metric_type=MetricType.QUANTUM_UTILIZATION,
            value=utilization,
            timestamp=now,
            unit="percent",
            source="quantum_resource_monitor"
        ))

        # Error rate metric
        error_rate = await self._get_error_rate()
        metrics.append(QuantumMetric(
            metric_type=MetricType.ERROR_RATE,
            value=error_rate,
            timestamp=now,
            unit="percent",
            source="quantum_job_tracker"
        ))

        # Throughput metric
        throughput = await self._get_throughput()
        metrics.append(QuantumMetric(
            metric_type=MetricType.THROUGHPUT,
            value=throughput,
            timestamp=now,
            unit="jobs_per_hour",
            source="quantum_analytics"
        ))

        return metrics

    async def _evaluate_policy(self, policy: AutoScalingPolicy, current_metrics: list[QuantumMetric]):
        """Evaluate a scaling policy and take action if needed"""

        # Check cooldown period
        if await self._is_in_cooldown(policy):
            return

        if policy.policy_type == ScalingPolicy.TARGET_TRACKING:
            await self._evaluate_target_tracking_policy(policy, current_metrics)
        elif policy.policy_type == ScalingPolicy.STEP_SCALING:
            await self._evaluate_step_scaling_policy(policy, current_metrics)
        elif policy.policy_type == ScalingPolicy.PREDICTIVE_SCALING:
            await self._evaluate_predictive_scaling_policy(policy, current_metrics)
        elif policy.policy_type == ScalingPolicy.SCHEDULED_SCALING:
            await self._evaluate_scheduled_scaling_policy(policy)

    async def _evaluate_target_tracking_policy(self,
                                             policy: AutoScalingPolicy,
                                             current_metrics: list[QuantumMetric]):
        """Evaluate target tracking scaling policy"""

        # Find the relevant metric
        relevant_metric = None
        for metric in current_metrics:
            if metric.metric_type == policy.metric_type:
                relevant_metric = metric
                break

        if not relevant_metric:
            return

        target = self.scaling_targets.get(policy.target_resource)
        if not target:
            return

        current_value = relevant_metric.value
        target_value = policy.target_value

        # Calculate scaling needed
        if current_value > target_value * 1.1:  # 10% buffer
            # Scale up
            scale_factor = current_value / target_value
            new_capacity = min(
                target.max_capacity,
                math.ceil(target.current_capacity * scale_factor)
            )

            if new_capacity > target.current_capacity:
                await self._execute_scaling_action(
                    policy, target, new_capacity, relevant_metric, ScalingDirection.UP
                )

        elif current_value < target_value * 0.9:  # 10% buffer
            # Scale down
            scale_factor = current_value / target_value
            new_capacity = max(
                target.min_capacity,
                math.floor(target.current_capacity * scale_factor)
            )

            if new_capacity < target.current_capacity:
                await self._execute_scaling_action(
                    policy, target, new_capacity, relevant_metric, ScalingDirection.DOWN
                )

    async def _evaluate_step_scaling_policy(self,
                                          policy: AutoScalingPolicy,
                                          current_metrics: list[QuantumMetric]):
        """Evaluate step scaling policy"""

        # For this example, assume we're scaling based on average wait time
        wait_time_metric = None
        for metric in current_metrics:
            if metric.metric_type == MetricType.AVERAGE_WAIT_TIME:
                wait_time_metric = metric
                break

        if not wait_time_metric:
            return

        target = self.scaling_targets.get(policy.target_resource)
        if not target:
            return

        current_wait_time = wait_time_metric.value

        # Find appropriate scaling step
        scaling_adjustment = 0
        for step in policy.scaling_steps:
            lower = step.get("lower_bound", 0)
            upper = step.get("upper_bound")

            if upper is None:
                if current_wait_time >= lower:
                    scaling_adjustment = step["scaling_adjustment"]
                    break
            else:
                if lower <= current_wait_time < upper:
                    scaling_adjustment = step["scaling_adjustment"]
                    break

        if scaling_adjustment != 0:
            new_capacity = target.current_capacity + scaling_adjustment
            new_capacity = max(target.min_capacity, min(target.max_capacity, new_capacity))

            if new_capacity != target.current_capacity:
                direction = ScalingDirection.UP if scaling_adjustment > 0 else ScalingDirection.DOWN
                await self._execute_scaling_action(
                    policy, target, new_capacity, wait_time_metric, direction
                )

    async def _evaluate_predictive_scaling_policy(self,
                                                policy: AutoScalingPolicy,
                                                current_metrics: list[QuantumMetric]):
        """Evaluate predictive scaling policy using ML"""

        # Get historical data for prediction
        history = await self._get_historical_metrics(
            MetricType.QUEUE_DEPTH,
            hours=24
        )

        if len(history) < 10:  # Need enough data
            return

        # Predict future queue depth
        predicted_queue_depth = await self._predict_metric_value(
            MetricType.QUEUE_DEPTH,
            history,
            prediction_horizon_minutes=policy.prediction_horizon_minutes
        )

        target = self.scaling_targets.get(policy.target_resource)
        if not target:
            return

        # Calculate optimal capacity for predicted load
        optimal_capacity = await self._calculate_optimal_capacity(
            predicted_queue_depth, target
        )

        if optimal_capacity != target.current_capacity:
            # Create synthetic metric for the prediction
            prediction_metric = QuantumMetric(
                metric_type=MetricType.QUEUE_DEPTH,
                value=predicted_queue_depth,
                timestamp=datetime.utcnow(),
                unit="jobs",
                source="predictive_model"
            )

            direction = ScalingDirection.UP if optimal_capacity > target.current_capacity else ScalingDirection.DOWN
            await self._execute_scaling_action(
                policy, target, optimal_capacity, prediction_metric, direction
            )

    async def _evaluate_scheduled_scaling_policy(self, policy: AutoScalingPolicy):
        """Evaluate scheduled scaling policy"""

        now = datetime.utcnow()
        current_time = now.strftime("%H:%M")
        current_weekday = now.weekday() + 1  # Monday = 1

        target = self.scaling_targets.get(policy.target_resource)
        if not target:
            return

        # Check schedule rules
        for rule in policy.schedule.get("rules", []):
            if (rule["time"] == current_time and
                current_weekday in rule["days"]):

                desired_capacity = rule["desired_capacity"]

                if desired_capacity != target.current_capacity:
                    # Create synthetic metric for scheduled scaling
                    schedule_metric = QuantumMetric(
                        metric_type=MetricType.QUEUE_DEPTH,
                        value=0,  # Not applicable for scheduled scaling
                        timestamp=now,
                        unit="schedule",
                        source="scheduled_policy"
                    )

                    direction = ScalingDirection.UP if desired_capacity > target.current_capacity else ScalingDirection.DOWN
                    await self._execute_scaling_action(
                        policy, target, desired_capacity, schedule_metric, direction
                    )
                break

    async def _execute_scaling_action(self,
                                    policy: AutoScalingPolicy,
                                    target: ScalingTarget,
                                    new_capacity: int,
                                    trigger_metric: QuantumMetric,
                                    direction: ScalingDirection):
        """Execute a scaling action"""

        action_id = f"scale-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}-{target.resource_type}"
        old_capacity = target.current_capacity

        try:
            # Execute the actual scaling (would call infrastructure APIs)
            success = await self._perform_scaling(
                target.resource_type, old_capacity, new_capacity
            )

            if success:
                # Update target capacity
                target.current_capacity = new_capacity
                target.desired_capacity = new_capacity

                print(f"Scaled {target.resource_type} from {old_capacity} to {new_capacity} ({direction.value})")

            # Record scaling action
            action = ScalingAction(
                action_id=action_id,
                policy_id=policy.policy_id,
                resource_type=target.resource_type,
                direction=direction,
                old_capacity=old_capacity,
                new_capacity=new_capacity,
                trigger_metric=trigger_metric,
                timestamp=datetime.utcnow(),
                success=success
            )

            self.scaling_actions.append(action)

        except Exception as e:
            # Record failed action
            action = ScalingAction(
                action_id=action_id,
                policy_id=policy.policy_id,
                resource_type=target.resource_type,
                direction=direction,
                old_capacity=old_capacity,
                new_capacity=new_capacity,
                trigger_metric=trigger_metric,
                timestamp=datetime.utcnow(),
                success=False,
                error_message=str(e)
            )

            self.scaling_actions.append(action)
            print(f"Failed to scale {target.resource_type}: {e}")

    async def _perform_scaling(self, resource_type: str, old_capacity: int, new_capacity: int) -> bool:
        """Perform the actual scaling operation"""

        # In a real implementation, this would call Kubernetes APIs,
        # AWS Auto Scaling APIs, or other infrastructure management systems

        print(f"Scaling {resource_type}: {old_capacity} -> {new_capacity}")

        if resource_type == "quantum_executors":
            # Scale quantum executor pods
            return await self._scale_quantum_executors(new_capacity)
        elif resource_type == "job_queue_workers":
            # Scale job queue worker processes
            return await self._scale_job_queue_workers(new_capacity)
        elif resource_type == "circuit_optimizers":
            # Scale circuit optimizer services
            return await self._scale_circuit_optimizers(new_capacity)

        return False

    async def _scale_quantum_executors(self, new_capacity: int) -> bool:
        """Scale quantum executor instances"""
        # Simulate scaling delay
        await asyncio.sleep(1)
        return True

    async def _scale_job_queue_workers(self, new_capacity: int) -> bool:
        """Scale job queue worker processes"""
        # Simulate scaling delay
        await asyncio.sleep(0.5)
        return True

    async def _scale_circuit_optimizers(self, new_capacity: int) -> bool:
        """Scale circuit optimizer services"""
        # Simulate scaling delay
        await asyncio.sleep(0.3)
        return True

    async def _is_in_cooldown(self, policy: AutoScalingPolicy) -> bool:
        """Check if policy is in cooldown period"""

        # Find last action for this policy
        last_action = None
        for action in reversed(self.scaling_actions):
            if action.policy_id == policy.policy_id and action.success:
                last_action = action
                break

        if not last_action:
            return False

        cooldown_end = last_action.timestamp + timedelta(seconds=policy.cooldown_period_seconds)
        return datetime.utcnow() < cooldown_end

    # Metric collection methods (simplified)
    async def _get_queue_depth(self) -> float:
        """Get current queue depth"""
        # Simulate queue depth (would query actual job queue)
        import random
        return random.uniform(5, 25)

    async def _get_average_wait_time(self) -> float:
        """Get average job wait time"""
        # Simulate wait time (would calculate from job history)
        import random
        return random.uniform(10, 120)

    async def _get_quantum_utilization(self) -> float:
        """Get quantum resource utilization percentage"""
        # Simulate utilization (would query quantum backends)
        import random
        return random.uniform(30, 95)

    async def _get_error_rate(self) -> float:
        """Get job error rate percentage"""
        # Simulate error rate (would calculate from job results)
        import random
        return random.uniform(1, 10)

    async def _get_throughput(self) -> float:
        """Get jobs completed per hour"""
        # Simulate throughput (would calculate from completed jobs)
        import random
        return random.uniform(50, 200)

    async def _get_historical_metrics(self, metric_type: MetricType, hours: int) -> list[float]:
        """Get historical metric values"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        values = []
        for metric in self.metrics_history:
            if (metric.metric_type == metric_type and
                metric.timestamp > cutoff_time):
                values.append(metric.value)

        return values

    async def _predict_metric_value(self,
                                  metric_type: MetricType,
                                  history: list[float],
                                  prediction_horizon_minutes: int) -> float:
        """Predict future metric value using simple ML"""

        if len(history) < 5:
            return statistics.mean(history) if history else 0

        # Simple linear trend prediction
        # In a real system, would use proper ML models
        recent_values = history[-10:]  # Last 10 values

        if len(recent_values) < 2:
            return recent_values[-1] if recent_values else 0

        # Calculate trend
        x = list(range(len(recent_values)))
        y = recent_values

        # Simple linear regression
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x_squared = sum(x[i] ** 2 for i in range(n))

        # Calculate slope and intercept
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x_squared - sum_x ** 2)
        intercept = (sum_y - slope * sum_x) / n

        # Predict future value
        future_x = len(recent_values) + (prediction_horizon_minutes / 5)  # Assuming 5-min intervals
        predicted_value = slope * future_x + intercept

        # Ensure reasonable bounds
        current_value = recent_values[-1]
        max_change = current_value * 0.5  # Max 50% change
        predicted_value = max(
            current_value - max_change,
            min(current_value + max_change, predicted_value)
        )

        return max(0, predicted_value)  # Ensure non-negative

    async def _calculate_optimal_capacity(self, predicted_load: float, target: ScalingTarget) -> int:
        """Calculate optimal capacity for predicted load"""

        # Simple heuristic: 1 executor per 5 queued jobs
        optimal = math.ceil(predicted_load / 5)

        # Apply bounds
        optimal = max(target.min_capacity, min(target.max_capacity, optimal))

        return optimal

    # API methods for external access
    async def get_scaling_policies(self) -> list[dict[str, Any]]:
        """Get all scaling policies"""

        policies = []
        for policy in self.scaling_policies.values():
            policy_dict = {
                "policy_id": policy.policy_id,
                "policy_name": policy.policy_name,
                "policy_type": policy.policy_type.value,
                "target_resource": policy.target_resource,
                "enabled": policy.enabled,
                "created_at": policy.created_at.isoformat() if policy.created_at else None
            }

            if policy.policy_type == ScalingPolicy.TARGET_TRACKING:
                policy_dict.update({
                    "target_value": policy.target_value,
                    "metric_type": policy.metric_type.value if policy.metric_type else None
                })
            elif policy.policy_type == ScalingPolicy.STEP_SCALING:
                policy_dict["scaling_steps"] = policy.scaling_steps
            elif policy.policy_type == ScalingPolicy.SCHEDULED_SCALING:
                policy_dict["schedule"] = policy.schedule

            policies.append(policy_dict)

        return policies

    async def get_scaling_targets(self) -> list[dict[str, Any]]:
        """Get all scaling targets"""

        targets = []
        for target in self.scaling_targets.values():
            targets.append({
                "resource_type": target.resource_type,
                "min_capacity": target.min_capacity,
                "max_capacity": target.max_capacity,
                "desired_capacity": target.desired_capacity,
                "current_capacity": target.current_capacity
            })

        return targets

    async def get_scaling_history(self, hours: int = 24) -> list[dict[str, Any]]:
        """Get scaling action history"""

        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        recent_actions = [
            action for action in self.scaling_actions
            if action.timestamp > cutoff_time
        ]

        history = []
        for action in recent_actions:
            history.append({
                "action_id": action.action_id,
                "policy_id": action.policy_id,
                "resource_type": action.resource_type,
                "direction": action.direction.value,
                "old_capacity": action.old_capacity,
                "new_capacity": action.new_capacity,
                "trigger_metric": {
                    "type": action.trigger_metric.metric_type.value,
                    "value": action.trigger_metric.value,
                    "unit": action.trigger_metric.unit
                },
                "timestamp": action.timestamp.isoformat(),
                "success": action.success,
                "error_message": action.error_message
            })

        return history

# Example usage
if __name__ == "__main__":
    async def main():
        # Initialize auto-scaler
        autoscaler = QuantumAutoScaler()

        # Start monitoring
        await autoscaler.start_monitoring()

        print("Quantum Auto-Scaler started. Monitoring for 60 seconds...")

        # Let it run for a minute
        await asyncio.sleep(60)

        # Get current status
        targets = await autoscaler.get_scaling_targets()
        print("\nCurrent Scaling Targets:")
        for target in targets:
            print(f"  {target['resource_type']}: {target['current_capacity']} (min: {target['min_capacity']}, max: {target['max_capacity']})")

        # Get scaling history
        history = await autoscaler.get_scaling_history(hours=1)
        print(f"\nScaling Actions (last hour): {len(history)}")
        for action in history[-5:]:  # Show last 5 actions
            print(f"  {action['timestamp']}: {action['resource_type']} {action['direction']} {action['old_capacity']}->{action['new_capacity']}")

        # Stop monitoring
        await autoscaler.stop_monitoring()

    asyncio.run(main())
