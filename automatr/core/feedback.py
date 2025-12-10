"""Feedback management for Automatr.

Captures user feedback (thumbs-up/down) on LLM-generated outputs
to enable future template improvements.
"""

import hashlib
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Literal

from automatr.core.config import get_config_dir


@dataclass
class FeedbackEntry:
    """A single feedback entry for a generated output.
    
    Attributes:
        timestamp: ISO format timestamp when feedback was given.
        template_name: Name of the template used.
        prompt_hash: SHA256 hash of the full prompt (for deduplication).
        output_snippet: First 200 chars of the generated output.
        rating: User rating - "up" (thumbs-up) or "down" (thumbs-down).
        correction: Optional user-provided correction (thumbs-down only).
    """
    
    timestamp: str
    template_name: str
    prompt_hash: str
    output_snippet: str
    rating: Literal["up", "down"]
    correction: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        d = asdict(self)
        # Remove None values for cleaner JSON
        return {k: v for k, v in d.items() if v is not None}
    
    @classmethod
    def from_dict(cls, data: dict) -> "FeedbackEntry":
        """Create from dictionary."""
        return cls(
            timestamp=data.get("timestamp", ""),
            template_name=data.get("template_name", ""),
            prompt_hash=data.get("prompt_hash", ""),
            output_snippet=data.get("output_snippet", ""),
            rating=data.get("rating", "up"),
            correction=data.get("correction"),
        )


class FeedbackManager:
    """Manages feedback storage and retrieval."""
    
    def __init__(self):
        self._entries: List[FeedbackEntry] = []
        self._path = get_config_dir() / "feedback.json"
        self._load()
    
    def _load(self):
        """Load feedback from disk."""
        if self._path.exists():
            try:
                with open(self._path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._entries = [
                    FeedbackEntry.from_dict(e) for e in data.get("entries", [])
                ]
            except (json.JSONDecodeError, KeyError, TypeError):
                # Corrupted file - start fresh
                self._entries = []
    
    def _save(self):
        """Save feedback to disk."""
        self._path.parent.mkdir(parents=True, exist_ok=True)
        data = {"entries": [e.to_dict() for e in self._entries]}
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    
    def add(
        self,
        template_name: str,
        prompt: str,
        output: str,
        rating: Literal["up", "down"],
        correction: Optional[str] = None,
    ) -> FeedbackEntry:
        """Add a new feedback entry.
        
        Args:
            template_name: Name of the template used.
            prompt: The full rendered prompt sent to LLM.
            output: The full generated output.
            rating: "up" for thumbs-up, "down" for thumbs-down.
            correction: Optional correction text (thumbs-down only).
        
        Returns:
            The created FeedbackEntry.
        """
        entry = FeedbackEntry(
            timestamp=datetime.now().isoformat(),
            template_name=template_name,
            prompt_hash=hashlib.sha256(prompt.encode()).hexdigest()[:16],
            output_snippet=output[:200] if output else "",
            rating=rating,
            correction=correction if correction and correction.strip() else None,
        )
        self._entries.append(entry)
        self._save()
        return entry
    
    def get_by_template(self, template_name: str) -> List[FeedbackEntry]:
        """Get all feedback entries for a specific template."""
        return [e for e in self._entries if e.template_name == template_name]
    
    def get_all(self) -> List[FeedbackEntry]:
        """Get all feedback entries."""
        return list(self._entries)
    
    def count_by_template(self, template_name: str) -> dict:
        """Get count of thumbs-up and thumbs-down for a template."""
        entries = self.get_by_template(template_name)
        return {
            "up": sum(1 for e in entries if e.rating == "up"),
            "down": sum(1 for e in entries if e.rating == "down"),
        }


# Module-level singleton
_feedback_manager: Optional[FeedbackManager] = None


def get_feedback_manager() -> FeedbackManager:
    """Get the global FeedbackManager instance."""
    global _feedback_manager
    if _feedback_manager is None:
        _feedback_manager = FeedbackManager()
    return _feedback_manager


def build_improvement_prompt(template_content: str, refinements: List[str], additional_notes: str = "") -> str:
    """Build a prompt asking the LLM to improve a template based on refinements.
    
    Args:
        template_content: The current template content.
        refinements: List of user feedback/corrections to incorporate.
        additional_notes: Optional additional guidance for this improvement attempt.
    
    Returns:
        A prompt string for the LLM.
    """
    prompt_parts = [
        "You are a prompt engineering expert. Improve the template below based on user feedback.",
        "",
        "CURRENT TEMPLATE:",
        "---START TEMPLATE---",
        template_content,
        "---END TEMPLATE---",
        "",
    ]
    
    if refinements:
        prompt_parts.extend(["USER FEEDBACK TO ADDRESS:"])
        for i, ref in enumerate(refinements, 1):
            prompt_parts.append(f"{i}. {ref}")
        prompt_parts.append("")
    
    if additional_notes:
        prompt_parts.extend(["ADDITIONAL NOTES:", additional_notes, ""])
    
    prompt_parts.extend([
        "CRITICAL INSTRUCTIONS:",
        "- Output ONLY the improved template text",
        "- Do NOT include any explanations, commentary, or meta-text",
        "- Do NOT include markdown code blocks or formatting markers",
        "- Do NOT include phrases like 'Here is the improved template'",
        "- Do NOT include the words 'template', 'improvement', 'feedback', or 'refinement' in your output",
        "- Keep all {{variable_name}} placeholders exactly as they appear",
        "- The output should be ready to use directly as a prompt template",
        "",
        "OUTPUT THE IMPROVED TEMPLATE NOW:",
    ])
    
    return "\n".join(prompt_parts)
