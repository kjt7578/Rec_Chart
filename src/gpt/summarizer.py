import openai
from datetime import datetime
import os
from dotenv import load_dotenv
import json
from typing import Optional, Dict

class GPTSummarizer:
    """GPT 기반 텍스트 요약 클래스"""
    
    def __init__(self, settings):
        """
        GPT 요약기 초기화
        
        Args:
            settings (dict): GPT 설정
        """
        self.settings = settings
        self.model = settings['gpt']['model']
        self.temperature = settings['gpt']['temperature']
        self.max_tokens = settings['gpt']['max_tokens']
        
        # OpenAI API 키 로드
        load_dotenv()
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Enhanced Analyzer 초기화
        try:
            from .enhanced_analyzer import EnhancedInterviewAnalyzer
            self.enhanced_analyzer = EnhancedInterviewAnalyzer(settings)
            print("[GPTSummarizer] Enhanced Analyzer 초기화 완료")
        except ImportError as e:
            print(f"[GPTSummarizer] Enhanced Analyzer 초기화 실패: {e}")
            self.enhanced_analyzer = None
        
    def summarize(self, text):
        """
        텍스트 요약 수행
        
        Args:
            text (str): 요약할 텍스트
            
        Returns:
            dict: 요약 결과
        """
        if not text.strip():
            print('[GPTSummarizer] 입력 텍스트가 비어 있음')
            return {}
        
        try:
            print('[GPTSummarizer] OpenAI API 호출 시작')
            # GPT 프롬프트 구성 (사용자 제안에 따라 개선)
            prompt = f"""다음 후보자 프로필을 아래 항목에 중점을 두어 요약해 주세요:

{text}

요약 중점 사항:
1. 기술적 HR 전문성
2. 전략적 및 리더십 자질
3. 산업에 대한 관심과 장기적인 동기
4. 문화 적합성 및 협업 스타일

단순한 업무 나열을 피하고, 경력 이동과 직무에 대한 관심 이면에 있는 *이유*를 파악해 주세요."""

            # GPT API 호출
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "당신은 채용 관리자를 위해 후보자 프로필에 대한 통찰력 있고 사람이 읽기 쉬운 요약 보고서를 작성하는 전문 HR 분석가입니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            print('[GPTSummarizer] OpenAI API 호출 성공')
            
            # 응답 파싱
            summary_text = response.choices[0].message.content
            
            # 결과 구조화
            result = {
                'timestamp': datetime.now().isoformat(),
                'text_length': len(text),
                'summary': summary_text
            }
            
            # 주요 포인트와 키워드 추출
            lines = summary_text.split('\n')
            main_points = []
            keywords = []
            
            for line in lines:
                line = line.strip()
                if line.startswith('- '):
                    main_points.append(line[2:])
                elif line.startswith('키워드:'):
                    keywords = [k.strip() for k in line[6:].split(',')]
                    
            result['main_points'] = main_points
            result['keywords'] = keywords
            
            return result
            
        except Exception as e:
            print(f'[GPTSummarizer] OpenAI API 호출 실패: {e}')
            # API 키 오류 등 예외 발생 시 안내 메시지 반환
            return {'summary': f'요약 실패: OpenAI API 키를 확인하거나 네트워크 상태를 점검하세요.\n에러: {str(e)}'}
            
    def set_model(self, model):
        """GPT 모델 설정"""
        self.model = model
        
    def set_temperature(self, temperature):
        """생성 온도 설정"""
        self.temperature = temperature
        
    def set_max_tokens(self, max_tokens):
        """최대 토큰 수 설정"""
        self.max_tokens = max_tokens 

    def analyze_interview_and_get_summary(self, interview_text: str, template: Optional[Dict] = None) -> Dict:
        """
        향상된 분석기를 사용하여 인터뷰를 분석하고, 최종 리포트를 포함한 전체 분석 결과 반환
        """
        if not self.enhanced_analyzer:
            print("[GPTSummarizer] Enhanced Analyzer가 초기화되지 않았습니다. 기본 요약을 수행합니다.")
            return self.summarize(interview_text)

        if template is None:
            template = {}

        try:
            print("[GPTSummarizer] Enhanced Analyzer를 사용하여 전체 인터뷰 분석 시작...")
            
            # Enhanced Analyzer의 분석 파이프라인 호출
            analysis_result = self.analyze_complete_interview(
                interview_script=interview_text,
                template=template,
                screening_data={}  # 초기 스크리닝 데이터는 비어있음
            )
            
            print("[GPTSummarizer] 전체 인터뷰 분석 완료.")
            return analysis_result

        except Exception as e:
            print(f"[GPTSummarizer] 전체 인터뷰 분석 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()
            # 실패 시 기본 요약으로 대체
            return self.summarize(interview_text)

    def summarize_incremental(self, incremental_prompt):
        """
        증분 요약: 사용자 커스텀 가이드라인 기반 스크리닝 노트 생성
        (향후 이 기능도 Enhanced Analyzer로 통합 고려)
        """
        try:
            # 새로운 텍스트만 추출
            lines = incremental_prompt.split('\n')
            new_text = ""
            for line in lines:
                if line.startswith('새로 추가된 내용:'):
                    new_text = '\n'.join(lines[lines.index(line)+1:])
                    break
            
            if not new_text.strip():
                return {"summary": "새로운 내용이 없습니다.", "key_points": []}
            
            # 커스텀 가이드라인 기반 프롬프트
            custom_prompt = f"""
The following is newly mentioned content from an interview:

{new_text}

📘 **Please organize according to Screening Note Summary Guideline v2.0:**

**🎯 Select only relevant categories from the 9 core categories:**
1. **Work Experience**: Total years of experience, job titles, company names, relevant industry
2. **Technical Skills**: Systems, platforms, tools, certifications, real-world usage
3. **Project/Achievements**: Specific projects led/participated in, problems solved, outcomes achieved
4. **Industry Expertise**: Industry or product domain familiarity
5. **Global/Cultural Exposure**: Cross-country/regional collaboration, Korean or multinational team experience
6. **Job Motivation/Fit**: Interest in company/position, career alignment
7. **Relocation/Work Mode**: Current location, relocation willingness, onsite/remote preference
8. **Availability**: Current employment status, possible start date
9. **Compensation**: Previous compensation, salary expectations, bonus information

**📝 Few-Shot Learning Examples:**

**Example 1:**
Input: "I have been working at Johnson & Johnson for 13 years in payroll management and HR systems."
Output: {{"category": "Work Experience", "note": "13+ years of payroll management and HR systems experience at Johnson & Johnson."}}

**Example 2:**
Input: "I'm experienced with SAP SuccessFactors, Workday, and I have certifications in Project Management."
Output: {{"category": "Technical Skills", "note": "Hands-on with SAP SuccessFactors and Workday; certified in Project Management."}}

**Example 3:**
Input: "I led a major integration project that reduced processing time by 30% and solved data mapping issues."
Output: {{"category": "Project/Achievements", "note": "Led integration project reducing processing time by 30% and resolving data mapping issues."}}

**Example 4:**
Input: "I work with teams from LATAM, EMEA, and APAC. I'm comfortable with Korean leadership."
Output: {{"category": "Global/Cultural Exposure", "note": "Collaborated with LATAM, EMEA, and APAC teams; comfortable working with Korean leadership."}}

**Example 5:**
Input: "My last salary was $53.26 per hour. I'm looking for around $120K base salary."
Output: {{"category": "Compensation", "note": "Last comp: $53.26/hour; targeting $120K base salary."}}

**📋 Sentence Construction Principles:**
- Be specific (avoid vague terms without context)
- Include numeric values whenever possible (years, salary, team size, etc.)
- Avoid repeating the same content
- Do not abbreviate key technical terms (e.g., always write "SAP SuccessFactors" in full)
- One sentence per key idea

**If the content is not important or not applicable, respond with "Not Applicable".**

Please respond in JSON format:
{{
    "category": "Category name (one of the 9 above, or 'Not Applicable')",
    "note": "One sentence summary following guidelines (empty string if not applicable)",
    "summary": "Complete screening note"
}}
"""
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": """You are a professional Screening Note specialist trained on Screening Note Summary Guideline v2.0 for English interviews. 

Your expertise:
- Creating structured, specific, and numeric-rich summaries in professional English
- Following exact sentence construction principles for enterprise recruitment
- Using recommended templates for consistency across all candidates
- Avoiding vague or abstract language in favor of concrete details
- Ensuring technical terms are accurate and complete (no abbreviations)
- Focusing on English interview context and North American business standards

You MUST follow the provided guidelines exactly and produce professional-quality screening notes that meet enterprise recruitment standards for English-speaking candidates."""},
                    {"role": "user", "content": custom_prompt}
                ],
                max_tokens=800,
                temperature=0.1  # 매우 일관성 있는 결과
            )
            
            result = response.choices[0].message.content.strip()
            
            # JSON 파싱 시도
            try:
                summary_json = json.loads(result)
                return summary_json
            except json.JSONDecodeError:
                # JSON 파싱 실패 시 기본 형식으로 변환
                return {
                    "category": "Other",
                    "note": result,
                    "summary": result
                }
                
        except Exception as e:
            print(f"Custom guideline-based processing failed: {e}")
            return {
                "category": "Error",
                "note": f"Processing failed: {str(e)}",
                "summary": "Unable to process content."
            } 

    def generate_screening_note_with_speaker(self, conversation_text, interviewer_name):
        """화자 구분이 포함된 대화에서 스크리닝 노트 생성"""
        try:
            # 화자 구분 기반 프롬프트
            speaker_aware_prompt = f"""
The following is a conversation from an English interview where "{interviewer_name}" is the interviewer:

{conversation_text}

📘 **Please organize according to Screening Note Summary Guideline v2.0:**

**🚨 CRITICAL INSTRUCTION: Only extract information from CANDIDATE responses. 
Interviewer statements provide context but should NEVER be included in the candidate's background/experience.**

**🎯 Select only relevant categories from the 9 core categories:**
1. **Work Experience**: Total years of experience, job titles, company names, relevant industry
2. **Technical Skills**: Systems, platforms, tools, certifications, real-world usage
3. **Project/Achievements**: Specific projects led/participated in, problems solved, outcomes achieved
4. **Industry Expertise**: Industry or product domain familiarity
5. **Global/Cultural Exposure**: Cross-country/regional collaboration, Korean or multinational team experience
6. **Job Motivation/Fit**: Interest in company/position, career alignment
7. **Relocation/Work Mode**: Current location, relocation willingness, onsite/remote preference
8. **Availability**: Current employment status, possible start date
9. **Compensation**: Previous compensation, salary expectations, bonus information

**📝 Few-Shot Learning Examples:**

**Example 1:**
Conversation:
{interviewer_name}: Tell me about your experience with payroll systems.
Candidate: I have been working at Johnson & Johnson for 13 years in payroll management and HR systems.

Output: {{"category": "Work Experience", "note": "13+ years of payroll management and HR systems experience at Johnson & Johnson."}}

**Example 2:**
Conversation:
{interviewer_name}: What tools have you worked with?
Candidate: I'm experienced with SAP SuccessFactors, Workday, and I have certifications in Project Management.

Output: {{"category": "Technical Skills", "note": "Hands-on with SAP SuccessFactors and Workday; certified in Project Management."}}

**📋 Sentence Construction Principles:**
- Extract ONLY from candidate responses, never from interviewer statements
- Be specific (avoid vague terms without context)
- Include numeric values whenever possible (years, salary, team size, etc.)
- Avoid repeating the same content
- Do not abbreviate key technical terms (e.g., always write "SAP SuccessFactors" in full)
- One sentence per key idea

**If the candidate content is not important or not applicable, respond with "Not Applicable".**

Please respond in JSON format:
{{
    "category": "Category name (one of the 9 above, or 'Not Applicable')",
    "note": "One sentence summary following guidelines (empty string if not applicable)",
    "summary": "Complete screening note"
}}
"""
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"""You are a professional Screening Note specialist trained on Screening Note Summary Guideline v2.0 for English interviews with speaker differentiation.

Your expertise:
- Analyzing interview conversations between interviewer ({interviewer_name}) and candidate
- Creating structured summaries ONLY from candidate responses
- Completely ignoring interviewer statements when building candidate profiles
- Following exact sentence construction principles for enterprise recruitment
- Using recommended templates for consistency across all candidates
- Ensuring technical terms are accurate and complete (no abbreviations)
- Focusing on English interview context and North American business standards

CRITICAL RULE: You MUST distinguish between interviewer and candidate statements. NEVER include interviewer's background, experience, or statements as part of the candidate's profile."""},
                    {"role": "user", "content": speaker_aware_prompt}
                ],
                max_tokens=800,
                temperature=0.1  # 매우 일관성 있는 결과
            )
            
            result = response.choices[0].message.content.strip()
            
            # JSON 파싱 시도
            try:
                summary_json = json.loads(result)
                return summary_json
            except json.JSONDecodeError:
                # JSON 파싱 실패 시 기본 형식으로 변환
                return {
                    "category": "Other",
                    "note": result,
                    "summary": result
                }
                
        except Exception as e:
            print(f"Speaker-aware screening note generation failed: {e}")
            return {
                "category": "Error",
                "note": f"Processing failed: {str(e)}",
                "summary": "Unable to process content."
            } 

    def categorize_interview_content(self, conversation_text, categories):
        """
        인터뷰 대화 내용을 사용자 정의 카테고리별로 분류하여 요약
        (이 기능은 analyze_complete_interview로 대체되었습니다.)
        """
        print("[GPTSummarizer] 'categorize_interview_content'는 더 이상 사용되지 않습니다. 'analyze_interview_and_get_summary'를 사용하세요.")
        
        # 임시로 호환성을 위해 Enhanced Analyzer를 호출하는 로직으로 연결
        if self.enhanced_analyzer:
            # 여기서 template을 만들거나 찾아야 하지만, 이 함수는 사용되지 않으므로 간단히 처리
            template = {"position": "CustomHR"} # 카테고리를 보고 임시 추정
            analysis_result = self.analyze_interview_and_get_summary(conversation_text, template)
            if analysis_result.get("success"):
                return analysis_result.get("comprehensive_analysis", {}).get("detailed_analysis", {})
        
        return {"error": "This function is deprecated. Please use 'analyze_interview_and_get_summary'."}
            
    def _parse_category_text(self, text, categories):
        """텍스트에서 카테고리별 내용 파싱 (JSON 파싱 실패 시 대안)"""
        result = {}
        lines = text.split('\n')
        current_category = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 카테고리 찾기
            found_category = None
            for category in categories:
                if category.lower() in line.lower() and ':' in line:
                    found_category = category
                    break
                    
            if found_category:
                # 이전 카테고리 내용 저장
                if current_category and current_content:
                    result[current_category] = ' '.join(current_content).strip()
                    
                # 새 카테고리 시작
                current_category = found_category
                current_content = [line.split(':', 1)[1].strip() if ':' in line else '']
            elif current_category:
                current_content.append(line)
                
        # 마지막 카테고리 내용 저장
        if current_category and current_content:
            result[current_category] = ' '.join(current_content).strip()
            
        return result
        
    def analyze_incremental_content(self, new_content, existing_categories):
        """
        새로 추가된 내용만 분석하여 기존 카테고리에 추가
        
        Args:
            new_content (str): 새로 추가된 대화 내용
            existing_categories (list): 기존 카테고리 목록
            
        Returns:
            dict: 새로 분석된 카테고리별 내용
        """
        if not new_content.strip():
            return {}
        
        # Enhanced Analyzer를 사용하여 분석
        template = {"position": "CustomHR"}  # 기본값으로 CustomHR 사용
        analysis_result = self.analyze_interview_and_get_summary(new_content, template)
        
        if analysis_result.get("success"):
            detailed_analysis = analysis_result.get("comprehensive_analysis", {}).get("detailed_analysis", {})
            
            # 기존 카테고리 형식으로 변환
            result = {}
            for category, analysis_data in detailed_analysis.items():
                if isinstance(analysis_data, dict) and "assessment" in analysis_data:
                    assessment_list = analysis_data["assessment"]
                    if isinstance(assessment_list, list):
                        result[category] = "\n".join(assessment_list)
                    else:
                        result[category] = str(assessment_list)
                else:
                    result[category] = str(analysis_data)
            
            return result
        
        return {}
    
    def analyze_complete_interview(self, interview_script: str, template: dict, screening_data: dict) -> dict:
        """Complete interview script analysis using Enhanced Analyzer"""
        
        if not self.enhanced_analyzer:
            return {
                "error": "Enhanced Analyzer not initialized.",
                "fallback_analysis": self._fallback_analysis(interview_script, template, screening_data)
            }
        
        try:
            print("[GPTSummarizer] 🚀 Enhanced Analyzer를 사용하여 전체 인터뷰 분석 시작...")
            print(f"[GPTSummarizer] 📄 분석 대상 텍스트 길이: {len(interview_script)}자")
            
            # 1. Extract candidate profile
            print("[GPTSummarizer] 📊 Step 1: 후보자 프로필 추출 중...")
            candidate_profile = self.enhanced_analyzer.extract_candidate_profile(interview_script, template)
            print(f"[GPTSummarizer] ✅ Step 1 완료: 후보자 '{candidate_profile.get('candidate_name', 'Unknown')}' 프로필 추출됨")
            
            # 2. Comprehensive interview analysis
            print("[GPTSummarizer] 🔍 Step 2: 종합적 인터뷰 분석 중...")
            comprehensive_analysis = self.enhanced_analyzer.analyze_comprehensive_interview(
                interview_script, template, candidate_profile
            )
            print(f"[GPTSummarizer] ✅ Step 2 완료: {len(comprehensive_analysis.get('detailed_analysis', {}))}개 카테고리 분석됨")
            
            # 3. Improve existing screening notes
            print("[GPTSummarizer] 📝 Step 3: 스크리닝 노트 개선 중...")
            improved_screening = self.enhanced_analyzer.improve_screening_notes(
                screening_data, interview_script, template
            )
            print("[GPTSummarizer] ✅ Step 3 완료: 스크리닝 노트 품질 개선됨")
            
            # 4. Generate final report
            print("[GPTSummarizer] 📋 Step 4: 최종 리포트 생성 중...")
            final_report = self.enhanced_analyzer.generate_final_report(
                candidate_profile, comprehensive_analysis, improved_screening, interview_script, template
            )
            print(f"[GPTSummarizer] ✅ Step 4 완료: {len(final_report)}자 최종 리포트 생성됨")
            
            print("[GPTSummarizer] 🎉 전체 인터뷰 분석 완료!")
            
            return {
                "success": True,
                "candidate_profile": candidate_profile,
                "comprehensive_analysis": comprehensive_analysis,
                "improved_screening": improved_screening,
                "final_report": final_report,
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"[GPTSummarizer] ❌ 전체 인터뷰 분석 실패: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                "error": f"Analysis failed: {str(e)}",
                "fallback_analysis": self._fallback_analysis(interview_script, template, screening_data)
            }
    
    def _fallback_analysis(self, interview_script: str, template: dict, screening_data: dict) -> dict:
        """Basic analysis when Enhanced Analyzer fails"""
        try:
            # Perform basic summary
            basic_summary = self.summarize(interview_script[:2000])  # Length limit
            
            return {
                "type": "basic_analysis",
                "summary": basic_summary.get('summary', 'Unable to perform basic analysis.'),
                "screening_summary": self._summarize_screening_data(screening_data),
                "recommendation": "Only basic analysis available as Enhanced Analyzer is not accessible."
            }
            
        except Exception as e:
            return {
                "type": "error",
                "message": f"Basic analysis also failed: {str(e)}"
            }
    
    def _summarize_screening_data(self, screening_data: dict) -> str:
        """Summarize screening data"""
        if not screening_data:
            return "No screening data available."
        
        summary_parts = []
        summary_parts.append("=== Screening Notes Summary ===")
        
        for category, content in screening_data.items():
            if content and content.strip():
                summary_parts.append(f"\n▼ {category}")
                # Organize content by lines
                lines = content.strip().split('\n')
                for line in lines[:3]:  # Maximum 3 lines
                    if line.strip():
                        summary_parts.append(f"   • {line.strip()}")
        
        return '\n'.join(summary_parts)
    
    def quick_profile_extraction(self, interview_text: str) -> dict:
        """Quick candidate profile extraction (for immediate display in SummaryWidget)"""
        
        if self.enhanced_analyzer:
            try:
                return self.enhanced_analyzer.extract_candidate_profile(interview_text, {})
            except Exception as e:
                print(f"[GPTSummarizer] Quick profile extraction failed: {e}")
        
        # Fallback: simple regex extraction
        return self._basic_profile_extraction(interview_text)
    
    def _basic_profile_extraction(self, text: str) -> dict:
        """Basic profile extraction using regex"""
        
        # Attempt to extract name
        name_patterns = [
            r'(?:Hi,?\s+)?(?:I\'m|My name is|This is)\s+([A-Z][a-z]+)',
            r'Interviewer:\s*Hi\s+([A-Z][a-z]+)',
            r'^([A-Z][a-z]+):',  # Extract name from conversation format
        ]
        
        name = "Not specified"
        for pattern in name_patterns:
            match = re.search(pattern, text, re.MULTILINE)
            if match:
                name = match.group(1)
                break
        
        # Extract company
        company_match = re.search(r'(?:at|with|from)\s+([A-Z][a-zA-Z\s&]+(?:Inc|Corp|LLC|Company|Solutions|Logistics|Group))', text)
        company = company_match.group(1) if company_match else "Not specified"
        
        # Extract salary information
        salary_patterns = [
            r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'(\d{1,3}(?:,\d{3})*)\s*(?:k|K|thousand)',
            r'base salary of.*?\$?(\d{1,3}(?:,\d{3})*)'
        ]
        
        salary = "Not specified"
        for pattern in salary_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                salary = f"${match.group(1)}"
                break
        
        return {
            "candidate_name": name,
            "current_company": company,
            "salary_expectation": salary,
            "extraction_method": "basic_regex"
        }

    def quick_categorize_text(self, text: str, categories: list) -> dict:
        """
        텍스트를 빠르게 카테고리별로 분류 (Enhanced Analyzer 없이)
        
        Args:
            text (str): 분석할 텍스트
            categories (list): 분류할 카테고리 목록
            
        Returns:
            dict: 카테고리별 분류 결과
        """
        if not text.strip():
            return {}
        
        try:
            print(f"[GPTSummarizer] ⚡ 빠른 카테고리 분석 시작 (텍스트 길이: {len(text)}자)")
            
            # 카테고리 목록을 문자열로 변환
            categories_str = ", ".join(categories)
            
            # 영어 전용 분류 프롬프트
            quick_prompt = f"""Please categorize the following interview text into the most appropriate category based on the definitions below and provide a brief summary in ENGLISH ONLY.

**--- CATEGORY DEFINITIONS ---**

*   **`Expertise`**: Core professional skills, specific accomplishments, and direct job-related experiences. (e.g., "Managed payroll for 500 employees," "Developed a new sales pipeline.")
*   **`Industry/Product/Technical Familiarity`**: Knowledge of the specific industry, markets, products, or technologies. (e.g., "Familiar with the automotive sector," "Experience with SAP and Workday.")
*   **`Leadership/Cultural Fit`**: Leadership style, team collaboration, and adaptability to the work environment. (e.g., "Led a team of 5 engineers," "Comfortable in a fast-paced startup.")
*   **`Motivation/Reason for Interest`**: Why the candidate is seeking a new role and their interest in this specific company. (e.g., "Seeking more growth opportunities," "Attracted to the company's mission.")
*   **`Logistics`**: Practical details like salary, location, and availability. (e.g., "Looking for $120K base," "Can start in 2 weeks.")

**--- INTERVIEW TEXT ---**
{text}

**--- RESPONSE FORMAT (JSON) ---**
Response in JSON format (ALL TEXT MUST BE IN ENGLISH):
{{
    "Category_Name": {{
        "assessment": ["Summary point 1 in English", "Summary point 2 in English"]
    }}
}}

**--- CRITICAL REQUIREMENTS ---**
- **Adhere strictly to the category definitions above.**
- **ALL output text must be in English only.**
- **CAPTURE BOTH OBJECTIVE FACTS AND SUBJECTIVE EXPRESSIONS** (emotions, motivations, values, thoughts).
- **USE RESUME-STYLE BULLET POINTS**: Start directly with action verbs, NO SUBJECTS (he/she/candidate).
    - ✅ Good: "Manages HR operations for 700+ employees."
    - ✅ Good: "Expresses passion for the automotive industry."
    - ❌ Avoid: "He manages HR operations..."
- **IF NO CONCRETE INFORMATION EXISTS FOR A CATEGORY, SIMPLY SKIP THAT CATEGORY.**
- Use specific numbers when mentioned (e.g., "3-year" instead of "multi-year").
- Keep summaries concise and action-oriented.
"""
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # 빠른 모델 사용
                messages=[
                    {"role": "system", "content": "You are a professional interview content categorizer. You MUST respond ONLY in English. Analyze and categorize interview content accurately and concisely in English only."},
                    {"role": "user", "content": quick_prompt}
                ],
                temperature=0.1,
                max_tokens=800,
                response_format={ "type": "json_object" }
            )
            
            result = response.choices[0].message.content
            print(f"[GPTSummarizer] ✅ 빠른 분석 완료 (영어 전용)")
            
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                print(f"[GPTSummarizer] JSON 파싱 실패, 텍스트로 반환")
                return {"Other": {"assessment": [f"Analysis error: {result[:100]}..."]}}
                
        except Exception as e:
            print(f"[GPTSummarizer] 빠른 분석 실패: {e}")
            return {"Other": {"assessment": [f"Analysis failed: {text[:100]}..."]}}