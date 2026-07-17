#!/usr/bin/env python3
"""CLI: install / migrate ResearchOS projects into tree/ + code layout."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from koi.adapters.project_install import (
    classify_install,
    install_project,
    layout_status,
)


def _print(data: object) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


def cmd_status(args: argparse.Namespace) -> None:
    scan = Path(args.scan_root).expanduser() if args.scan_root else None
    _print(layout_status(scan_root=scan))


def cmd_classify(args: argparse.Namespace) -> None:
    scan = Path(args.scan_root).expanduser() if args.scan_root else None
    plan = classify_install(
        args.path,
        scan_root=scan,
        sync_branch=args.branch,
        create_if_missing=args.create,
    )
    _print(
        {
            "case": plan.case.value,
            "repo_name": plan.repo_name,
            "code_root": str(plan.code_root),
            "tree_worktree": str(plan.tree_worktree),
            "tree_koi": str(plan.tree_koi),
            "sync_branch": plan.sync_branch,
            "detail": plan.detail,
        }
    )


def cmd_install(args: argparse.Namespace) -> None:
    scan = Path(args.scan_root).expanduser() if args.scan_root else None
    result = install_project(
        args.path,
        scan_root=scan,
        sync_branch=args.branch,
        title=args.title,
        push=not args.no_push,
        dry_run=args.dry_run,
        create_if_missing=args.create,
    )
    _print(result)
    if not result.get("ok"):
        raise SystemExit(1)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Install or migrate a project into ResearchOS tree/ layout:\n"
            "  tree/<repo>/koi-structure/  ← branch koi/research\n"
            "  <repo>/                    ← code, any branch"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--scan-root",
        default=None,
        help="Workspace root (default: parent of ReseachOS / KOI_SCAN_ROOTS)",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_status = sub.add_parser("status", help="Show tree/ vs code layout for all siblings")
    p_status.set_defaults(func=cmd_status)

    p_cls = sub.add_parser("classify", help="Detect which install case applies")
    p_cls.add_argument("path", help="Code repo path or sibling folder name")
    p_cls.add_argument("--branch", default=None, help="Sync branch (default koi/research)")
    p_cls.add_argument(
        "--create",
        action="store_true",
        help="Allow classifying as new_empty when folder is missing",
    )
    p_cls.set_defaults(func=cmd_classify)

    p_inst = sub.add_parser(
        "install",
        help=(
            "Apply the right case: new_with_code | integrated | new_empty | migrate_to_tree"
        ),
    )
    p_inst.add_argument("path", help="Code repo path or sibling folder name")
    p_inst.add_argument("--branch", default=None, help="Sync branch (default koi/research)")
    p_inst.add_argument("--title", default=None, help="Project title when seeding project.md")
    p_inst.add_argument("--dry-run", action="store_true")
    p_inst.add_argument("--no-push", action="store_true", help="Do not push new orphan branch")
    p_inst.add_argument(
        "--create",
        action="store_true",
        help="Create a brand-new empty project if path does not exist",
    )
    p_inst.set_defaults(func=cmd_install)

    # Alias: migrate → install (auto-detects migrate_to_tree)
    p_mig = sub.add_parser(
        "migrate",
        help="Same as install; useful when koi-structure is not yet under tree/",
    )
    p_mig.add_argument("path", help="Code repo path or sibling folder name")
    p_mig.add_argument("--branch", default=None)
    p_mig.add_argument("--title", default=None)
    p_mig.add_argument("--dry-run", action="store_true")
    p_mig.add_argument("--no-push", action="store_true")
    p_mig.add_argument("--create", action="store_true")
    p_mig.set_defaults(func=cmd_install)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
