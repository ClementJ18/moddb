class ModdbException(Exception):
    """Standard exception raised when the moddb.Client encounters an error related to the request
    being made"""

    pass


class AwaitingAuthorisation(ModdbException):
    """This object is awaiting authorisation and can therefore not be accessed at the
    present time."""

    pass


class Ratelimited(ModdbException):
    """You are being ratelimited internally by the library, please be respectful of the
    website and its creators."""

    def __init__(self, message, remaining) -> None:
        super().__init__(message)

        self.remaining = remaining


class AuthError(ModdbException):
    """The user you are trying to login with requires 2FA to login. Use
    the TwoFactorAuthClient object to do so.
    """

    pass
