from typing import List, Type
from pydantic import BaseModel
from drf_spectacular.utils import OpenApiParameter


class PydanticModelParameters:

    def __init__(self, model: Type[BaseModel], location: str = "query"):
        self.model = model
        self.location = location

    def get_parameters(self) -> List[OpenApiParameter]:
        parameters = []
        for field_name, model_field in self.model.model_fields.items():
            param = OpenApiParameter(
                name=field_name,
                type=model_field.annotation,
                location=self.location,
                required=model_field.is_required,  # используем is_required
                description=model_field.description or "",
            )
            parameters.append(param)
        return parameters
