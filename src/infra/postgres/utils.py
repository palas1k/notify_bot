from typing import Annotated

from sqlalchemy.orm import mapped_column

integer_id = Annotated[
    int, mapped_column(primary_key=True, nullable=False, autoincrement=True)
]

default_dict = {
    "математика": 0,
    "русский": 0,
    "английский": 0,
    "физика": 0
}
