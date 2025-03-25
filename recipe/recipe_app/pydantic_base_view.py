from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError as DRFValidationError
from pydantic import ValidationError as PydanticValidationError


class PydanticAPIView(APIView):
    """
    Custom APIView that validates request data using a Pydantic model.
    """

    pydantic_model = None  # Override in subclasses with a Pydantic model

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        if self.pydantic_model and request.method in ('POST', 'PUT', 'PATCH'):
            self.validate_request_data()

    def validate_request_data(self):
        try:
            validated_data = self.pydantic_model(**self.request.data)
            self.request.pydantic = validated_data
        except PydanticValidationError as e:
            raise DRFValidationError(e.errors())


class FileUploadPydanticAPIView(PydanticAPIView):
    """
    Custom APIView for file upload endpoints.
    Creates a mutable copy of request.data (without modifying the original)
    and removes specified file fields before validation.
    """

    file_fields: list[str] = []

    def initial(self, request, *args, **kwargs):
        # Create a mutable copy of the incoming data without changing request.data
        try:
            mutable_data = request.data.copy()
        except Exception:
            mutable_data = dict(request.data)
        for field in self.file_fields:
            mutable_data.pop(field, None)
        # Store the mutable data for later use in validation
        self._validated_request_data = mutable_data
        super().initial(request, *args, **kwargs)

    def validate_request_data(self):
        data = getattr(self, '_validated_request_data', self.request.data)
        try:
            validated_data = self.pydantic_model(**data)
            self.request.pydantic = validated_data
        except PydanticValidationError as e:
            raise DRFValidationError(e.errors())
