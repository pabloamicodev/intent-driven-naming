"""Deterministic resource-route expectations for behavior evaluations."""

from __future__ import annotations

from typing import Any

LANGUAGE_PROFILES = {
    "typescript": "typescript-javascript",
    "javascript": "typescript-javascript",
    "react": "web-framework",
    "python": "dynamic",
    "ruby": "dynamic",
    "php": "dynamic",
    "go": "systems",
    "rust": "systems",
    "c": "systems",
    "cpp": "systems",
    "java": "managed-mobile",
    "kotlin": "managed-mobile",
    "csharp": "managed-mobile",
    "swift": "managed-mobile",
    "dart": "managed-mobile",
    "haskell": "functional-concurrent",
    "ocaml": "functional-concurrent",
    "fsharp": "functional-concurrent",
    "scala": "functional-concurrent",
    "clojure": "functional-concurrent",
    "erlang": "functional-concurrent",
    "elixir": "functional-concurrent",
    "sql": "data-infrastructure",
    "shell": "data-infrastructure",
    "powershell": "data-infrastructure",
    "terraform": "data-infrastructure",
    "kubernetes": "data-infrastructure",
    "protobuf": "data-infrastructure",
}
FEATURES = {"callable", "local-variable", "high-risk"}
BOUNDARY_TAGS = {"contract", "serialization", "schema", "protobuf"}
BOUNDARY_RISKS = {"dynamic", "generated", "stateful"}


def allowed_behavior_resources(case: dict[str, Any], routes: dict[str, Any]) -> set[str]:
    """Return resources justified by explicit case metadata and route rules."""
    allowed = set(routes.get("always", []))
    mode = "new-code" if case.get("mode") == "generation" else case.get("mode")
    allowed.update(routes.get("modes", {}).get(mode, []))

    tags = set(case.get("tags", []))
    features = (set(case.get("features", [])) | tags) & FEATURES
    for feature in features:
        allowed.update(routes.get("features", {}).get(feature, []))

    languages = set(case.get("languages", []))
    profiles = {LANGUAGE_PROFILES[language] for language in languages if language in LANGUAGE_PROFILES}
    if "web-framework" in profiles:
        profiles.discard("typescript-javascript")
    for profile in profiles:
        allowed.update(routes.get("profiles", {}).get(profile, []))

    if (
        len(languages) > 1
        or case.get("contract_risk") in BOUNDARY_RISKS
        or bool(tags & BOUNDARY_TAGS)
    ):
        allowed.update(routes.get("conditional_core", {}).get("polyglot-boundary", []))
    if "generic" in languages or any(
        language not in LANGUAGE_PROFILES for language in languages
    ):
        allowed.update(routes.get("conditional_core", {}).get("uncertain-conventions", []))
    return allowed


def loaded_profile_count(resources: set[str], routes: dict[str, Any]) -> int:
    """Count profile families while treating the web profile as a TS/JS superset."""
    profiles = routes.get("profiles", {})
    loaded: set[str] = set()
    for profile, paths in profiles.items():
        if any(path in resources for path in paths):
            loaded.add(profile)
    if "web-framework" in loaded:
        loaded.discard("typescript-javascript")
    return len(loaded)
