#!/usr/bin/env python3
"""
Quick Fix: Update all uploaded_documents to use the frontend's hardcoded org ID.
Frontend always sends organizationId = 6732a1000000000000000001
"""
import os
import sys
from bson import ObjectId

try:
    from pymongo import MongoClient
except ImportError:
    print("[Error] pymongo not found.")
    sys.exit(1)

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/enterprise_ai?authSource=admin")
DB_NAME = "enterprise_ai"

# This is what the frontend ALWAYS sends as X-Organization-Id
FRONTEND_ORG_ID = ObjectId("6732a1000000000000000001")

def fix():
    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    db = client[DB_NAME]

    try:
        db.command("ping")
        print("[+] MongoDB connected!")
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

    # 1. Show current state
    all_docs = list(db.uploaded_documents.find({}, {"fileName": 1, "organizationId": 1}))
    print(f"\n[*] Current uploaded_documents ({len(all_docs)} total):")
    for d in all_docs:
        print(f"    {d['fileName']} → orgId: {d.get('organizationId')}")

    if not all_docs:
        print("\n[!] No documents found. Run seed_rag_documents.py first!")
        client.close()
        return

    # 2. Update all documents to use frontend org ID
    result = db.uploaded_documents.update_many(
        {},
        {"$set": {"organizationId": FRONTEND_ORG_ID}}
    )
    print(f"\n[+] Updated {result.modified_count} documents → organizationId: {FRONTEND_ORG_ID}")

    # 3. Also fix organizations collection (upsert)
    existing_org = db.organizations.find_one({"_id": FRONTEND_ORG_ID})
    if not existing_org:
        # Check if any org exists
        any_org = db.organizations.find_one({})
        if any_org:
            # Update existing org to use frontend ID
            db.organizations.update_one(
                {"_id": any_org["_id"]},
                {"$set": {"_id": FRONTEND_ORG_ID}}
            )
            print(f"[+] Organization ID updated to match frontend: {FRONTEND_ORG_ID}")
        else:
            import datetime
            db.organizations.insert_one({
                "_id": FRONTEND_ORG_ID,
                "name": "Acme Global Enterprises",
                "code": "acme-corp",
                "domain": "acme.com",
                "status": "ACTIVE",
                "subscriptionTier": "ENTERPRISE",
                "createdAt": datetime.datetime.utcnow(),
                "updatedAt": datetime.datetime.utcnow()
            })
            print(f"[+] Created org with frontend ID: {FRONTEND_ORG_ID}")
    else:
        print(f"[+] Organization already has correct ID: {FRONTEND_ORG_ID}")

    # 4. Verify
    fixed_docs = list(db.uploaded_documents.find({"organizationId": FRONTEND_ORG_ID}, {"fileName": 1}))
    print(f"\n[SUCCESS] {len(fixed_docs)} documents now linked to frontend org ID:")
    for d in fixed_docs:
        print(f"    ✅ {d['fileName']}")

    client.close()
    print("\n[*] Done! Restart AI service and test RAG again.")

if __name__ == "__main__":
    fix()
