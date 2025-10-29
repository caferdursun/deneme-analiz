#!/usr/bin/env python3
"""
Discover and populate YouTube channels for all subjects
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.services.channel_service import ChannelService


def discover_all_subjects():
    """Discover channels for all subjects"""
    subjects = ["Matematik", "Fizik", "Kimya", "Biyoloji", "Türkçe"]

    db = SessionLocal()
    try:
        service = ChannelService(db)

        print("\n" + "="*70)
        print("YouTube Kanal Keşfi - Tüm Dersler")
        print("="*70)

        all_channels = []

        for subject in subjects:
            print(f"\n{'='*70}")
            print(f"📚 {subject} için kanal aranıyor...")
            print(f"{'='*70}")

            channels = service.discover_channels_for_subject(subject)

            if channels:
                print(f"\n✅ {subject} için {len(channels)} kanal bulundu:")
                for i, ch in enumerate(channels, 1):
                    print(f"   {i}. {ch.channel_name}")
                    print(f"      Aboneler: {ch.subscriber_count:,}")
                    print(f"      Videolar: {ch.video_count:,}")
                    print(f"      Trust Score: {ch.trust_score}")
                    print(f"      Kanal ID: {ch.channel_id}")
                all_channels.extend(channels)
            else:
                print(f"⚠️ {subject} için kanal bulunamadı")

        print(f"\n{'='*70}")
        print(f"✅ TOPLAM: {len(all_channels)} kanal veritabanına eklendi")
        print(f"{'='*70}")

        # Summary by subject
        print("\n📊 Ders Bazında Özet:")
        for subject in subjects:
            count = len([ch for ch in all_channels if ch.subject_name == subject])
            print(f"   {subject}: {count} kanal")

        return all_channels

    finally:
        db.close()


def list_all_channels():
    """List all channels in database"""
    db = SessionLocal()
    try:
        service = ChannelService(db)

        print("\n" + "="*70)
        print("Veritabanındaki Tüm YouTube Kanalları")
        print("="*70)

        subjects = service.get_all_subjects_with_channels()

        if not subjects:
            print("\n⚠️ Henüz hiç kanal eklenmemiş")
            return

        for subject in subjects:
            print(f"\n{'='*70}")
            print(f"📚 {subject}")
            print(f"{'='*70}")

            channels = service.get_trusted_channels(subject, min_trust_score=0.0, limit=10)

            for i, ch in enumerate(channels, 1):
                print(f"\n{i}. {ch.channel_name}")
                print(f"   Channel ID: {ch.channel_id}")
                print(f"   Aboneler: {ch.subscriber_count:,}")
                print(f"   Videolar: {ch.video_count:,}")
                print(f"   Görüntüleme: {ch.view_count:,}")
                print(f"   Trust Score: {ch.trust_score}")
                print(f"   Durum: {'✅ Aktif' if ch.is_active else '❌ Pasif'}")
                print(f"   Keşif: {ch.discovered_via}")
                if ch.custom_url:
                    print(f"   URL: https://youtube.com/{ch.custom_url}")

    finally:
        db.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="YouTube kanal keşfi ve listeleme")
    parser.add_argument("--list", action="store_true", help="Mevcut kanalları listele")
    parser.add_argument("--discover", action="store_true", help="Yeni kanalları keşfet")

    args = parser.parse_args()

    if args.list:
        list_all_channels()
    elif args.discover:
        discover_all_subjects()
    else:
        # Default: discover then list
        print("\n🚀 Kanallar keşfediliyor...")
        discover_all_subjects()
        print("\n" + "="*70)
        input("\nDevam etmek için Enter'a basın...")
        list_all_channels()
