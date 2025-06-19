import openai
from datetime import datetime
import os
from dotenv import load_dotenv
import json
import re
from typing import Dict, List, Optional, Tuple

class EnhancedInterviewAnalyzer:
    """향상된 인터뷰 분석기 - 모든 포지션에 대응 가능한 범용 분석"""
    
    def __init__(self, settings):
        """분석기 초기화"""
        self.settings = settings
        self.model = settings['gpt'].get('model', 'gpt-3.5-turbo')
        self.temperature = settings['gpt'].get('temperature', 0.3)  # 일관성을 위해 낮춤
        self.max_tokens = settings['gpt'].get('max_tokens', 2000)  # 증가
        
        load_dotenv()
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # 위치별 핵심 평가 영역 정의
        self.position_frameworks = {
            "HR": ["HR_Expertise", "Employee_Relations", "Compliance", "Strategic_Thinking", "Leadership", "Industry_Knowledge"],
            "CustomHR": ["HR Expertise", "Industry Background", "Leadership & Cultural Sensitivity", "Market Status & Reason for Interest & work timing", "Onsite & Salary Expectations"],
            "Engineering": ["Technical_Skills", "Problem_Solving", "System_Design", "Code_Quality", "Team_Collaboration", "Innovation"],
            "Sales": ["Sales_Performance", "Client_Relationship", "Market_Knowledge", "Negotiation", "Communication", "Results_Orientation"],
            "Marketing": ["Marketing_Strategy", "Digital_Marketing", "Analytics", "Creative_Thinking", "Brand_Management", "Campaign_Execution"],
            "Finance": ["Financial_Analysis", "Accounting", "Risk_Management", "Strategic_Planning", "Compliance", "Business_Acumen"],
            "Operations": ["Process_Optimization", "Quality_Management", "Supply_Chain", "Team_Leadership", "Problem_Solving", "Continuous_Improvement"],
            "General": ["Professional_Experience", "Leadership", "Communication", "Problem_Solving", "Cultural_Fit", "Career_Motivation"]
        }
        
    def extract_candidate_profile(self, interview_text: str, template: Dict) -> Dict:
        """Extract candidate basic information from interview text"""
        
        extraction_prompt = f"""
From the interview transcript below, identify the candidate's name and extract their information. The candidate is the person responding to the "Interviewer".

**Interview Transcript:**
---
{interview_text}
---

**Instructions:**
1.  Identify the candidate's full name. The candidate is the main speaker besides the "Interviewer".
2.  Extract the following details from the candidate's responses.
3.  If a piece of information is not mentioned, use "Not specified".
4.  Provide your response in a valid JSON format.

**JSON Output Format:**
{{
    "candidate_name": "Candidate's full name",
    "current_position": "Current job title",
    "current_company": "Current company",
    "target_position": "Applied position (infer from interview context)",
    "experience_years": "Total years of experience (if mentioned)",
    "education": "Educational background",
    "location_current": "Current location",
    "location_preference": "Preferred work location/relocation willingness",
    "availability": "Availability to start",
    "salary_current": "Current salary information",
    "salary_expectation": "Expected salary",
    "key_skills": ["List of key skills mentioned by the candidate"],
    "industry_background": "Industry background",
    "career_motivation": "Career motivation/goals"
}}
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert in accurately extracting candidate information from interview transcripts. Prioritize explicitly stated information, but include contextually clear inferences when available."},
                    {"role": "user", "content": extraction_prompt}
                ],
                temperature=0.1,  # Low temperature for accuracy
                max_tokens=1000
            )
            
            result = response.choices[0].message.content
            
            # JSON 파싱 시도
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                # JSON 파싱 실패시 기본값 반환
                return self._extract_basic_info_fallback(interview_text)
                
        except Exception as e:
            print(f"[EnhancedAnalyzer] 후보자 정보 추출 실패: {e}")
            return self._extract_basic_info_fallback(interview_text)
    
    def _extract_basic_info_fallback(self, text: str) -> Dict:
        """기본 정보 추출 실패시 폴백 방법"""
        # 간단한 정규식으로 기본 정보 추출 시도
        name_match = re.search(r'(?:I\'m|My name is|This is|Hi,?\s+I\'m)\s+([A-Z][a-z]+)', text)
        salary_match = re.search(r'\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:per hour|k|K|thousand)', text)
        company_match = re.search(r'(?:at|with|from)\s+([A-Z][a-zA-Z\s&]+(?:Inc|Corp|LLC|Company|Solutions|Logistics|Group)?)', text)
        
        return {
            "candidate_name": name_match.group(1) if name_match else "Not specified",
            "current_company": company_match.group(1) if company_match else "Not specified",
            "salary_expectation": f"${salary_match.group(1)}" if salary_match else "Not specified",
            "target_position": "Not specified",
            "experience_years": "Not specified",
            "location_preference": "Not specified"
        }
    
    def analyze_comprehensive_interview(self, interview_text: str, template: Dict, candidate_profile: Dict) -> Dict:
        """Comprehensive interview analysis - Position-specific evaluation"""
        
        # Determine position type
        position_type = self._determine_position_type(template.get('position', ''), interview_text)
        evaluation_areas = self.position_frameworks.get(position_type, self.position_frameworks["General"])
        
        analysis_prompt = f"""
