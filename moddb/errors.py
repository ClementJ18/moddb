class ModdbException(Exception):
    """Standard exception raised when the moddb.Client encounters an error related to the request
    being made"""

    pass


class AwaitingAuthorisation(Exception):
    """This object is awaiting authorisation and can therefore not be accessed at the
    present time."""

    pass
