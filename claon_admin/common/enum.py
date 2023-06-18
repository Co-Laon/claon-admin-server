from enum import Enum


class Role(Enum):
    PENDING = "pending"
    NOT_APPROVED = "not_approved"
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


class MemberInfoSearchStatus(Enum):
    EXPIRED = "expired"
    USING = "using"


class MemberInfoSearchOrder(Enum):
    LATEST = "latest"
    EXTEND = "extend"


class MembershipIssuanceInfoSearchOrder(Enum):
    ISSUED = "issued"
    STARTED = "started"
    EXPIRED = "expired"


class MembershipIssuanceInfoSearchStatus(Enum):
    EXPIRED = "expired"
    TO_BE_EXPIRED = "to_be_expired"
    USING = "using"


class MembershipUploadPurpose(Enum):
    IMAGE = "image"

    def get_extensions(purpose: str):
        if purpose == "image":
            return ["jpg", "jpeg", "png"]


class PeriodType(Enum):
    WEEK = "week"
    MONTH = "month"