You are an expert HR analyst. Your task is to analyze an interview transcript and create a structured summary based on a provided example.

**CRITICAL INSTRUCTIONS:**
1.  **Analyze ONLY the CANDIDATE's responses.** The candidate's name is "{candidate_profile.get('candidate_name', 'the candidate')}". Ignore the Interviewer's questions when extracting information.
2.  **Use the provided `evaluation_areas`** as the main categories for the analysis.
3.  **Follow the `JSON Output Format`** precisely. The output must be a valid JSON object.
4.  **Populate the `detailed_analysis` section** by summarizing the candidate's statements into bullet points for each relevant category.
5.  If no information is found for a category, state "No relevant information provided in the transcript." in the assessment.

---
**1. EXAMPLE OF A HIGH-QUALITY ANALYSIS**

**Sample Interview Transcript:**
```
Interviewer:
Hi Greg, thanks for taking the time to speak with us today. To start off, could you briefly introduce yourself and tell us about your current role?

Greg Goyer:
Sure, thank you. I'm currently an HR Manager at Kenco Logistics, overseeing HR operations across 4 sites and approximately 700 employees in 3 states. I directly manage 3 HR staff members. My responsibilities cover full-cycle HR operations, including payroll administration, HRIS data management, benefits coordination, and employee relations. I ensure compliance with EEOC, FMLA, OSHA, and internal policies through ongoing training, consistent reporting, and strict policy enforcement.

Interviewer:
I see you've also handled labor relations. Could you elaborate a bit more on your experience there?

Greg Goyer:
Absolutely. I've been fully responsible for labor relations, including union contract administration, resolving grievances, and leading successful contract negotiations. I've worked closely with union representatives and management to ensure productive labor partnerships and smooth operations.

Interviewer:
You've had experience in different industries. What draws you to the automotive sector, and specifically Hyundai Glovis?

Greg Goyer:
While I'm currently in the logistics sector, I have prior experience in automotive manufacturing and packaging, and the automotive industry has always been a core passion of mine. I'm especially drawn to Hyundai Glovis because of your strong reputation and commitment to progressive HR practices. I believe this role would allow me to combine my HR leadership skills with my enthusiasm for the industry, and contribute meaningfully to your organizational development goals.

Interviewer:
Tell us about your leadership style. How do you manage your team across multiple sites?

Greg Goyer:
I lead with transparency and consistency. I believe in empowering my team by giving them clear goals and the support they need to succeed. I currently manage 3 direct reports and work closely with VPs, Directors, and General Managers across sites. I make sure communication is proactive and that I'm accessible despite the distance. I'm also very comfortable working with diverse teams and leadership from various cultural and professional backgrounds.

Interviewer:
How do you stay on top of compliance and training in a high-volume, multi-state environment?

Greg Goyer:
It comes down to systems and discipline. I've developed and delivered training programs on compliance topics like harassment prevention, safety protocols, and labor relations. I ensure every site follows a consistent compliance calendar and I use data from our HRIS and internal audits to stay ahead of issues before they escalate.

Interviewer:
Where are you in your job search process, and what kind of timeline are you working with?

Greg Goyer:
I'm currently employed at Kenco Logistics but actively exploring opportunities that offer greater growth with less travel. If selected, I can provide a standard 2-3 week notice to ensure a smooth transition. I'm also prepared to relocate to Savannah with my spouse and am excited about the possibility of joining your team.

Interviewer:
Do you have any expectations around compensation or work structure?

Greg Goyer:
Yes, I'm comfortable with an onsite work structure. In terms of compensation, I'm looking for a base salary of at least $120K, with bonus potential being a consideration. That said, the opportunity itself is most important to me—especially one aligned with my values and industry passion.
```

