from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum


class CalculationType(Enum):
    INITIALIZED = "initialized"
    LANL_OPT = "lanl_opt"
    DZ_OPT = "dz_opt"


class Status(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class CalculationStep:
    calculation_type: CalculationType = CalculationType.INITIALIZED
    status: Status = Status.PENDING
    job_id: str | None = None
    folder: Path | None = None

    def to_json(self) -> dict:
        return {
            "calculation_type": self.calculation_type.value,
            "status": self.status.value,
            "job_id": self.job_id,
            "folder": str(self.folder) if self.folder is not None else None,
        }

    @classmethod
    def from_json(cls, data: dict) -> "CalculationStep":
        folder = data.get("folder")
        return cls(
            calculation_type=CalculationType(data["calculation_type"]),
            status=Status(data["status"]),
            job_id=data.get("job_id"),
            folder=Path(folder) if folder is not None else None,
        )


@dataclass
class WorkflowCase:
    name: str
    directory: Path
    charge: int
    multiplicity: int
    source_input: Path | None = None
    steps: list[CalculationStep] = field(default_factory=list)
    current_step_index: int = 0

    def current_step(self) -> CalculationStep | None:
        if not self.steps:
            return None
        if self.current_step_index < 0 or self.current_step_index >= len(self.steps):
            return None
        return self.steps[self.current_step_index]

    def previous_step(self) -> CalculationStep | None:
        if self.current_step_index <= 0:
            return None
        return self.steps[self.current_step_index - 1]

    def next_step(self) -> CalculationStep | None:
        next_index = self.current_step_index + 1
        if next_index >= len(self.steps):
            return None
        return self.steps[next_index]

    def advance(self) -> CalculationStep | None:
        if self.current_step_index + 1 >= len(self.steps):
            return None
        self.current_step_index += 1
        return self.current_step()

    def to_json(self) -> dict:
        return {
            "name": self.name,
            "directory": str(self.directory),
            "charge": self.charge,
            "multiplicity": self.multiplicity,
            "source_input": str(self.source_input) if self.source_input is not None else None,
            "steps": [step.to_json() for step in self.steps],
            "current_step_index": self.current_step_index,
        }

    @classmethod
    def from_json(cls, data: dict) -> "WorkflowCase":
        return cls(
            name=data["name"],
            directory=Path(data["directory"]),
            charge=int(data["charge"]),
            multiplicity=int(data["multiplicity"]),
            source_input=Path(data["source_input"]) if data.get("source_input") else None,
            steps=[CalculationStep.from_json(step_data) for step_data in data.get("steps", [])],
            current_step_index=data.get("current_step_index", 0),
        )
