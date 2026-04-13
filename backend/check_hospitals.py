from pymongo import MongoClient

db = MongoClient('mongodb://localhost:27017/')['triage_system']
hospitals = list(db.hospitals.find({}, {'hospital_id': 1, 'hospital_name': 1, '_id': 0}).limit(5))
for h in hospitals:
    print(f"{h['hospital_id']}: {h['hospital_name']}")
