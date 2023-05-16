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


class LectorUploadPurpose(Enum):
    PROOF = "proof"


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
