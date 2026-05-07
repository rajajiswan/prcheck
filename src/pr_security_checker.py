from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class SecurityResult:
    passed: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    secrets_found: List[str] = field(default_factory=list)

    def fail(self, message: str) -> None:
        self.passed = False
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    def __bool__(self) -> bool:
        return self.passed


_SECRET_PATTERNS: List[tuple[str, str]] = [
    (r"(?i)api[_-]?key\s*=\s*['\"][^'\"]{8,}", "API key"),
    (r"(?i)secret\s*=\s*['\"][^'\"]{8,}", "secret value"),
    (r"(?i)password\s*=\s*['\"][^'\"]{4,}", "password"),
    (r"(?i)token\s*=\s*['\"][^'\"]{8,}", "token"),
    (r"AKIA[0-9A-Z]{16}", "AWS access key"),
    (r"(?i)private[_-]?key\s*=\s*['\"][^'\"]{8,}", "private key"),
]

_SENSITIVE_FILES: List[str] = [
    ".env",
    ".env.local",
    ".env.production",
    "id_rsa",
    "id_ed25519",
    "*.pem",
    "*.key",
    "credentials.json",
    "secrets.yaml",
    "secrets.yml",
]


def _matches_sensitive_file(filename: str) -> Optional[str]:
    for pattern in _SENSITIVE_FILES:
        if pattern.startswith("*"):
            if filename.endswith(pattern[1:]):
                return pattern
        elif filename == pattern or filename.endswith("/" + pattern):
            return pattern
    return None


def check_pr_security(
    pr_body: str,
    diff_files: List[str],
    diff_patch: str,
    *,
    block_secrets: bool = True,
    block_sensitive_files: bool = True,
    warn_only: bool = False,
) -> SecurityResult:
    result = SecurityResult()

    if block_sensitive_files:
        for filename in diff_files:
            match = _matches_sensitive_file(filename)
            if match:
                msg = f"Sensitive file detected in diff: '{filename}' (matches pattern '{match}')"
                if warn_only:
                    result.warn(msg)
                else:
                    result.fail(msg)

    if block_secrets:
        for pattern, label in _SECRET_PATTERNS:
            if re.search(pattern, diff_patch):
                result.secrets_found.append(label)
                msg = f"Possible {label} detected in diff"
                if warn_only:
                    result.warn(msg)
                else:
                    result.fail(msg)

    return result
