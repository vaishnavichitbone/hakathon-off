from datetime import date
from sqlalchemy.orm import Session
from ..models import StudentProfile, Opportunity
from typing import List, Dict, Any

def get_list_from_csv(csv_str: str) -> List[str]:
    if not csv_str:
        return []
    return [item.strip().lower() for item in csv_str.split(",") if item.strip()]

def calculate_match(student: StudentProfile, opportunity: Opportunity) -> Dict[str, Any]:
    # Default minimum match
    score = 0
    matched_skills = []
    missing_skills = []
    matched_interests = []
    matched_category = False

    # 1. Skill Match (40%)
    student_skills = get_list_from_csv(student.skills)
    opp_skills = get_list_from_csv(opportunity.required_skills)
    
    if opp_skills:
        skill_match_count = 0
        for skill in opp_skills:
            if skill in student_skills:
                skill_match_count += 1
                matched_skills.append(skill.title())
            else:
                missing_skills.append(skill.title())
                
        skill_score = (skill_match_count / len(opp_skills)) * 40
        score += skill_score
    else:
        score += 40 # If no skills required, full skill points

    # 2. Interest/Category Match (25%)
    student_interests = get_list_from_csv(student.interests)
    student_pref_cats = get_list_from_csv(student.preferred_categories)
    opp_category = opportunity.category.lower() if opportunity.category else ""
    
    cat_interest_score = 0
    if opp_category in student_pref_cats:
        cat_interest_score += 15
        matched_category = True
        
    # Check if any interests match description or category
    for interest in student_interests:
        if opportunity.description and interest in opportunity.description.lower():
            if interest not in matched_interests:
                matched_interests.append(interest.title())
                cat_interest_score += 10
                break # Cap at 10 points for interests
                
    score += min(cat_interest_score, 25)

    # 3. Education/Degree Match (15%)
    edu_score = 0
    if student.education and student.education.lower() in (opportunity.eligibility or "").lower():
        edu_score += 7.5
    if student.degree and student.degree.lower() in (opportunity.eligibility or "").lower():
        edu_score += 7.5
    # Simplification: give partial points if eligibility is empty or student fields are empty but they have some profile
    if not opportunity.eligibility:
        edu_score = 15
    score += edu_score

    # 4. Year/Eligibility Match (10%)
    year_score = 0
    if student.year and student.year.lower() in (opportunity.eligibility or "").lower():
        year_score = 10
    elif not opportunity.eligibility:
        year_score = 10
    score += year_score

    # 5. Location/Mode Preference (10%)
    loc_score = 0
    if student.preferred_mode and opportunity.mode:
        if student.preferred_mode.lower() in opportunity.mode.lower():
            loc_score += 5
    if student.preferred_location and opportunity.location:
        if student.preferred_location.lower() in opportunity.location.lower() or "remote" in opportunity.location.lower():
            loc_score += 5
    # Default points if not specified
    if not opportunity.mode: loc_score += 5
    if not opportunity.location: loc_score += 5
    score += loc_score

    # Normalize between 0 and 100
    final_score = min(max(round(score), 0), 100)
    
    # Calculate Priority
    priority = "LOW PRIORITY"
    days_remaining = None
    if opportunity.deadline:
        days_remaining = (opportunity.deadline - date.today()).days
    
    if final_score >= 80:
        if days_remaining is not None and days_remaining <= 14:
            priority = "HIGH PRIORITY"
        else:
            priority = "MEDIUM PRIORITY"
    elif final_score >= 60:
        priority = "MEDIUM PRIORITY"

    return {
        "match_score": final_score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "matched_interests": matched_interests,
        "matched_category": matched_category,
        "priority": priority,
        "days_remaining": days_remaining if days_remaining is not None and days_remaining >= 0 else None
    }
