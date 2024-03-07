import inspect
from typing import Tuple

import fundus_evaluation
from fundus_evaluation.extractors import Extractor

EXTRACTORS: Tuple[Extractor, ...] = tuple(
    function
    for name, function in inspect.getmembers(fundus_evaluation.extractors, inspect.isfunction)
    if name.startswith("extract_")
)
