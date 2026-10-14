import threading
from typing import Callable, Optional
from finrest import FinREST, UserFinancialContext, FinolaResponse

class FinRESTService:
    """Service bridge integrating the FinREST SDK into the desktop client."""

    def __init__(self, endpoint_url: str = "http://127.0.0.1:8000"):
        self.client = FinREST(base_url=endpoint_url)

    def is_engine_online(self) -> bool:
        """Quick check to confirm whether local Ollama + FinREST are reachable."""
        res = self.client.health()
        return res.get("status") == "online"

    def query_async(
        self,
        message: str,
        context: UserFinancialContext,
        on_success: Callable[[FinolaResponse], None],
        on_error: Optional[Callable[[Exception], None]] = None
    ):
        """Dispatches an inquiry on a background thread to prevent UI freezing."""
        def _worker():
            try:
                response = self.client.chat(message=message, context=context)
                on_success(response)
            except Exception as exc:
                if on_error:
                    on_error(exc)

        thread = threading.Thread(target=_worker, daemon=True)
        thread.start()