from pathlib import Path

from ir import CalculationType

INPUT_FOLDER: Path = Path("input_files")
REPOSITORY_FOLDER: Path = Path("repository")
RUN_FOLDER: Path = Path("runs")

STEP_INPUT_FILENAME = "input.com"
STEP_LOG_FILENAME = "job.log"
STEP_CHK_FILENAME = "job.chk"
STEP_SUBMIT_FILENAME = "submit.sh"

DEFAULT_MEMORY = "2GB"
DEFAULT_NPROCS = 4
JOB_DESCRIPTION = "job description"

LANL_ROUTE_SECTION = "#p opt hf lanl1mb"
DZ_ROUTE_SECTION = "#p opt hf"
LANL_FOOTER = ""
DZ_FOOTER = ""

CALCULATION_SEQUENCE = [
    CalculationType.LANL_OPT,
    CalculationType.DZ_OPT,
]

ROUTE_BY_TYPE = {
    CalculationType.LANL_OPT: LANL_ROUTE_SECTION,
    CalculationType.DZ_OPT: DZ_ROUTE_SECTION,
}

FOOTER_BY_TYPE = {
    CalculationType.LANL_OPT: LANL_FOOTER,
    CalculationType.DZ_OPT: DZ_FOOTER,
}

SCHEDULER_MODE = "slurm"
GAUSSIAN_EXECUTABLE = "g16"
JOB_NAME_PREFIX = "ptwf"

SLURM_SUBMIT_COMMAND = "sbatch"
SLURM_STATUS_COMMAND = "squeue"
SLURM_JOB_ID_PATTERN = r"(?:Submitted batch job\s+)?(\d+)"
SLURM_CPUS = 4
SLURM_MEMORY = "4G"
SLURM_TIME = "24:00:00"
SLURM_PARTITION: str | None = None
