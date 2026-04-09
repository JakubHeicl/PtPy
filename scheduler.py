from __future__ import annotations

import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

from config import (
    GAUSSIAN_EXECUTABLE,
    JOB_NAME_PREFIX,
    SCHEDULER_MODE,
    SLURM_CPUS,
    SLURM_JOB_ID_PATTERN,
    SLURM_MEMORY,
    SLURM_PARTITION,
    SLURM_STATUS_COMMAND,
    SLURM_SUBMIT_COMMAND,
    SLURM_TIME,
    STEP_LOG_FILENAME,
    STEP_SUBMIT_FILENAME,
)
from ir import CalculationStep, WorkflowCase


@dataclass
class Scheduler:
    mode: str = SCHEDULER_MODE

    def submit(self, case: WorkflowCase, step: CalculationStep, input_file: Path) -> str:
        if step.folder is None:
            raise ValueError("Calculation step folder is not set.")

        step.folder.mkdir(parents=True, exist_ok=True)

        if self.mode == "slurm":
            return self._submit_slurm(case, step, input_file)
        if self.mode == "local":
            return self._submit_local(step, input_file)

        raise ValueError(f"Unsupported scheduler mode '{self.mode}'.")

    def is_running(self, job_id: str | None) -> bool:
        if not job_id:
            return False

        if self.mode == "slurm":
            return self._is_running_slurm(job_id)
        if self.mode == "local":
            return self._is_running_local(job_id)

        raise ValueError(f"Unsupported scheduler mode '{self.mode}'.")

    def _submit_slurm(self, case: WorkflowCase, step: CalculationStep, input_file: Path) -> str:
        submit_script = self._write_slurm_submit_script(case, step, input_file)
        try:
            result = subprocess.run(
                [SLURM_SUBMIT_COMMAND, submit_script.name],
                cwd=step.folder,
                capture_output=True,
                text=True,
                check=True,
            )
        except FileNotFoundError as error:
            raise RuntimeError(
                f"Slurm submit command '{SLURM_SUBMIT_COMMAND}' was not found. "
                "Update config.py or run the workflow on a machine with Slurm available."
            ) from error
        return self._extract_job_id(result.stdout.strip())

    def _submit_local(self, step: CalculationStep, input_file: Path) -> str:
        log_file = step.folder / STEP_LOG_FILENAME
        with open(log_file, "w", encoding="utf-8") as log_handle:
            try:
                process = subprocess.Popen(
                    [GAUSSIAN_EXECUTABLE, input_file.name],
                    cwd=step.folder,
                    stdout=log_handle,
                    stderr=subprocess.STDOUT,
                )
            except FileNotFoundError as error:
                raise RuntimeError(
                    f"Gaussian executable '{GAUSSIAN_EXECUTABLE}' was not found. "
                    "Update config.py with the correct executable path."
                ) from error
        return str(process.pid)

    def _is_running_slurm(self, job_id: str) -> bool:
        try:
            result = subprocess.run(
                [SLURM_STATUS_COMMAND, "-h", "-j", job_id, "-o", "%T"],
                capture_output=True,
                text=True,
                check=False,
            )
        except FileNotFoundError as error:
            raise RuntimeError(
                f"Slurm status command '{SLURM_STATUS_COMMAND}' was not found. "
                "Update config.py or run the workflow on a machine with Slurm available."
            ) from error
        return bool(result.stdout.strip())

    def _is_running_local(self, job_id: str) -> bool:
        if os.name == "nt":
            result = subprocess.run(
                ["tasklist", "/FI", f"PID eq {job_id}", "/FO", "CSV", "/NH"],
                capture_output=True,
                text=True,
                check=False,
            )
            output = result.stdout.strip()
            return bool(output) and "No tasks are running" not in output

        try:
            os.kill(int(job_id), 0)
            return True
        except OSError:
            return False

    def _write_slurm_submit_script(self, case: WorkflowCase, step: CalculationStep, input_file: Path) -> Path:
        submit_script = step.folder / STEP_SUBMIT_FILENAME
        lines = [
            "#!/bin/bash",
            f"#SBATCH --job-name={JOB_NAME_PREFIX}-{case.name}-{step.calculation_type.value}",
            f"#SBATCH --cpus-per-task={SLURM_CPUS}",
            f"#SBATCH --mem={SLURM_MEMORY}",
            f"#SBATCH --time={SLURM_TIME}",
        ]

        if SLURM_PARTITION:
            lines.append(f"#SBATCH --partition={SLURM_PARTITION}")

        lines.extend(
            [
                "",
                f'{GAUSSIAN_EXECUTABLE} "{input_file.name}" > "{STEP_LOG_FILENAME}" 2>&1',
                "",
            ]
        )
        submit_script.write_text("\n".join(lines), encoding="utf-8")
        return submit_script

    def _extract_job_id(self, submit_stdout: str) -> str:
        match = re.search(SLURM_JOB_ID_PATTERN, submit_stdout)
        if match is None:
            raise ValueError(f"Could not parse scheduler job id from '{submit_stdout}'.")
        return match.group(1)
