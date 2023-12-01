from __future__ import annotations

import os
import abc
import math
import enum
import typing
import dataclasses
import pandas as pd
import matplotlib.pyplot as plt


@dataclasses.dataclass
class CMakeConfiguration:
    build_configuration: str
    build_type: typing.Literal["Debug", "Release"]
    toolchain_file: typing.Final[os.PathLike] \
        = "/home/ubuntu/vcpkg/scripts/buildsystems/vcpkg.cmake"
    build_directory_base_name: typing.Final[str] = "build"
    source_directory: typing.Final[os.PathLike] = "/tmp/Spiral"
    use_log: typing.Literal["ON", "OFF"] = "ON"
    use_timer_log: typing.Literal["ON", "OFF"] = "ON"
    use_native_log: typing.Literal["ON", "OFF"] = "OFF"

    @property
    def build_path(self) -> str:
        return os.fspath(
            f"{self.source_directory}/{self.build_directory_base_name}_{self.build_configuration}"
        )

    def __str__(self) -> str:
        return (
            f"cmake "
            f"-DCMAKE_BUILD_TYPE={self.build_type} "
            f"-DCMAKE_TOOLCHAIN_FILE={self.toolchain_file} "
            f"-DUSE_TIMERLOG={self.use_timer_log} "
            f"-DUSE_NATIVELOG={self.use_native_log} "
            f"-DUSE_LOG={self.use_log} "
            f"-S {self.source_directory} "
            f"-B {self.build_path}"
        )


@dataclasses.dataclass
class CMakeBuild:
    parameter_set: str
    build_path: str
    target: typing.Literal["Seperated", "Server", "Client"]
    core_count: int = 4
    verbose: bool = True

    def __str__(self) -> str:
        return (
            f"cmake "
            f"--build {self.build_path} "
            f"--target {self.target} "
            + (f"-v " if self.verbose else "") +
            f"-j{self.core_count} "
            f"-- PARAMSET=PARAMS_DYNAMIC {self.parameter_set}"
        )


@dataclasses.dataclass
class CMakeRun:
    cmake_configuration: CMakeConfiguration
    cmake_build: CMakeBuild
    executable: typing.Literal["Seperated", "Server", "Client"]
    database_file: str
    further_dimensions: int
    folding_factor: int

    @property
    def build_path(self) -> str:
        return self.cmake_build.build_path

    def executable_path(self) -> str:
        target_project_map = {
            "Seperated": "Seperated",
            "Server": "PIR_Server",
            "Client": "Client"
        }
        return os.fspath(
            f"{self.build_path}/{target_project_map[self.executable]}/{self.executable}"
        )

    def generate_command(self) -> str:
        return (
            f"{self.cmake_configuration} && "
            f"{self.cmake_build} && "
            f"{self.executable_path()} "
            f"{self.further_dimensions} {self.folding_factor} "
            f"{self.database_file}"
        )

    def run(self) -> None:
        os.system(self.generate_command())


class Evaluation:

    def __init__(self) -> None:
        metric_file_to_table_map: dict[str, typing.Type[EvaluationTable]] = {
            "Query_Generation.client": QueryGenerationTable,
            "Extract_Response.client": ResponseExtractionTable,
            "Rate.client": RateTable,
            "Database_Generation.server": DatabaseGenerationTable,
            "Answer.server": AnswerTable,
            "Query_Cost.communication": QueryCostTable,
            "Response_Cost.communication": ResponseCostTable,
            "Total_Cost.communication": TotalCostTable,
        }
        _evaluation_table_map: dict[str, EvaluationTable] = dict()
        for metric_file, table_type in metric_file_to_table_map.items():
            assert metric_file in metric_file_to_table_map, \
                f"{metric_file} not in table map."
            _evaluation_table_map[metric_file] = table_type()
        self.evaluation_table_map = _evaluation_table_map
        self.data_path: str = os.fspath("./Data")


class TableSection(str, enum.Enum):
    SERVER = "I: Server"
    CLIENT = "II: Client"
    COMMUNICATION_COST = "III: Communication Cost"


