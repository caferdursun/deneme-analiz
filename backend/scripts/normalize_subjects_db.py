"""
Script to normalize subject names in existing database records
Run this once to clean up existing data with (T) suffixes
"""
from sqlalchemy import create_engine, text
from app.core.config import settings
from app.utils.subject_normalizer import normalize_subject_name
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def normalize_database():
    """Normalize subject names in all relevant tables"""

    engine = create_engine(settings.DATABASE_URL)

    with engine.connect() as conn:
        # Get table names to update
        tables_to_update = [
            "subject_results",
            "learning_outcomes",
            "questions"
        ]

        for table in tables_to_update:
            logger.info(f"\n=== Processing table: {table} ===")

            # Get all unique subject names
            result = conn.execute(text(f"SELECT DISTINCT subject_name FROM {table}"))
            unique_subjects = [row[0] for row in result]

            logger.info(f"Found {len(unique_subjects)} unique subject names")

            # Track changes
            changes = {}

            for old_name in unique_subjects:
                new_name = normalize_subject_name(old_name)
                if old_name != new_name:
                    changes[old_name] = new_name
                    logger.info(f"  '{old_name}' -> '{new_name}'")

            if not changes:
                logger.info(f"No changes needed for {table}")
                continue

            # Apply updates
            logger.info(f"\nApplying {len(changes)} updates to {table}...")

            for old_name, new_name in changes.items():
                result = conn.execute(
                    text(f"UPDATE {table} SET subject_name = :new_name WHERE subject_name = :old_name"),
                    {"old_name": old_name, "new_name": new_name}
                )
                logger.info(f"  Updated {result.rowcount} rows: '{old_name}' -> '{new_name}'")

            conn.commit()
            logger.info(f"✓ Completed {table}")

        # Show final unique subjects
        logger.info("\n=== Final unique subjects across all tables ===")
        for table in tables_to_update:
            result = conn.execute(text(f"SELECT DISTINCT subject_name FROM {table} ORDER BY subject_name"))
            subjects = [row[0] for row in result]
            logger.info(f"\n{table} ({len(subjects)} subjects):")
            for subject in subjects:
                logger.info(f"  - {subject}")


if __name__ == "__main__":
    logger.info("Starting database subject normalization...")
    logger.info(f"Database: {settings.DATABASE_URL}\n")

    response = input("This will modify existing database records. Continue? (yes/no): ")
    if response.lower() != "yes":
        logger.info("Aborted.")
        exit(0)

    normalize_database()
    logger.info("\n✓ Database normalization completed!")
