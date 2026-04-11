from ir import WorkflowCase
from enum import Enum

class TerminationStatus(Enum):
    SUCCESS = "success"
    FAILURE = "failure"

def get_log_termination_status(case: WorkflowCase) -> TerminationStatus:
    
    current_step = case.get_current_step()

    log_file = current_step.log_file

    if log_file is None or not log_file.exists():
        raise RuntimeError(f"Log file for case {case.name} does not exist. Cannot determine termination status.")
    
    with open(log_file, "r") as f:
        lines = f.readlines()
        if not lines:
            raise RuntimeError(f"Log file for case {case.name} is empty. Cannot determine termination status.")
        
        for line in reversed(lines):
            line = line.strip()
            if not line:
                continue
            if "Normal termination" in line:
                return TerminationStatus.SUCCESS
            elif "Error termination" in line:
                return TerminationStatus.FAILURE
    raise RuntimeError(f"Could not determine termination status for case {case.name}. Please check the log file for details.")