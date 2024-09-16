from typing import Annotated

from sqlalchemy.orm import mapped_column

integer_id = Annotated[
    int, mapped_column(primary_key=True, nullable=False, autoincrement=True)
]