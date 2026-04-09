from pathlib import Path


_SYMBOLS = {
    "X",
    "H", "He",
    "Li", "Be", "B", "C", "N", "O", "F", "Ne",
    "Na", "Mg", "Al", "Si", "P", "S", "Cl", "Ar",
    "K", "Ca", "Sc", "Ti", "V", "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn",
    "Ga", "Ge", "As", "Se", "Br", "Kr",
    "Rb", "Sr", "Y", "Zr", "Nb", "Mo", "Tc", "Ru", "Rh", "Pd", "Ag", "Cd",
    "In", "Sn", "Sb", "Te", "I", "Xe",
    "Cs", "Ba", "La", "Ce", "Pr", "Nd", "Pm", "Sm", "Eu", "Gd", "Tb", "Dy", "Ho", "Er", "Tm", "Yb", "Lu",
    "Hf", "Ta", "W", "Re", "Os", "Ir", "Pt", "Au", "Hg",
    "Tl", "Pb", "Bi", "Po", "At", "Rn",
    "Fr", "Ra", "Ac", "Th", "Pa", "U", "Np", "Pu", "Am", "Cm", "Bk", "Cf", "Es", "Fm", "Md", "No", "Lr",
    "Rf", "Db", "Sg", "Bh", "Hs", "Mt", "Ds", "Rg", "Cn",
    "Nh", "Fl", "Mc", "Lv", "Ts", "Og",
}

_SYMBOLS_BY_ATOMIC_NUMBER = [
    "X",
    "H", "He",
    "Li", "Be", "B", "C", "N", "O", "F", "Ne",
    "Na", "Mg", "Al", "Si", "P", "S", "Cl", "Ar",
    "K", "Ca", "Sc", "Ti", "V", "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn",
    "Ga", "Ge", "As", "Se", "Br", "Kr",
    "Rb", "Sr", "Y", "Zr", "Nb", "Mo", "Tc", "Ru", "Rh", "Pd", "Ag", "Cd",
    "In", "Sn", "Sb", "Te", "I", "Xe",
    "Cs", "Ba", "La", "Ce", "Pr", "Nd", "Pm", "Sm", "Eu", "Gd", "Tb", "Dy", "Ho", "Er", "Tm", "Yb", "Lu",
    "Hf", "Ta", "W", "Re", "Os", "Ir", "Pt", "Au", "Hg",
    "Tl", "Pb", "Bi", "Po", "At", "Rn",
    "Fr", "Ra", "Ac", "Th", "Pa", "U", "Np", "Pu", "Am", "Cm", "Bk", "Cf", "Es", "Fm", "Md", "No", "Lr",
    "Rf", "Db", "Sg", "Bh", "Hs", "Mt", "Ds", "Rg", "Cn",
    "Nh", "Fl", "Mc", "Lv", "Ts", "Og",
]


def xyz_to_lanl(input_file, output_file, charge, mult):
    input_path = Path(input_file)
    output_path = Path(output_file)
    geometry_lines = extract_geometry_from_xyz(input_path)
    write_gaussian_input(
        output_path,
        charge=int(charge),
        mult=int(mult),
        route_section="#p opt hf lanl1mb",
        geometry_lines=geometry_lines,
    )


def com_to_lanl(input_file, output_file):
    input_path = Path(input_file)
    output_path = Path(output_file)
    charge, mult, geometry_lines = extract_com_data(input_path)
    write_gaussian_input(
        output_path,
        charge=charge,
        mult=mult,
        route_section="#p opt hf lanl1mb",
        geometry_lines=geometry_lines,
    )
    return charge, mult


def get_charge_and_mult_from_com(input_file):
    charge, mult, _ = extract_com_data(Path(input_file))
    return charge, mult


def find_case_input(case_name: str, input_folder: Path) -> Path | None:
    com_path = input_folder / f"{case_name}.com"
    if com_path.exists():
        return com_path

    xyz_path = input_folder / f"{case_name}.xyz"
    if xyz_path.exists():
        return xyz_path

    return None


def extract_geometry_from_xyz(input_file: Path) -> list[str]:
    lines = input_file.read_text(encoding="utf-8").splitlines()
    return [f"{line}\n" for line in lines[2:] if line.strip()]