**Sample JSON Output (This is your goal):**
```json
{{
    "executive_summary": "Greg Goyer is an experienced HR Manager with a strong background in full-cycle HR operations, labor relations, and compliance management within high-volume, multi-state environments. He demonstrates clear leadership capabilities and a passion for the automotive industry. He is actively seeking a growth opportunity with less travel and is prepared to relocate, targeting a base salary of at least $120K.",
    "detailed_analysis": {{
        "HR Expertise": {{
            "assessment": [
                "At Kenco, oversaw full-cycle HR operations for high-volume distribution centers, including payroll administration, HRIS data management, benefits coordination, and employee relations.",
                "Ensured compliance with EEOC, FMLA, OSHA, and internal policies through consistent training, reporting, and policy enforcement.",
                "Provided strategic HR support and guidance to managers and staff on performance management, discipline, and employee development.",
                "Designed and delivered training on compliance topics like harassment prevention, safety, and labor relations.",
                "Oversaw all aspects of labor relations, including union contract administration, grievance resolution, and successful contract negotiations."
            ]
        }},
        "Industry Background": {{
            "assessment": [
                "Currently in the logistics industry with prior experience in automotive manufacturing and packaging.",
                "Maintains a strong, long-term interest and passion for the automotive sector."
            ]
        }},
        "Leadership & Cultural Sensitivity": {{
            "assessment": [
                "Manages 3 direct reports and oversees 4 sites with 700 employees across 3 states.",
                "Collaborates with VPs, Directors, and General Managers.",
                "Comfortable working with diverse teams and leadership from various backgrounds."
            ]
        }},
        "Market Status & Reason for Interest & work timing": {{
            "assessment": [
                "Currently employed at Kenco Logistics.",
                "Seeking opportunities with greater professional growth and less travel.",
                "Interested in Hyundai Glovis due to its reputation and alignment with his passion for the automotive industry.",
                "Can provide a standard 2-3 week notice and is prepared to relocate to Savannah with his spouse."
            ]
        }},
        "Onsite & Salary Expectations": {{
            "assessment": [
                "Comfortable with an onsite work structure.",
                "Expects a base salary of at least $120K, with bonus potential as a consideration."
            ]
        }}
    }},
    "strengths": [
        "Extensive experience in full-cycle HR operations and compliance.",
        "Proven track record in labor relations and contract negotiation.",
        "Strong leadership skills in a multi-site environment.",
        "Clear motivation and passion for the automotive industry."
    ],
    "concerns": [
        "Current experience is in logistics, which may require some adaptation to the specifics of the automotive sector."
    ],
    "recommendation": {{
        "decision": "Recommend",
        "reasoning": "The candidate's extensive HR experience, leadership skills, and strong motivation make him a promising fit. His background in labor relations is a significant asset.",
        "next_steps": "Proceed with a second-round interview with the hiring manager."
    }}
}}
```
---

**🎯 CRITICAL WRITING GUIDELINES - USE DIVERSE SENTENCE STARTERS**

📝 **AVOID REPETITIVE PATTERNS** - Do not start every sentence with "Experienced in..." or similar phrases.

**DIVERSE SENTENCE STARTER TEMPLATES (use variety):**

💼 **Career & Role**: Has led/managed/overseen/directed/supported... | Served as... | Functioned as... | Previously worked in... | Held the position of... | Played a key role in... | Was responsible for... | Took ownership of...

⚙️ **Skills & Systems**: Demonstrated expertise in... | Proficient in using... | Skilled in handling... | Well-versed in... | Has utilized... | Hands-on experience with... | Administered... | Implemented and maintained...

📈 **Performance & Strategy**: Successfully implemented... | Consistently delivered results in... | Improved processes related to... | Streamlined operations by... | Achieved measurable outcomes in... | Spearheaded efforts to... | Played a critical role in optimizing...

📚 **Training & Compliance**: Designed and delivered training on... | Developed policies for... | Ensured compliance with... | Conducted workshops on... | Provided guidance on... | Established internal controls for...

🤝 **Collaboration**: Collaborated with... | Partnered with cross-functional teams to... | Built strong working relationships with... | Provided consultation to...

🧭 **Leadership Style**: Emphasized transparency in... | Fostered an inclusive work environment by... | Known for a collaborative leadership style... | Guided teams through...

🚀 **Projects & Initiatives**: Launched initiatives focused on... | Led cross-functional projects to... | Drove transformation in... | Coordinated multi-site rollouts of...

