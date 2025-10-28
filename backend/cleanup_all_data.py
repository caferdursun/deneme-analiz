"""
Complete database cleanup - removes ALL data for fresh testing
WARNING: This will delete everything!
"""
import sqlite3

db_path = "/root/projects/deneme-analiz/backend/deneme_analiz.db"

def cleanup_all_data():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        print("=" * 80)
        print("FULL DATABASE CLEANUP - REMOVING ALL DATA")
        print("=" * 80)

        # 1. Resource-related tables
        print("\n[1] Cleaning resource data...")
        cursor.execute("DELETE FROM recommendation_resources")
        print(f"   ✓ Deleted {cursor.rowcount} recommendation-resource links")

        cursor.execute("DELETE FROM resource_blacklist")
        print(f"   ✓ Deleted {cursor.rowcount} blacklist entries")

        cursor.execute("DELETE FROM resources")
        print(f"   ✓ Deleted {cursor.rowcount} resources")

        # 2. Study plans
        print("\n[2] Cleaning study plan data...")
        cursor.execute("DELETE FROM study_plan_items")
        print(f"   ✓ Deleted {cursor.rowcount} study plan items")

        cursor.execute("DELETE FROM study_plan_days")
        print(f"   ✓ Deleted {cursor.rowcount} study plan days")

        cursor.execute("DELETE FROM study_plans")
        print(f"   ✓ Deleted {cursor.rowcount} study plans")

        # 3. Recommendations
        print("\n[3] Cleaning recommendation data...")
        cursor.execute("DELETE FROM recommendations")
        print(f"   ✓ Deleted {cursor.rowcount} recommendations")

        # 4. Questions
        print("\n[4] Cleaning question data...")
        cursor.execute("DELETE FROM questions")
        print(f"   ✓ Deleted {cursor.rowcount} questions")

        # 5. Learning outcomes
        print("\n[5] Cleaning learning outcome data...")
        cursor.execute("DELETE FROM learning_outcomes")
        print(f"   ✓ Deleted {cursor.rowcount} learning outcomes")

        # 6. Subject results
        print("\n[6] Cleaning subject result data...")
        cursor.execute("DELETE FROM subject_results")
        print(f"   ✓ Deleted {cursor.rowcount} subject results")

        # 7. Exam results
        print("\n[7] Cleaning exam result data...")
        cursor.execute("DELETE FROM exam_results")
        print(f"   ✓ Deleted {cursor.rowcount} exam results")

        # 8. Exams
        print("\n[8] Cleaning exam data...")
        cursor.execute("DELETE FROM exams")
        print(f"   ✓ Deleted {cursor.rowcount} exams")

        # 9. Students (if you want to keep student profile, comment this out)
        print("\n[9] Cleaning student data...")
        cursor.execute("DELETE FROM students")
        print(f"   ✓ Deleted {cursor.rowcount} students")

        # Commit all changes
        conn.commit()

        print("\n" + "=" * 80)
        print("✅ COMPLETE DATABASE CLEANUP SUCCESSFUL!")
        print("=" * 80)
        print("\nDatabase is now empty and ready for fresh testing.")

    except Exception as e:
        conn.rollback()
        print(f"\n❌ Error during cleanup: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    print("\n⚠️  WARNING: This will delete ALL data from the database!")
    response = input("Are you sure you want to continue? (yes/no): ")

    if response.lower() == 'yes':
        cleanup_all_data()
    else:
        print("\n❌ Cleanup cancelled.")
