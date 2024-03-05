import json
import datetime
from fuzzywuzzy import fuzz


def calculate_score(candidate_cv, job_description):
    score = 0
    max_score = 0

    # Evaluate certifications
    required_certifications = job_description.get("certifications", [])
    if required_certifications:
        matched_certifications = candidate_cv.get("certifications", [])
        max_score += len(required_certifications)
        total_chars = sum(len(cert) for cert in required_certifications) * 0.8
        score += sum(
            1
            for job_cert in required_certifications
            if any(
                fuzz.token_sort_ratio(job_cert, candidate_cert) >= total_chars
                for candidate_cert in matched_certifications
            )
        ) / len(required_certifications)

    # Evaluate skills
    required_skills = {
        skill["skill_name"]: skill["yoe"] for skill in job_description.get("skills", [])
    }
    if required_skills:
        candidate_skills = {
            skill["skill_name"]: skill["yoe"]
            for skill in candidate_cv.get("skills", [])
        }
        max_score += len(required_skills)
        if required_skills:
            total_skill_score = sum(
                min(candidate_skills.get(skill_name, 0) / required_yoe, 1)
                for skill_name, required_yoe in required_skills.items()
            )
        score += total_skill_score

    # Evaluate education
    required_degrees = job_description.get("education", [])
    if required_degrees:
        candidate_degrees = [
            degree.get("edu_degree", "") for degree in candidate_cv.get("education", [])
        ]
        max_score += 1
        for required_degree in required_degrees:
            for candidate_degree in candidate_degrees:
                if fuzz.token_sort_ratio(required_degree, candidate_degree) >= 80:
                    score += 1
                    break

    # Evaluate years of experience
    required_experience = job_description.get("experience", {})
    if required_experience:
        current_year = datetime.datetime.now().year
        max_score += 1
        max_end_year = float("-inf")
        min_start_year = float("inf")
        for experience in candidate_cv.get("work_exp", []):
            timeline = experience.get("work_timeline")
            if isinstance(timeline, list) and len(timeline) == 2:
                start_year, end_year = timeline
                if not isinstance(end_year, int):
                    end_year = current_year
                min_start_year = min(min_start_year, start_year)
                max_end_year = max(max_end_year, end_year)
            elif isinstance(timeline, int):  # Handle single year
                min_start_year = min(min_start_year, timeline)
                max_end_year = max(max_end_year, timeline)

        if max_end_year != float("-inf") and min_start_year != float("inf"):
            years_of_experience = max_end_year - min_start_year
            if years_of_experience <= required_experience:
                score += years_of_experience / required_experience
            else:
                score += 1
    score = (10 / max_score) * score

    return score, max_score


def filter_candidates(candidate_cvs, job_description):
    qualified_candidates = []

    for candidate_cv in candidate_cvs:
        score, max_score = calculate_score(candidate_cv, job_description)
        if score >= 7:
            qualified_candidates.append((candidate_cv, score, max_score))

    qualified_candidates.sort(key=lambda x: x[1], reverse=True)

    return qualified_candidates


if __name__ == "__main__":
    # Example usage:

    candidate_cvs = json.loads(
        """
    [
    {
        "candidate_name": "John Doe",
        "candidate_title": "Software Engineer",
        "summary": "Experienced software engineer with a passion for creating efficient and scalable solutions.",
        "links": ["https://linkedin.com/in/johndoe"],
        "languages": [
        { "lang": "Vietnamese", "lang_lvl": "native" },
        { "lang": "English", "lang_lvl": "fluent" }
        ],
        "work_exp": [
        {
            "work_timeline": [2018, 2023],
            "work_company": "TechCorp",
            "work_title": "Senior Software Engineer",
            "work_responsibilities": [
                "Designed and implemented new features",
                "Optimized existing codebase for performance improvements",
                "Mentored junior developers"
            ],
            "technologies": "ReAct, Git, Python, Javascript, SQL",
            "work_description": "Led a team of developers in designing and implementing critical features for the flagship product."
        },
        {
            "work_timeline": [2015, 2018],
            "work_company": "CodeCrafters",
            "work_title": "Software Engineer",
            "work_responsibilities": [
                "Developed and maintained backend services",
                "Collaborated with UX/UI designers for front-end development"
            ],
            "technologies": "Canvas, Figma, CSS, HTML",
            "work_description": "Collaborated with cross-functional teams to deliver high-quality software solutions."
        }
        ],
        "education": [
        {
            "edu_timeline": [2011, 2015],
            "edu_school": "University of Tech",
            "edu_degree": "Bachelor of Science in Computer Science",
            "edu_gpa": 3.8,
            "edu_description": "Graduated with honors"
        }
        ],
        "projects": [
        {
            "project_timeline": [2020, 2021],
            "project_name": "Mobile Expense Tracker App",
            "project_responsibilities": [
                "Safeguard user information through encryption",
                "Design an intuitive and accessible interface",
                "Enable reliable data access across devices"
            ],
            "project_technologies": "CSS, HTML, Git, Javascript",
            "project_description": "Designed and developed a mobile app for tracking personal expenses."
        }
        ],
        "certifications": [
            "IELTS 9.0",
            "2023: PMI Agile Certified Practitioner"
        ],
        "skills": [
            { "skill_name": "JavaScript", "yoe": 5 },
            { "skill_name": "React", "yoe": 3 }
        ]
    }
    ]
    """
    )

    job_description = json.loads(
        """
    {
        "certifications": [
            "PMI Agile Certified Practitioner"
        ],
        "skills": [
            { "skill_name": "JavaScript", "yoe": 3 },
            { "skill_name": "React", "yoe": 2 }
        ],
        "education": [
        {
            "edu_degree": "Bachelor of Marketing in International Business",
            "edu_degree": "Bachelor of Science in Computer Science"
        }
        ],
        "experience": 10
    }
    """
    )

    qualified_candidates = filter_candidates(candidate_cvs, job_description)
    print("Qualified candidates:")
    for candidate, score, max_score in qualified_candidates:
        print(f"{candidate['candidate_name']} - Score: {score}/10.0")
