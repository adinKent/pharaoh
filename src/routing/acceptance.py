from dataclasses import dataclass

from routing.models import Capability, ExecutionPlan, Freshness


@dataclass(frozen=True)
class AcceptanceReport:
    total: int
    passed: int

    @property
    def accuracy(self) -> float:
        return self.passed / self.total if self.total else 0.0


def evaluate_routes(expected: list[tuple[tuple[Capability, ...], Freshness]], actual: list[ExecutionPlan]) -> AcceptanceReport:
    if len(expected) != len(actual):
        raise ValueError("Expected and actual route counts must match")
    passed = sum(
        1
        for (expected_capabilities, expected_freshness), plan in zip(expected, actual)
        if tuple(plan.capabilities) == expected_capabilities and plan.freshness == expected_freshness
    )
    return AcceptanceReport(total=len(expected), passed=passed)


def assert_acceptance_threshold(report: AcceptanceReport, threshold: float = 0.95) -> None:
    if report.accuracy < threshold:
        raise AssertionError(f"Routing accuracy {report.accuracy:.1%} is below {threshold:.1%}")
