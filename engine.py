from pathlib import Path

from config import (
    CALCULATION_SEQUENCE,
    DEFAULT_MEMORY,
    DEFAULT_NPROCS,
    FOOTER_BY_TYPE,
    INPUT_FOLDER,
    REPOSITORY_FOLDER,
    ROUTE_BY_TYPE,
    RUN_FOLDER,
    STEP_CHK_FILENAME,
    STEP_INPUT_FILENAME,
    STEP_LOG_FILENAME,
)
from ir import CalculationStep, CalculationType, Status, WorkflowCase
from repository import Repository
from scheduler import Scheduler
from utils import (
    extract_com_data,
    extract_final_geometry_from_gaussian_log,
    extract_geometry_from_xyz,
    find_case_input,
    gaussian_finished_ok,
    get_charge_and_mult_from_com,
    write_gaussian_input,
)


def add_to_repository_from_input_folder(repo: Repository, input_folder: Path):
    for input_file in input_folder.glob("*.xyz"):
        existing_case = repo.get_case_by_name(input_file.stem)
        if existing_case is not None:
            if existing_case.source_input is None:
                existing_case.source_input = input_file
            continue

        charge = int(input(f"Enter charge for {input_file.name}: "))
        mult = int(input(f"Enter multiplicity for {input_file.name}: "))
        repo.add_case(_build_case(input_file, charge, mult))

    for input_file in input_folder.glob("*.com"):
        existing_case = repo.get_case_by_name(input_file.stem)
        if existing_case is not None:
            existing_case.source_input = input_file
            continue

        charge, mult = get_charge_and_mult_from_com(input_file)
        repo.add_case(_build_case(input_file, charge, mult))


def run_engine_once(repo: Repository) -> bool:
    scheduler = Scheduler()
    changed = False

    for case in repo.cases:
        changed = process_case(case, scheduler) or changed

    return changed


def process_case(case: WorkflowCase, scheduler: Scheduler) -> bool:
    step = case.current_step()
    if step is None:
        return False

    if step.status == Status.COMPLETED:
        next_step = case.advance()
        if next_step is None:
            return False
        if next_step.status == Status.PENDING:
            return _prepare_and_submit_step(case, next_step, scheduler)
        return process_case(case, scheduler)

    if step.status == Status.PENDING:
        return _prepare_and_submit_step(case, step, scheduler)

    if step.status == Status.RUNNING:
        if scheduler.is_running(step.job_id):
            return False

        log_file = _step_log_file(step)
        if gaussian_finished_ok(log_file):
            step.status = Status.COMPLETED
            next_step = case.advance()
            if next_step is None:
                return True
            _prepare_and_submit_step(case, next_step, scheduler)
            return True

        if log_file.exists():
            step.status = Status.FAILED
            return True

    return False


def _prepare_and_submit_step(case: WorkflowCase, step: CalculationStep, scheduler: Scheduler) -> bool:
    if step.folder is None:
        raise ValueError(f"Workflow step {step.calculation_type.value} is missing a folder.")

    step.folder.mkdir(parents=True, exist_ok=True)
    input_file = _step_input_file(step)

    if step.calculation_type == CalculationType.LANL_OPT:
        _write_lanl_input(case, input_file)
    elif step.calculation_type == CalculationType.DZ_OPT:
        _write_dz_input(case, input_file)
    else:
        raise ValueError(f"Unsupported calculation type '{step.calculation_type.value}'.")

    step.job_id = scheduler.submit(case, step, input_file)
    step.status = Status.RUNNING
    return True


def _write_lanl_input(case: WorkflowCase, output_file: Path) -> None:
    source_input = case.source_input or find_case_input(case.name, INPUT_FOLDER)
    if source_input is None:
        raise FileNotFoundError(f"Could not find source input for case '{case.name}'.")

    case.source_input = source_input
    if source_input.suffix.lower() == ".xyz":
        geometry_lines = extract_geometry_from_xyz(source_input)
        charge = case.charge
        mult = case.multiplicity
    elif source_input.suffix.lower() == ".com":
        charge, mult, geometry_lines = extract_com_data(source_input)
    else:
        raise ValueError(f"Unsupported input format '{source_input.suffix}' for {source_input}.")

    write_gaussian_input(
        output_file,
        charge=charge,
        mult=mult,
        route_section=ROUTE_BY_TYPE[CalculationType.LANL_OPT],
        geometry_lines=geometry_lines,
        title=f"{case.name} {CalculationType.LANL_OPT.value}",
        chk_name=STEP_CHK_FILENAME,
        memory=DEFAULT_MEMORY,
        nproc=DEFAULT_NPROCS,
        footer=FOOTER_BY_TYPE[CalculationType.LANL_OPT],
    )


def _write_dz_input(case: WorkflowCase, output_file: Path) -> None:
    previous_step = case.previous_step()
    if previous_step is None:
        raise ValueError(f"Case '{case.name}' does not have a previous step for DZ input generation.")
    if previous_step.status != Status.COMPLETED:
        raise ValueError(f"Previous step for case '{case.name}' is not completed yet.")

    geometry_lines = extract_final_geometry_from_gaussian_log(_step_log_file(previous_step))
    write_gaussian_input(
        output_file,
        charge=case.charge,
        mult=case.multiplicity,
        route_section=ROUTE_BY_TYPE[CalculationType.DZ_OPT],
        geometry_lines=geometry_lines,
        title=f"{case.name} {CalculationType.DZ_OPT.value}",
        chk_name=STEP_CHK_FILENAME,
        memory=DEFAULT_MEMORY,
        nproc=DEFAULT_NPROCS,
        footer=FOOTER_BY_TYPE[CalculationType.DZ_OPT],
    )


def _build_case(source_input: Path, charge: int, mult: int) -> WorkflowCase:
    directory = RUN_FOLDER / source_input.stem
    directory.mkdir(parents=True, exist_ok=True)

    return WorkflowCase(
        name=source_input.stem,
        directory=directory,
        charge=charge,
        multiplicity=mult,
        source_input=source_input,
        steps=[
            CalculationStep(
                calculation_type=calc_type,
                folder=directory / calc_type.value,
            )
            for calc_type in CALCULATION_SEQUENCE
        ],
    )


def _step_input_file(step: CalculationStep) -> Path:
    if step.folder is None:
        raise ValueError("Calculation step folder is not set.")
    return step.folder / STEP_INPUT_FILENAME


def _step_log_file(step: CalculationStep) -> Path:
    if step.folder is None:
        raise ValueError("Calculation step folder is not set.")
    return step.folder / STEP_LOG_FILENAME


if __name__ == "__main__":
    INPUT_FOLDER.mkdir(parents=True, exist_ok=True)
    REPOSITORY_FOLDER.mkdir(parents=True, exist_ok=True)
    RUN_FOLDER.mkdir(parents=True, exist_ok=True)

    repo = Repository()
    repo.load_from_folder(REPOSITORY_FOLDER)
    add_to_repository_from_input_folder(repo, INPUT_FOLDER)
    run_engine_once(repo)
    repo.save_to_folder(REPOSITORY_FOLDER)