@dataclasses.dataclass
class EvaluationTable(abc.ABC):
    data: list[list[str]] = dataclasses.field(default_factory=list)
    column_labels: typing.Final[list[str]] \
        = dataclasses.field(
        default_factory=lambda: [
            f"2^{{{database_size}}}"
            for database_size in range(10, 31, 2)
        ]
    )
    row_labels: typing.Final[list[str]] \
        = dataclasses.field(
        default_factory=lambda: [
            str(q)
            for q in [2, 16, 128, 256]
        ]
    )

    @property
    def label(self) -> str:
        return f"tab:{self.title.lower().replace(' ', '_')}"

    @property
    @abc.abstractmethod
    def section(self) -> TableSection:
        pass

    @property
    @abc.abstractmethod
    def title(self) -> str:
        pass

    @property
    @abc.abstractmethod
    def unit(self) -> str:
        pass

    def __str__(self) -> str:
        df = self.retrieve_padded_dataframe()
        return df.to_latex(caption=f"{self.title} ({self.unit})", label=self.label)

    def _retrieve_data_column_map(self) -> dict[str, list[str]]:
        column_map = dict()
        for column_index, column_label in enumerate(self.column_labels):
            column_map[column_label] = self.data[column_index].copy() \
                if column_index < len(self.data) else []
        return column_map

    def _pad_rows(self, out_data: dict[str, list[str]]) -> dict[str, list[str]]:
        for column_name, column in out_data.items():
            # Lengthen the columns to be of row size.
            out_data[column_name].extend(["0"] * (len(self.row_labels) - len(column)))
        return out_data

    def retrieve_padded_dataframe(self) -> pd.DataFrame:
        df_data = self._retrieve_data_column_map()
        self._pad_rows(df_data)
        return pd.DataFrame(df_data, index=self.row_labels)

    def write_latex_table(self) -> None:
        with open(f"./Latex_Tables/{self.title.replace(' ', '_')}.tex", "w") as file:
            file.write(str(self))

    def render(self, show: bool = False, save_to_file: bool = True) -> None:
        df = self.retrieve_padded_dataframe()
        fig, ax = plt.subplots(figsize=(12, 2))
        ax.axis('off')
        ax.axis('tight')
        ax.set_title(f"{self.section} - {self.title} ({self.unit})")
        ax.table(cellText=df.values, colLabels=df.columns, rowLabels=df.index, loc='center')
        fig.tight_layout()
        if save_to_file:
            plt.savefig(f"./Figures/{self.title.replace(' ', '_')}.png")
        if show:
            plt.show()
        plt.close()


@dataclasses.dataclass
class QueryGenerationTable(EvaluationTable):

    @property
    def section(self) -> TableSection:
        return TableSection.CLIENT

    @property
    def title(self) -> str:
        return "Query generation time"

    @property
    def unit(self) -> str:
        return "μs"


@dataclasses.dataclass
class ResponseExtractionTable(EvaluationTable):

    @property
    def section(self) -> TableSection:
        return TableSection.CLIENT

    @property
    def title(self) -> str:
        return "Query extraction time"

    @property
    def unit(self) -> str:
        return "μs"


@dataclasses.dataclass
class RateTable(EvaluationTable):

    @property
    def section(self) -> TableSection:
        return TableSection.CLIENT

    @property
    def title(self) -> str:
        return "Rate"

    @property
    def unit(self) -> str:
        return "number of hashes per record"


@dataclasses.dataclass
class AnswerTable(EvaluationTable):

    @property
    def section(self) -> TableSection:
        return TableSection.SERVER

    @property
    def title(self) -> str:
        return "Answer time"

    @property
    def unit(self) -> str:
        return "μs"


@dataclasses.dataclass
class DatabaseGenerationTable(EvaluationTable):

    @property
    def section(self) -> TableSection:
        return TableSection.SERVER

    @property
    def title(self) -> str:
        return "Encoding time"

    @property
    def unit(self) -> str:
        return "μs"