⚡ **SPECIFIC NUMBERS**: Use exact numbers when mentioned (e.g., "3-year" instead of "multi-year", "70+ employees" instead of "many employees")

**EXAMPLES OF GOOD VARIATIONS:**
✅ "Has managed payroll operations for 70+ employees across 4 sites"
✅ "Successfully implemented HRIS systems resulting in 30% efficiency improvement"  
✅ "Led 3-year compliance initiative covering EEOC and FMLA regulations"
✅ "Collaborated with union representatives to achieve productive labor partnerships"
✅ "Designed and delivered training programs on harassment prevention"

❌ **AVOID REPETITIVE STARTS:**
❌ "Experienced in payroll management..."
❌ "Experienced in compliance..."  
❌ "Experienced in training..."

---
**4. YOUR TASK**

**Candidate Profile:**
- Name: {candidate_profile.get('candidate_name', 'Not specified')}
- Current Company: {candidate_profile.get('current_company', 'Not specified')}
- Current Position: {candidate_profile.get('current_position', 'Not specified')}
- Target Position: {template.get('position', 'Not specified')}

**Interview Transcript to Analyze:**
```
{interview_text}
```

**Evaluation Areas (Categories):**
{evaluation_areas}

**JSON Output Format:**
```json
{{
    "executive_summary": "3-4 sentence summary of the candidate (strengths, fit, major concerns).",
    "detailed_analysis": {{
        "Category 1 from Evaluation Areas": {{
            "assessment": ["Bulleted list of key points from candidate's response."]
        }},
        "Category 2 from Evaluation Areas": {{
            "assessment": ["Bulleted list of key points from candidate's response."]
        }}
    }},
    "strengths": ["List 3-5 key strengths based on the analysis."],
    "concerns": ["List 2-3 potential concerns or areas for improvement."],
    "recommendation": {{
        "decision": "Highly Recommend/Recommend/Consider/Not Recommend",
        "reasoning": "Briefly explain the recommendation decision.",
        "next_steps": "Suggest concrete next steps (e.g., technical interview, team interview)."
    }}
}}
```

**🎯 CRITICAL WRITING GUIDELINES - USE DIVERSE SENTENCE STARTERS**

📝 **AVOID REPETITIVE PATTERNS** - Do not start every sentence with "Experienced in..." or similar phrases.

**DIVERSE SENTENCE STARTER TEMPLATES (use variety):**

💼 **Career & Role**: Has led/managed/overseen/directed/supported... | Served as... | Functioned as... | Previously worked in... | Held the position of... | Played a key role in... | Was responsible for... | Took ownership of...

⚙️ **Skills & Systems**: Demonstrated expertise in... | Proficient in using... | Skilled in handling... | Well-versed in... | Has utilized... | Hands-on experience with... | Administered... | Implemented and maintained...

📈 **Performance & Strategy**: Successfully implemented... | Consistently delivered results in... | Improved processes related to... | Streamlined operations by... | Achieved measurable outcomes in... | Spearheaded efforts to... | Played a critical role in optimizing...

📚 **Training & Compliance**: Designed and delivered training on... | Developed policies for... | Ensured compliance with... | Conducted workshops on... | Provided guidance on... | Established internal controls for...

🤝 **Collaboration**: Collaborated with... | Partnered with cross-functional teams to... | Built strong working relationships with... | Provided consultation to...

🧭 **Leadership Style**: Emphasized transparency in... | Fostered an inclusive work environment by... | Known for a collaborative leadership style... | Guided teams through...

🚀 **Projects & Initiatives**: Launched initiatives focused on... | Led cross-functional projects to... | Drove transformation in... | Coordinated multi-site rollouts of...

⚡ **SPECIFIC NUMBERS**: Use exact numbers when mentioned (e.g., "3-year" instead of "multi-year", "70+ employees" instead of "many employees")

**EXAMPLES OF GOOD VARIATIONS:**
✅ "Has managed payroll operations for 70+ employees across 4 sites"
✅ "Successfully implemented HRIS systems resulting in 30% efficiency improvement"  
✅ "Led 3-year compliance initiative covering EEOC and FMLA regulations"
✅ "Collaborated with union representatives to achieve productive labor partnerships"
✅ "Designed and delivered training programs on harassment prevention"

