from sqlalchemy.orm import Session

from .models import HCP

SEED_HCPS = [
    {"name": "Dr. John Smith", "specialty": "Cardiology", "hospital": "Apollo Hospitals", "email": "j.smith@apollo.example"},
    {"name": "Dr. Priya Rao", "specialty": "Endocrinology", "hospital": "Care Hospitals", "email": "p.rao@care.example"},
    {"name": "Dr. Michael Chen", "specialty": "Oncology", "hospital": "Yashoda Hospitals", "email": "m.chen@yashoda.example"},
    {"name": "Dr. Anitha Reddy", "specialty": "Neurology", "hospital": "KIMS Hospitals", "email": "a.reddy@kims.example"},
    {"name": "Dr. Robert Fernandez", "specialty": "Pulmonology", "hospital": "Continental Hospitals", "email": "r.fernandez@continental.example"},
]


def seed_hcps(db: Session) -> None:
    if db.query(HCP).count() > 0:
        return
    for row in SEED_HCPS:
        db.add(HCP(**row))
    db.commit()
