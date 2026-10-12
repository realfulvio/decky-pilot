MESSAGES = {
    "NOT_CONFIGURED": "Configura provider, modello e credenziale nelle impostazioni.",
    "INVALID_INPUT": "Dati non validi: controlla i campi e i limiti indicati.",
    "AUTH_FAILED": "Credenziale rifiutata dal provider.",
    "MODEL_UNAVAILABLE": "Modello non disponibile: selezionane uno autorizzato.",
    "RATE_LIMITED": "Limite del provider raggiunto. Attendi prima di riprovare.",
    "TIMEOUT": "La richiesta ha superato il tempo massimo.",
    "NETWORK_ERROR": "Provider non raggiungibile o risposta non valida.",
    "IMAGE_UNSUPPORTED": "Supporto immagini non confermato per questo modello.",
    "CONSENT_REQUIRED": "Serve il consenso esplicito per questa destinazione.",
    "CONTEXT_STALE": "Il contesto è cambiato o non è abbastanza recente.",
    "CANCELLED": "Richiesta annullata; il provider potrebbe aver già applicato un costo.",
    "PROVIDER_BLOCKED": "Il provider non ha restituito una risposta utilizzabile.",
    "BUSY": "Una richiesta è già in corso.",
    "INTERNAL_ERROR": "Operazione non riuscita. Controlla la diagnostica.",
    "STORAGE_ERROR": "Archivio locale non sicuro o non valido; i dati non sono stati azzerati.",
    "VOICE_UNAVAILABLE": "Voce non disponibile: la risposta testuale resta accessibile.",
}


class RpcError(Exception):
    def __init__(self, code, retry_after_ms=None):
        self.code = code
        self.retry_after_ms = retry_after_ms
        super().__init__(MESSAGES.get(code, MESSAGES["INTERNAL_ERROR"]))

    def payload(self):
        value = {"code": self.code, "message": str(self),
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
