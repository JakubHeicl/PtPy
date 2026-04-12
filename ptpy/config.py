from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parent

INPUT_FOLDER: Path = Path("input_files")
REPOSITORY_FOLDER: Path = Path("repository")
METADATA_FILE: Path = Path("metadata.json")
RUN_FOLDER: Path = Path("runs")
BASES_FOLDER: Path = Path(PACKAGE_ROOT, "bases")

LANL_EXTENSION = "lanl"
DZ_EXTENSION = "dz" 

AIM_CLUSTER = "heiclj@jupiter.karlov.mff.cuni.cz"
AIM_FOLDER = "/Volumes/Home_2/Users_Ju/heiclj/ptpy_aim_calc"

SCHEDULER = "slurm" # Options: "slurm", "local", "pbs"
PARTITION = "q_kchfo"
NUMBER_OF_CORES_GAUSSAIN = 16
MEMORY = 4000 # in MB   

NUMBER_OF_CORES_AIM = 4

USER = "heiclj"
