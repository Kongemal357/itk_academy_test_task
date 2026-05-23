from src.api.v1.schemas.base import ErrorResponse

error_dict_400_404_409_422_500: dict = {
    400: {"model": ErrorResponse},
    404: {"model": ErrorResponse},
    409: {"model": ErrorResponse},
    422: {"model": ErrorResponse},
    500: {"model": ErrorResponse},
}
