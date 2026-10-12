from .i18n import CATALOGS, translate

MESSAGES = {key[6:]: value for key, value in CATALOGS["en"].items() if key.startswith("error.")}


class RpcError(Exception):
    def __init__(self, code, retry_after_ms=None):
        self.code = code
        self.retry_after_ms = retry_after_ms
        super().__init__(MESSAGES.get(code, MESSAGES["INTERNAL_ERROR"]))

    def payload(self, language="en"):
        value = {"code": self.code, "message": translate("error." + self.code, language),
                 "retryable": self.code in {"RATE_LIMITED", "TIMEOUT", "NETWORK_ERROR", "BUSY"}}
        if self.retry_after_ms is not None:
            value["retryAfterMs"] = self.retry_after_ms
        return value


def require(condition, code="INVALID_INPUT"):
    if not condition:
        raise RpcError(code)


def fields(value, allowed):
    require(isinstance(value, dict) and set(value) <= set(allowed))


def string(value, maximum, minimum=0):
    require(isinstance(value, str) and minimum <= len(value) <= maximum and "\x00" not in value)
    return value.strip()
