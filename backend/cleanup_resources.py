"""
Clean up all resource-related data from the database
This will remove all resources, recommendation_resources links, and blacklist entries
"""
import sqlite3

db_path = "/root/projects/deneme-analiz/backend/deneme_analiz.db"

def cleanup_resources():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Delete in correct order to respect foreign key constraints
        print("Cleaning up resource data...")

        # 1. Delete recommendation_resources links
        cursor.execute("DELETE FROM recommendation_resources")
        deleted_links = cursor.rowcount
        print(f"✓ Deleted {deleted_links} recommendation-resource links")

        # 2. Delete resource_blacklist entries
        cursor.execute("DELETE FROM resource_blacklist")
        deleted_blacklist = cursor.rowcount
        print(f"✓ Deleted {deleted_blacklist} blacklist entries")

        # 3. Delete all resources
        cursor.execute("DELETE FROM resources")
        deleted_resources = cursor.rowcount
        print(f"✓ Deleted {deleted_resources} resources")

        # Commit changes
        conn.commit()
        print("\n✅ Resource database cleanup completed successfully!")

    except Exception as e:
        conn.rollback()
        print(f"\n❌ Error during cleanup: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    cleanup_resources()
