from typing import Dict, Optional

class FactExtractor:
    """Provider-agnostic extraction interface."""

    def extract(self, text: str) -> Dict[str, Optional[str]]:
        raise NotImplementedError
