#!/usr/bin/env python3
"""
Crossmint Challenge - Enhanced Megaverse Creator
Main entry point for the application.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

# flake8: noqa: E402 - imports must be after sys.path modification
from src.config.settings import get_settings
from src.models.exceptions import ConfigurationError, MegaverseError
from src.services.api_client import APIClient
from src.services.goal_loader import GoalLoader
from src.services.megaverse_creator import ConsoleProgressObserver, MegaverseCreator
from src.services.object_factory import ObjectFactory
from src.utils.validators import validate_candidate_id


def setup_logging(log_level: str = "INFO") -> None:
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler("megaverse.log")],
    )


def create_services(settings) -> tuple[APIClient, GoalLoader, ObjectFactory, MegaverseCreator]:
    """Create and configure all services."""
    # Create core services
    api_client = APIClient(settings.api_base_url, settings.max_retries)
    goal_loader = GoalLoader()
    object_factory = ObjectFactory()

    # Create main orchestrator
    megaverse_creator = MegaverseCreator(
        api_client=api_client,
        goal_loader=goal_loader,
        object_factory=object_factory,
        settings=settings,
    )

    # Add console observer for progress tracking
    console_observer = ConsoleProgressObserver()
    megaverse_creator.add_observer(console_observer)

    return api_client, goal_loader, object_factory, megaverse_creator


def command_create(args, megaverse_creator: MegaverseCreator) -> None:
    """Handle create command."""
    print("🚀 Crossmint Challenge - Enhanced Megaverse Creator")
    print("=" * 60)

    try:
        if args.from_api:
            print("📡 Loading goal map from API...")
            results = megaverse_creator.create_from_api(
                args.candidate_id or megaverse_creator.settings.candidate_id
            )
        else:
            print(f"📁 Loading goal map from file: {args.goal_file}")
            results = megaverse_creator.create_from_file(args.goal_file)

        print("\n" + "=" * 60)
        print("📊 Final Results:")
        print(f"   ✅ Successful: {results['successful']}")
        print(f"   ❌ Failed: {results['failed']}")
        print(f"   📊 Total: {results['total']}")

        if results["failed"] == 0:
            print("\n🎉 All objects created successfully!")
            print("   Check your map at the challenge website to verify.")
        else:
            print(f"\n⚠️  {results['failed']} objects failed to create.")
            sys.exit(1)

    except MegaverseError as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


def command_preview(args, megaverse_creator: MegaverseCreator) -> None:
    """Handle preview command."""
    print("🔍 Megaverse Creation Preview")
    print("=" * 40)

    try:
        preview = megaverse_creator.preview_creation(args.goal_file)

        stats = preview["map_stats"]
        print(f"📏 Map Dimensions: {stats['dimensions']['rows']}x{stats['dimensions']['columns']}")
        print(f"📊 Total Objects: {stats['total_objects']}")
        print(f"🚀 Space Cells: {stats['space_count']}")

        print("\n📈 Object Type Breakdown:")
        for obj_type, count in stats["type_counts"].items():
            if count > 0:
                print(f"   {obj_type}: {count}")

        print("\n🎯 Specific Object Counts:")
        for obj_type, count in stats["object_counts"].items():
            print(f"   {obj_type}: {count}")

        print(f"\n⏱️  Estimated Time: {preview['estimated_time_minutes']:.1f} minutes")

        # Show first few objects as example
        if preview["objects"]:
            print("\n📍 First 5 Objects to Create:")
            for i, obj in enumerate(preview["objects"][:5], 1):
                print(f"   {i}. {obj}")

            if len(preview["objects"]) > 5:
                print(f"   ... and {len(preview['objects']) - 5} more")

    except MegaverseError as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


def command_delete(args, megaverse_creator: MegaverseCreator) -> None:
    """Handle delete command."""
    print("🗑️  Megaverse Deletion")
    print("=" * 30)

    candidate_id = args.candidate_id or megaverse_creator.settings.candidate_id

    print(f"⚠️  This will delete ALL objects from the megaverse for candidate: {candidate_id}")
    confirm = input("Are you sure you want to proceed? (y/N): ")

    if confirm.lower() != "y":
        print("❌ Operation cancelled.")
        return

    try:
        results = megaverse_creator.delete_all(candidate_id)

        print("\n📊 Deletion Results:")
        print(f"   ✅ Successful: {results['successful']}")
        print(f"   ❌ Failed: {results['failed']}")
        print(f"   📊 Total: {results['total']}")

        if results["failed"] == 0:
            print("\n🎉 All objects deleted successfully!")
        else:
            print(f"\n⚠️  {results['failed']} objects failed to delete.")

    except MegaverseError as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Enhanced Crossmint Megaverse Creator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s create                          # Create from goal.json
  %(prog)s create --from-api               # Create from API goal map
  %(prog)s create --goal-file custom.json  # Create from custom file
  %(prog)s preview                         # Preview creation plan
  %(prog)s delete                          # Delete all objects
        """,
    )

    # Global arguments
    parser.add_argument("--candidate-id", help="Candidate ID (overrides environment/config)")
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level",
    )

    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Create command
    create_parser = subparsers.add_parser("create", help="Create megaverse")
    create_parser.add_argument(
        "--goal-file", default="goal.json", help="Path to goal map file (default: goal.json)"
    )
    create_parser.add_argument(
        "--from-api", action="store_true", help="Load goal map from API instead of file"
    )

    # Preview command
    preview_parser = subparsers.add_parser("preview", help="Preview creation plan")
    preview_parser.add_argument(
        "--goal-file", default="goal.json", help="Path to goal map file (default: goal.json)"
    )

    # Delete command
    subparsers.add_parser("delete", help="Delete all objects")  # Fixed: removed unused variable

    # Parse arguments
    args = parser.parse_args()

    # Default to create if no command specified
    if args.command is None:
        args.command = "create"
        args.goal_file = "goal.json"
        args.from_api = False

    # Setup logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)

    try:
        # Load settings
        settings = get_settings()

        # Override candidate ID if provided
        if args.candidate_id:
            settings.candidate_id = args.candidate_id

        # Validate candidate ID
        validate_candidate_id(settings.candidate_id)

        # Create services
        api_client, goal_loader, object_factory, megaverse_creator = create_services(settings)

        # Execute command
        if args.command == "create":
            command_create(args, megaverse_creator)
        elif args.command == "preview":
            command_preview(args, megaverse_creator)
        elif args.command == "delete":
            command_delete(args, megaverse_creator)
        else:
            parser.print_help()
            sys.exit(1)

    except ConfigurationError as e:
        print(f"❌ Configuration Error: {e}")
        print("\nPlease check your .env file or environment variables.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        logger.exception("Unexpected error occurred")
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
