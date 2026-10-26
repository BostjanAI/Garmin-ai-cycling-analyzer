from __future__ import annotations

import argparse

from .bootstrap import build_repository, build_sync_service, configure_logging
from .config import Settings


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description="Garmin AI Cycling Analyzer")
    commands = root.add_subparsers(dest="command", required=True)
    commands.add_parser("sync", help="Uvozi nove FIT aktivnosti")
    commands.add_parser("list", help="Izpiši shranjene aktivnosti")
    delete = commands.add_parser("delete-all", help="Izbriši vse lokalno shranjene analize")
    delete.add_argument("--confirm", action="store_true", help="Potrdi nepovraten izbris")
    return root


def main() -> None:
    args = parser().parse_args()
    settings = Settings.from_env()
    configure_logging(settings.log_level)
    repository = build_repository(settings)

    if args.command == "sync":
        result = build_sync_service(settings).sync()
        print(
            f"Uvoženo: {result.imported}, preskočeno: {result.skipped}, "
            f"napake: {len(result.errors)}"
        )
        for error in result.errors:
            print(f"- {error}")
    elif args.command == "list":
        for item in repository.list_all():
            print(f"{item['started_at']} | {item['source_name']} | {item['distance_m'] or 0:.0f} m")
    elif args.command == "delete-all":
        if not args.confirm:
            raise SystemExit("Izbris ni izveden. Dodajte --confirm.")
        print(f"Izbrisano: {repository.delete_all()}")


if __name__ == "__main__":
    main()

