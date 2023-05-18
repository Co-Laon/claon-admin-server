from enum import Enum


class Role(Enum):
    PENDING = "pending"
    ADMIN = "admin"
    USER = "user"
    LECTOR = "lector"
    CENTER_ADMIN = "center_admin"


class OAuthProvider(Enum):
    GOOGLE = "google"
    KAKAO = "kakao"


class CenterUploadPurpose(Enum):
    PROFILE = "profile"
    IMAGE = "image"
    FEE = "fee"
    PROOF = "proof"

    def get_extensions(purpose: str):
        if purpose == "profile" or purpose == "image" or purpose == "fee":
            return ["jpg", "jpeg", "png"]

        if purpose == "proof":
            return ["jpg", "jpeg", "png", "pdf"]


class LectorUploadPurpose(Enum):
    PROOF = "proof"

    def get_extensions(purpose: str):
        if purpose == "proof":
            return ["jpg", "jpeg", "png", "pdf"]


class UserUploadPurpose(Enum):
    PROFILE = "profile"

    def get_extensions(purpose: str):
        if purpose == "profile":
            return ["jpg", "jpeg", "png"]


class WallType(Enum):
    ENDURANCE = "endurance"
    BOULDERING = "bouldering"


class MembershipType(Enum):
    PACKAGE = "package"
    MEMBER = "member"
    COURSE = "course"


class PeriodType(Enum):
    WEEK = "week"
    MONTH = "month"
