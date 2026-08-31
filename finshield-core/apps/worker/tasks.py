import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "api"))

from celery_app import celery_app
from db import SessionLocal
from models.case import Case
from graph.build_graph import build_case_graph

case_graph = build_case_graph()


@celery_app.task(name="run_case_pipeline")
def run_case_pipeline(case_id: str):
    db = SessionLocal()
    case = None
    try:
        case = db.query(Case).filter(Case.id == case_id).first()
        if not case:
            return {"error": f"case {case_id} not found"}

        case.status = "running"
        db.commit()

        case_graph.invoke({"case_id": case_id})

        case.status = "completed"
        db.commit()
        return {"case_id": case_id, "status": "completed"}
    except Exception as e:
        db.rollback()
        if case:
            case.status = "failed"
            db.commit()
        raise e
    finally:
        db.close()