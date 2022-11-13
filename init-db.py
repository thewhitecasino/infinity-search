from app import db, Candidate
import json

db.drop_all()
db.create_all()

with open("employee.json") as f:
    employee_data = json.load(f).get("employees")

    for i in employee_data:
        new_candidate = Candidate(skills=i.get("skills"), primary_skill=i.get("primary_skill"), name=i.get("name"),
                                  path_to_resume=i.get("path_to_resume"), resume_point=i.get("resume_point"))
        db.session.add(new_candidate)

    db.session.commit()
