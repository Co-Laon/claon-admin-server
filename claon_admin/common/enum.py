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

    def get_extensions(self):
        if self.value == "profile" or self.value == "image" or self.value == "fee":
            return ["jpg", "jpeg", "png"]

        if self.value == "proof":
            return ["jpg", "jpeg", "png", "pdf"]

    def is_valid_extension(self, extension: str):
        return extension in self.get_extensions()


class LectorUploadPurpose(Enum):
    PROOF = "proof"

    def get_extensions(self):
        if self.value == "proof":
            return ["jpg", "jpeg", "png", "pdf"]

    def is_valid_extension(self, extension: str):
        return extension in self.get_extensions()


class UserUploadPurpose(Enum):
    PROFILE = "profile"

    def get_extensions(self):
        if self.value == "profile":
            return ["jpg", "jpeg", "png"]

    def is_valid_extension(self, extension: str):
        return extension in self.get_extensions()


class WallType(Enum):
    ENDURANCE = "endurance"
    BOULDERING = "bouldering"


class CenterFeeType(Enum):
    PACKAGE = "package"
    MEMBER = "member"
    COURSE = "course"


class CenterMemberStatus(Enum):
    EXPIRED = "expired"
    USING = "using"


class CenterMemberSearchOrder(Enum):
    LATEST = "latest"
    EXTEND = "extend"


class MembershipStatusSearchOrder(Enum):
    ISSUED = "issued"
    STARTED = "started"
    EXPIRED = "expired"


class MembershipStatus(Enum):
    EXPIRED = "expired"
    TO_BE_EXPIRED = "to_be_expired"
    USING = "using"


class CenterFeeUploadPurpose(Enum):
    IMAGE = "image"

    def get_extensions(self):
        if self.value == "image":
            return ["jpg", "jpeg", "png"]

    def is_valid_extension(self, extension: str):
        return extension in self.get_extensions()


class PeriodType(Enum):
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