❌ **AVOID REPETITIVE STARTS:**
❌ "Experienced in payroll management..."
❌ "Experienced in compliance..."  
❌ "Experienced in training..."
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": f"You are a specialized {position_type} recruitment analyst. Your task is to produce a comprehensive candidate evaluation in a structured JSON format, based *only* on the candidate's statements in the provided transcript."},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.2, # Lower temperature for consistency
                max_tokens=self.max_tokens,
                response_format={ "type": "json_object" } # Enforce JSON output
            )
            
            result = response.choices[0].message.content
            
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                # JSON 파싱 실패시 텍스트 형태로라도 반환
                return {
                    "executive_summary": "Analysis completed but formatting error occurred",
                    "raw_analysis": result,
                    "error": "JSON parsing failed"
                }
                
        except Exception as e:
            print(f"[EnhancedAnalyzer] Comprehensive analysis failed: {e}")
            return {
                "error": f"Analysis failed: {str(e)}",
                "executive_summary": "An error occurred during analysis."
            }
    
    def _determine_position_type(self, position_title: str, interview_text: str) -> str:
        """Determine position type"""
        position_lower = position_title.lower()
        text_lower = interview_text.lower()
        
        # Keyword-based position classification
        if any(keyword in position_lower for keyword in ['hr', 'human resources', 'people', 'talent']):
            return "CustomHR"
        elif any(keyword in position_lower for keyword in ['engineer', 'developer', 'technical', 'software']):
            return "Engineering"
        elif any(keyword in position_lower for keyword in ['sales', 'account', 'business development']):
            return "Sales"
        elif any(keyword in position_lower for keyword in ['marketing', 'brand', 'digital', 'campaign']):
            return "Marketing"
        elif any(keyword in position_lower for keyword in ['finance', 'accounting', 'financial', 'controller']):
            return "Finance"
        elif any(keyword in position_lower for keyword in ['operations', 'supply chain', 'logistics', 'manufacturing']):
            return "Operations"
        
        # Additional classification attempt based on interview content
        if any(keyword in text_lower for keyword in ['payroll', 'benefits', 'employee relations', 'compliance', 'eeoc']):
            return "CustomHR"
        elif any(keyword in text_lower for keyword in ['code', 'programming', 'system', 'architecture', 'database']):
            return "Engineering"
        
        return "General"
    
    def improve_screening_notes(self, current_notes: Dict, interview_text: str, template: Dict) -> Dict:
        """Improve existing screening notes"""
        
        improvement_prompt = f"""
Please improve the existing screening notes based on the complete interview transcript:

【CURRENT SCREENING NOTES】
{json.dumps(current_notes, indent=2, ensure_ascii=False)}

【COMPLETE INTERVIEW TRANSCRIPT】
{interview_text}

【IMPROVEMENT OBJECTIVES】
1. Add missing important information
2. Clarify incomplete or ambiguous content
3. Balance coverage across categories
4. Enhance accuracy and completeness

Please provide improved notes in the following format:

{{
    "improved_categories": {{
        "category_name": {{
            "original": "Original content",
            "improved": "Improved content",
            "additions": ["Newly added information"],
            "rationale": "Reason for improvement"
        }}
    }},
    "missing_categories": {{
        "category_name": {{
            "content": "Newly discovered category content",
            "importance": "High/Medium/Low",
            "rationale": "Reason for addition"
        }}
    }},
    "overall_improvement": {{
        "completeness_score": "1-10 scale (after improvement)",
        "key_improvements": ["Major improvement points"],
        "remaining_gaps": ["Areas still needing attention"]
    }}
}}
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a screening notes quality improvement specialist. Your goal is to identify missing information, clarify ambiguous expressions, and enhance overall completeness."},
                    {"role": "user", "content": improvement_prompt}
                ],
                temperature=0.2,
                max_tokens=1500
            )
            
            result = response.choices[0].message.content
            
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                return {"error": "Improvement analysis failed - JSON parsing error", "raw_result": result}
                
        except Exception as e:
            print(f"[EnhancedAnalyzer] Screening notes improvement failed: {e}")
            return {"error": f"Improvement failed: {str(e)}"}
    
    def generate_final_report(self, candidate_profile: Dict, comprehensive_analysis: Dict, 
                            improved_screening: Dict, interview_text: str, template: Dict) -> str:
        """Generate final comprehensive report"""
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Generate report structure
        report_sections = []
        
        # 1. Header
        report_sections.append("=" * 80)
        report_sections.append("🎯 COMPREHENSIVE INTERVIEW ASSESSMENT REPORT")
        report_sections.append("=" * 80)
        report_sections.append("")
        
        # 2. Candidate information
        report_sections.append("👤 CANDIDATE PROFILE")
        report_sections.append("-" * 40)
        report_sections.append(f"Name: {candidate_profile.get('candidate_name', 'Not specified')}")
        report_sections.append(f"Target Position: {template.get('position', candidate_profile.get('target_position', 'Not specified'))}")
        report_sections.append(f"Current Role: {candidate_profile.get('current_position', 'Not specified')}")
        report_sections.append(f"Current Company: {candidate_profile.get('current_company', 'Not specified')}")
        report_sections.append(f"Experience: {candidate_profile.get('experience_years', 'Not specified')}")
        report_sections.append(f"Location: {candidate_profile.get('location_current', 'Not specified')} → {candidate_profile.get('location_preference', 'Not specified')}")
        report_sections.append(f"Salary Expectation: {candidate_profile.get('salary_expectation', 'Not specified')}")
        report_sections.append(f"Assessment Date: {timestamp}")
        report_sections.append("")
        
        # 3. Executive summary
        if 'executive_summary' in comprehensive_analysis:
            report_sections.append("📋 EXECUTIVE SUMMARY")
            report_sections.append("-" * 40)
            report_sections.append(comprehensive_analysis['executive_summary'])
            report_sections.append("")
        
        # 4. Detailed analysis
        if 'detailed_analysis' in comprehensive_analysis:
            report_sections.append("📊 DETAILED ASSESSMENT")
            report_sections.append("-" * 40)
            for area, analysis in comprehensive_analysis['detailed_analysis'].items():
                report_sections.append(f"▼ {area.replace('_', ' ').title()}")
                # Use 'assessment' which is now a list of strings
                if analysis.get('assessment'):
                    for point in analysis['assessment']:
                        report_sections.append(f"   • {point}")
                else:
                    report_sections.append(f"   • {analysis.get('assessment', 'No assessment provided')}")
                report_sections.append("")
        
        # 5. Strengths and concerns
        if 'strengths' in comprehensive_analysis or 'concerns' in comprehensive_analysis:
            report_sections.append("⚖️ STRENGTHS & CONCERNS")
            report_sections.append("-" * 40)
            
            if comprehensive_analysis.get('strengths'):
                report_sections.append("✅ Key Strengths:")
                for strength in comprehensive_analysis['strengths']:
                    report_sections.append(f"   • {strength}")
                report_sections.append("")
            
            if comprehensive_analysis.get('concerns'):
                report_sections.append("⚠️ Areas of Concern:")
                for concern in comprehensive_analysis['concerns']:
                    report_sections.append(f"   • {concern}")
                report_sections.append("")
        
        # 6. Final recommendation
        if 'recommendation' in comprehensive_analysis:
            rec = comprehensive_analysis['recommendation']
            report_sections.append("🎯 FINAL RECOMMENDATION")
            report_sections.append("-" * 40)
            report_sections.append(f"Decision: {rec.get('decision', 'Not specified')}")
            report_sections.append(f"Reasoning: {rec.get('reasoning', 'No reasoning provided')}")
            report_sections.append(f"Next Steps: {rec.get('next_steps', 'No next steps specified')}")
            report_sections.append("")
        
        # 7. Cultural fit
        if 'cultural_fit' in comprehensive_analysis:
            cultural = comprehensive_analysis['cultural_fit']
            report_sections.append("🤝 CULTURAL FIT ASSESSMENT")
            report_sections.append("-" * 40)
            report_sections.append(f"Rating: {cultural.get('rating', 'N/A')}/5")
            report_sections.append(f"Reasoning: {cultural.get('reasoning', 'No assessment provided')}")
            report_sections.append("")
        
        # 8. Interview quality metadata
        if 'interview_quality' in comprehensive_analysis:
            quality = comprehensive_analysis['interview_quality']
            report_sections.append("📈 INTERVIEW QUALITY METRICS")
            report_sections.append("-" * 40)
            report_sections.append(f"Interview Depth: {quality.get('depth', 'N/A')}/5")
            report_sections.append(f"Topic Coverage: {quality.get('coverage', 'N/A')}/5")
            if quality.get('notes'):
                report_sections.append(f"Notes: {quality['notes']}")
            report_sections.append("")
        
        # 9. Footer
        report_sections.append("=" * 80)
        report_sections.append("Report generated by Rec Chart OCR - Enhanced Interview Analysis System")
        report_sections.append(f"Analysis completed at {timestamp}")
        report_sections.append("=" * 80)
        
        return '\n'.join(report_sections) 