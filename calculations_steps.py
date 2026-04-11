from ir import StepStatus, WorkflowCase, CalculationType
from scheduler import Scheduler
from utils import xyz_to_lanl, com_to_lanl
from pathlib import Path
from config import LANL_EXTENSION, DZ_EXTENSION

def run_lanl_optimization(case: WorkflowCase, scheduler: Scheduler):
    current_step = case.get_current_step()
    folder = current_step.folder
    input_file = case.input_file

    if current_step.calculation_type != CalculationType.LANL_OPT:
        raise ValueError(f"Expected OPTIMIZATION step, got {current_step.calculation_type}.")
    
    name = f"{case.name}_{LANL_EXTENSION}"

    folder.mkdir(parents=True, exist_ok=True)
    lanl_input_file = Path(folder, name).with_suffix(".com")
    lanl_output_file = Path(folder, name).with_suffix(".log")

    if input_file.suffix == ".xyz":
        xyz_to_lanl(input_file, lanl_input_file, case.charge, case.multiplicity)

    elif input_file.suffix == ".com":
        com_to_lanl(input_file, lanl_input_file)
    else:
        raise ValueError(f"Unsupported input file format: {input_file.suffix}")
    
    job_id = scheduler.submit_job(folder, lanl_input_file)

    current_step.job_id = job_id
    current_step.input_file = lanl_input_file
    current_step.log_file = lanl_output_file
    current_step.status = StepStatus.RUNNING
    print(f"Submitted LANL optimization for case {case.name} with job ID {job_id}.")

def run_dz_optimization(case: WorkflowCase, scheduler: Scheduler):

    current_step = case.get_current_step()
    lanl_log_file = current_step.log_file

    if lanl_log_file is None or not lanl_log_file.exists():
        raise RuntimeError(f"LANL log file for case {case.name} does not exist. Cannot run DZ optimization.")
    
    if current_step.calculation_type != CalculationType.DZ_OPT:
        raise ValueError(f"Expected DZ_OPT step, got {current_step.calculation_type}.")
    
    name = f"{case.name}_{DZ_EXTENSION}"

    

    

    

    