#!/usr/bin/env python3
"""
Fix: Remove old duplicate docs + fix allowedRoles for CONFIDENTIAL documents
"""
import os, sys
from bson import ObjectId
from pymongo import MongoClient

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/enterprise_ai?authSource=admin")
client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
db = client["enterprise_ai"]

print("[+] Connected to MongoDB")

# 1. Show all current docs
docs = list(db.uploaded_documents.find({}, {"fileName": 1, "classification": 1, "allowedRoles": 1}))
print(f"\n[*] Current docs ({len(docs)}):")
for d in docs:
    print(f"    {d['fileName']} | {d.get('classification')} | roles: {d.get('allowedRoles')}")

# 2. Delete OLD duplicate docs (without _2026 in name) - these have wrong allowedRoles
old_names = [
    "Microservices_Architecture_and_SLA.docx",
    "Q3_Confidential_Financial_Budget_Allocations.pdf",
    "Acme_HR_Policy_and_Benefits_2026.pdf"  # keep only _2026 versions
]

# Delete specifically old non-2026 Finance and Tech docs
deleted = db.uploaded_documents.delete_many({
    "fileName": {"$in": [
        "Microservices_Architecture_and_SLA.docx",
        "Q3_Confidential_Financial_Budget_Allocations.pdf"
    ]}
})
print(f"\n[+] Deleted {deleted.deleted_count} old duplicate documents")

# 3. Fix allowedRoles for CONFIDENTIAL Finance doc
result = db.uploaded_documents.update_many(
    {"fileName": {"$regex": "Financial_Budget", "$options": "i"}},
    {"$set": {
        "classification": "CONFIDENTIAL",
        "allowedRoles": ["MANAGER", "ORG_ADMIN", "SUPER_ADMIN"]
    }}
)
print(f"[+] Fixed Finance doc allowedRoles: {result.modified_count} updated → MANAGER+ only")

# 4. Fix HR and Tech docs - INTERNAL (all roles)
result2 = db.uploaded_documents.update_many(
    {"fileName": {"$regex": "HR_Policy|SLA", "$options": "i"}},
    {"$set": {
        "classification": "INTERNAL",
        "allowedRoles": ["EMPLOYEE", "MANAGER", "ORG_ADMIN", "SUPER_ADMIN"]
    }}
)
print(f"[+] Fixed HR/SLA doc allowedRoles: {result2.modified_count} updated → All roles")

# 5. Final state
print("\n[*] Final document state:")
for d in db.uploaded_documents.find({}, {"fileName": 1, "classification": 1, "allowedRoles": 1}):
    print(f"    ✅ {d['fileName']}")
    print(f"       Classification: {d.get('classification')} | Roles: {d.get('allowedRoles')}")

client.close()
print("\n[SUCCESS] RBAC fixed! Restart AI service now.")
