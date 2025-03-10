from enum import Enum
from .config import EMAIL_LABELS

def create_enum_from_dict(name, labels):
    """Dynamically create an Enum class from JSON keys."""
    return Enum(name, {key: key for key in labels.keys()})


EmailCategory = create_enum_from_dict("EmailCategory", EMAIL_LABELS)
