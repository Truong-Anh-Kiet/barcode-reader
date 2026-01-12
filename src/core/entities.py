from dataclasses import dataclass
from typing import List, Tuple

@dataclass(frozen=True)
class BarcodeResult:
    content: str
    barcode_type: str
    bounding_box: Tuple[int, int, int, int]  # (x, y, w, h)