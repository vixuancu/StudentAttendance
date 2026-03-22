from enum import Enum


class ERROR_CODES:
    class CAMERA(str, Enum):
        CAMERA_NOT_FOUND = "CAMERA_NOT_FOUND"
        IP_ADDRESS_IS_EXISTED = "IP_ADDRESS_IS_EXISTED"
