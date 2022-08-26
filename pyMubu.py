from dataclasses import dataclass, field
import numpy as np

@dataclass
class Buffer:
    max_size: int
    size: int
    sample_rate: float
    sample_offset: float
    mx_rows: int
    mx_cols: int
    mx_data: np.ndarray[int, np.dtype[np.double]]
    timeTags: np.ndarray[int, np.dtype[np.double]]
    info: list[str]

@dataclass
class Track:
    name: str
    mx_cols: int
    mx_rows: int
    has_var_rows: bool
    mx_col_names: list[str]
    has_time_tags: bool
    non_num_types: str
    max_size: str
    buffers: list[Buffer]

@dataclass
class Container:
    num_buffer: int
    num_tracks: int
    tracks: list[Track]

    