def extract_com_data(input_file: Path) -> tuple[int, int, list[str]]:
    lines = input_file.read_text(encoding="utf-8").splitlines()
    geometry_start = _find_geometry_start(lines)

    charge_line_parts = lines[geometry_start - 1].strip().split()
    if len(charge_line_parts) < 2:
        raise ValueError(f"Missing charge/multiplicity line in {input_file}.")

    charge = int(charge_line_parts[0])
    mult = int(charge_line_parts[1])

    geometry_lines: list[str] = []
    for line in lines[geometry_start:]:
        if _is_geometry_line(line):
            geometry_lines.append(f"{line}\n")
            continue
        break

    return charge, mult, geometry_lines


def write_gaussian_input(
    output_file: Path,
    charge: int,
    mult: int,
    route_section: str,
    geometry_lines: list[str],
    title: str = "job description",
    chk_name: str | None = None,
    memory: str = "2GB",
    nproc: int = 4,
    footer: str = "",
) -> None:
    sections = [
        f"%mem={memory}",
        f"%nprocshared={nproc}",
    ]
    if chk_name:
        sections.append(f"%chk={chk_name}")
    sections.append(route_section)
    sections.append("")
    sections.append(title)
    sections.append("")
    sections.append(f"{charge} {mult}")

    body = "\n".join(sections) + "\n"
    body += "".join(geometry_lines)
    body += "\n"
    if footer.strip():
        body += footer.rstrip() + "\n"
    body += "\n"
    output_file.write_text(body, encoding="utf-8")


def _find_geometry_start(lines: list[str]) -> int:
    for index, line in enumerate(lines):
        if _is_geometry_line(line):
            return index
    raise ValueError("Could not find geometry block in Gaussian input.")


def _is_geometry_line(line: str) -> bool:
    parts = line.strip().split()
    return len(parts) > 1 and parts[0].capitalize() in _SYMBOLS


def gaussian_finished_ok(log_file: Path) -> bool:
    if not log_file.exists():
        return False
    text = log_file.read_text(encoding="utf-8", errors="ignore")
    return "Normal termination of Gaussian" in text


def extract_final_geometry_from_gaussian_log(log_file: Path) -> list[str]:
    if not log_file.exists():
        raise FileNotFoundError(log_file)

    lines = log_file.read_text(encoding="utf-8", errors="ignore").splitlines()
    last_geometry: list[str] | None = None

    for index, line in enumerate(lines):
        if "Standard orientation:" not in line and "Input orientation:" not in line:
            continue

        geometry_block: list[str] = []
        geometry_start = _find_geometry_table_start(lines, index)
        for geometry_line in lines[geometry_start:]:
            stripped = geometry_line.strip()
            if stripped.startswith("-----"):
                break

            parts = geometry_line.split()
            if len(parts) < 6:
                continue

            atomic_number = int(parts[1])
            symbol = _atomic_number_to_symbol(atomic_number)
            x_coord, y_coord, z_coord = parts[3], parts[4], parts[5]
            geometry_block.append(f"{symbol:<2} {x_coord:>16} {y_coord:>16} {z_coord:>16}\n")

        if geometry_block:
            last_geometry = geometry_block

    if last_geometry is None:
        raise ValueError(f"Could not find final geometry in Gaussian log {log_file}.")

    return last_geometry


def _find_geometry_table_start(lines: list[str], orientation_index: int) -> int:
    dashed_lines_seen = 0

    for index in range(orientation_index + 1, len(lines)):
        if lines[index].strip().startswith("-----"):
            dashed_lines_seen += 1
            if dashed_lines_seen == 2:
                return index + 1

    raise ValueError("Could not locate geometry table in Gaussian log.")


def _atomic_number_to_symbol(atomic_number: int) -> str:
    if atomic_number <= 0 or atomic_number >= len(_SYMBOLS_BY_ATOMIC_NUMBER):
        raise ValueError(f"Unsupported atomic number {atomic_number}.")
    return _SYMBOLS_BY_ATOMIC_NUMBER[atomic_number]