@dataclasses.dataclass
class QueryCostTable(EvaluationTable):

    @property
    def section(self) -> TableSection:
        return TableSection.COMMUNICATION_COST

    @property
    def title(self) -> str:
        return "Query cost"

    @property
    def unit(self) -> str:
        return "KB"


@dataclasses.dataclass
class ResponseCostTable(EvaluationTable):

    @property
    def section(self) -> TableSection:
        return TableSection.COMMUNICATION_COST

    @property
    def title(self) -> str:
        return "Response cost"

    @property
    def unit(self) -> str:
        return "KB"


@dataclasses.dataclass
class TotalCostTable(EvaluationTable):

    @property
    def section(self) -> TableSection:
        return TableSection.COMMUNICATION_COST

    @property
    def title(self) -> str:
        return "Total cost"

    @property
    def unit(self) -> str:
        return "KB"


def calculate_height(q: int, n: int) -> float:
    """
    Calculate the height of a tree given
    based on log_q(n).
    :param q: Q-value of a q-ary tree.
    :param n: Number of leaves in a tree.
    :return: The height of the tree.
    """
    return math.log(1 << n, q)


def derive_total_database_size(q: int, h: float) -> int:
    """
    Derive the total database size (N) of a tree
    based on q(q^{h} - 1) / q - 1.
    :param q: Q-value of a q-ary tree.
    :param h: Height of the tree.
    :return: The total number of hashes in the
             database.
    """
    return math.ceil(q * ((q ** h) - 1) / (q - 1))


def read_directory(directory) -> dict[str, str]:
    filename_to_content_map = dict()
    for filename in os.listdir(directory):
        if filename == "Meta":
            continue
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            with open(filepath, 'r') as file:
                filename_to_content_map[filename] = file.read()
    return filename_to_content_map


def parse_database_configuration(configuration: str) -> tuple[str, list[int, int]]:
    configuration_file = f"./../Documents/Configuration/{configuration}.config"
    with open(configuration_file, "r") as file:
        lines = file.readlines()
    build_configuration: str = lines[1].strip()
    FurtherDims = FoldDims = int
    program_arguments: list[FurtherDims, FoldDims] = \
        [int(number)
         for number in lines[4].split()
         if number.isdigit()][:2]
    return build_configuration, program_arguments


def evaluate_run(evaluator: Evaluation, n: int) -> None:
    assert n in range(10, 31, 2), f"n={n} not in range(10, 31, 2)"
    n_column_index = range(10, 31, 2).index(n)
    for metric, value in read_directory(evaluator.data_path).items():
        table = evaluator.evaluation_table_map[metric]
        try:
            table.data[n_column_index].append(value)
        except IndexError:
            table.data.append([value])
        table.render(show=False)
        table.write_latex_table()


def run_spiral_trials() -> None:
    element_size: typing.Final = 32
    evaluator = Evaluation()
    for n in range(10, 31, 2):
        for q in [2, 16, 128, 256]:
            h = calculate_height(q, n)
            N = derive_total_database_size(q, h)
            N_power = math.ceil(math.log(N, 2))
            if N_power > 30:
                print("Unsupported database size.")
                continue
            print(
                "\n\n------------------------------------------------------------",
                f"Running database size: 2^{N_power} with Q={q} and n={n}."
            )
            trial_configuration_label: str = f"{N_power}_{element_size}"
            parameter_set, program_arguments \
                = parse_database_configuration(trial_configuration_label)
            cmake_configuration = CMakeConfiguration(
                trial_configuration_label, "Release"
            )
            execution_instance = CMakeRun(
                cmake_configuration,
                CMakeBuild(
                    parameter_set, cmake_configuration.build_path, "Seperated"
                ),
                executable="Seperated",
                database_file="colorA_10.json",
                further_dimensions=program_arguments[0],
                folding_factor=program_arguments[1]
            )
            print(f"\nExecuting command: {execution_instance.generate_command()}")
            execution_instance.run()
            evaluate_run(evaluator, n)


if __name__ == "__main__":
    run_spiral_trials()
