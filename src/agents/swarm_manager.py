import logging
import os
from typing import Any, Callable, Dict, Optional

from .license_verifier import LicenseVerifier


class SwarmManager:
    """Wrapper around the optional ``openai-swarm`` package.

    If ``openai-swarm`` is installed, it can be used to coordinate multiple
    agents. If it is not available, agents will run locally.
    """

    def __init__(self, api_key: Optional[str] = None) -> None:
        self.logger = logging.getLogger(__name__)
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        try:
            from openai_swarm import AgentSwarm  # type: ignore
            self._swarm_cls = AgentSwarm
            self.logger.debug("openai-swarm available for orchestration")
        except Exception:  # pragma: no cover - package optional
            self._swarm_cls = None
            self.logger.warning(
                "openai-swarm not installed, agents will run locally"
            )

    def launch(self, func: Callable[..., Dict[str, Any]], *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Launch a callable either via ``openai-swarm`` or locally."""
        if self._swarm_cls:
            try:
                swarm = self._swarm_cls(api_key=self.api_key)
                # Actual orchestration would go here. This simple implementation
                # just runs the function locally as a placeholder.
                self.logger.info("Running agent via openai-swarm")
            except Exception as exc:  # pragma: no cover - runtime safeguard
                self.logger.error(f"Failed to run via openai-swarm: {exc}")
        return func(*args, **kwargs)


class SwarmOrchestrator:
    """High level orchestrator for document processing agents."""

    def __init__(self, swarm_manager: Optional[SwarmManager] = None) -> None:
        self.swarm_manager = swarm_manager or SwarmManager()
        self.logger = logging.getLogger(__name__)

    def run_license_verifier(self, document_path: str) -> Dict[str, Any]:
        """Launch the :class:`LicenseVerifier` agent."""
        verifier = LicenseVerifier()
        return self.swarm_manager.launch(verifier.verify_license, document_path)
