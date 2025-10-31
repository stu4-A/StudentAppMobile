# utils/matching.py

def recommend_opportunities(student, opportunities):
    """
    Recommends internship opportunities for a given student.
    
    - Uses both enrolled_subjects and skills from the student profile
    - Matches against opportunity fields (comma-separated)
    - Safely handles None or empty fields
    - Returns opportunities ranked by score (based on CGPA and location)
    """

    # --- Helper: convert CGPA to a weight ---
    def cgpa_weight(cgpa):
        if cgpa >= 4.0: return 1.0
        elif cgpa >= 3.5: return 0.9
        elif cgpa >= 3.0: return 0.8
        elif cgpa >= 2.5: return 0.6
        else: return 0.4

    # --- Step 1: Prepare student subjects and skills ---
    student_subjects = [
        s.strip().lower() for s in (student.enrolled_subjects or '').split(',') if s.strip()
    ]
    student_skills = [
        s.strip().lower() for s in (student.skills or '').split(',') if s.strip()
    ]
    student_keywords = student_subjects + student_skills

    if not student_keywords:
        # No subjects or skills; return empty list
        return []

    # --- Step 2: Filter opportunities by matching fields ---
    def matches_opportunity(opp):
        opp_fields = [f.strip().lower() for f in (getattr(opp, 'field', '') or '').split(',') if f.strip()]
        return any(keyword in opp_fields for keyword in student_keywords)

    matched_opportunities = list(filter(matches_opportunity, opportunities))

    if not matched_opportunities:
        return []

    # --- Step 3: Score opportunities ---
    def score(opp):
        base = cgpa_weight(getattr(student, 'cgpa', 0.0))

        # Optional: boost score if student and opportunity locations match
        student_loc = getattr(student, 'location', '')
        opp_loc = getattr(opp, 'location', '')
        if student_loc and opp_loc and student_loc.lower() == opp_loc.lower():
            base += 0.1

        # Optional: boost if opportunity has multiple fields matching student keywords
        opp_fields = [f.strip().lower() for f in (getattr(opp, 'field', '') or '').split(',') if f.strip()]
        match_count = sum(1 for k in student_keywords if k in opp_fields)
        base += 0.05 * match_count  # each match adds small boost

        return base

    scored_opportunities = [(opp, score(opp)) for opp in matched_opportunities]

    # --- Step 4: Sort opportunities by score descending ---
    sorted_opportunities = sorted(scored_opportunities, key=lambda x: x[1], reverse=True)

    # --- Step 5: Return only opportunity objects ---
    return [item[0] for item in sorted_opportunities]
