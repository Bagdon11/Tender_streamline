"""
Checklist Generator - Create personalized checklists from tender documents
"""

import re
from typing import List, Dict, Any
from datetime import datetime, timedelta

class ChecklistGenerator:
    """Generate personalized checklists based on tender document analysis."""
    
    def __init__(self):
        # Common tender checklist categories and their keywords
        self.categories = {
            "Documentation": [
                "certificate", "license", "permit", "registration", "document",
                "proof", "evidence", "record", "report", "statement", "form",
                "application", "copy", "signed", "notarized"
            ],
            "Technical Requirements": [
                "specification", "technical", "requirement", "standard", "quality",
                "performance", "capacity", "feature", "function", "design",
                "equipment", "software", "hardware", "system"
            ],
            "Financial": [
                "budget", "cost", "price", "financial", "payment", "invoice",
                "estimate", "quote", "bid", "tender amount", "bank guarantee",
                "funding", "grant", "sponsorship", "revenue"
            ],
            "Timeline & Delivery": [
                "deadline", "delivery", "timeline", "schedule", "completion",
                "milestone", "duration", "period", "date", "time frame",
                "start date", "end date", "due"
            ],
            "Legal & Compliance": [
                "legal", "compliance", "regulation", "law", "policy", "procedure",
                "agreement", "contract", "terms", "conditions", "liability",
                "insurance", "bond", "coverage"
            ],
            "Experience & Qualifications": [
                "experience", "qualification", "expertise", "skill", "competency",
                "track record", "portfolio", "reference", "testimonial", "cv",
                "resume", "background", "history"
            ],
            "Contact & Communication": [
                "contact", "phone", "email", "address", "communication",
                "representative", "coordinator", "manager", "director"
            ],
            "Submission Requirements": [
                "submit", "submission", "format", "copies", "original", "signed",
                "sealed", "envelope", "proposal", "tender submission", "deadline"
            ]
        }
        
        # Requirement keywords that indicate mandatory items
        self.requirement_indicators = [
            "must", "shall", "required", "mandatory", "need to", "have to",
            "essential", "compulsory", "obligatory", "necessary"
        ]
        
        # Common action verbs for checklist items
        self.action_verbs = [
            "obtain", "provide", "submit", "complete", "prepare", "review",
            "verify", "ensure", "confirm", "check", "validate", "compile",
            "gather", "collect", "organize", "arrange"
        ]
    
    def generate_checklist(self, document_content: str) -> Dict[str, Any]:
        """
        Generate a personalized checklist from tender document content.
        
        Args:
            document_content: Combined text content from tender documents
            
        Returns:
            Dictionary containing checklist data with categories and items
        """
        # Analyze document content
        analysis = self._analyze_content(document_content)
        
        # Extract key requirements
        requirements = self._extract_requirements(document_content)
        
        # Extract deadlines
        deadlines = self._extract_deadlines(document_content)
        
        # Generate checklist items by category
        checklist_data = {
            "title": "Tender Submission Checklist",
            "generated_date": datetime.now().isoformat(),
            "categories": {},
            "summary": analysis,
            "estimated_completion_time": self._estimate_completion_time(requirements),
            "critical_deadlines": deadlines
        }
        
        for category, keywords in self.categories.items():
            items = self._generate_category_items(category, keywords, document_content, requirements)
            if items:  # Only include categories with items
                checklist_data["categories"][category] = {
                    "items": items,
                    "completed": 0,
                    "total": len(items),
                    "priority": self._calculate_priority(category, document_content)
                }
        
        return checklist_data
    
    def _analyze_content(self, content: str) -> Dict[str, Any]:
        """Analyze document content for key metrics."""
        words = content.split()
        sentences = re.split(r'[.!?]+', content)
        
        # Check if this is OCR content
        is_ocr = "[OCR EXTRACTED TEXT]" in content
        
        analysis = {
            "word_count": len(words),
            "sentence_count": len([s for s in sentences if s.strip()]),
            "complexity_score": self._calculate_complexity(content),
            "key_sections": self._identify_key_sections(content),
            "document_type": self._identify_document_type(content),
            "is_ocr_content": is_ocr,
            "requirements_found": len(self._extract_requirements(content))
        }
        
        return analysis
    
    def _extract_requirements(self, content: str) -> List[str]:
        """Extract specific requirements from the document."""
        requirements = []
        
        # Look for requirement indicators
        requirement_patterns = [
            r"must\s+([^.!?]{10,150})",
            r"shall\s+([^.!?]{10,150})",
            r"required\s+to\s+([^.!?]{10,150})",
            r"applicant\s+(?:must|should|shall)\s+([^.!?]{10,150})",
            r"you\s+(?:must|need to|should)\s+([^.!?]{10,150})",
            r"please\s+(?:provide|submit|include|attach)\s+([^.!?]{10,150})"
        ]
        
        for pattern in requirement_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                requirement = match.group(1).strip()
                if len(requirement) > 10 and len(requirement) < 200:
                    # Clean up the requirement text
                    requirement = re.sub(r'\s+', ' ', requirement)
                    requirements.append(requirement)
        
        # Look for bulleted or numbered requirements
        bullet_patterns = [
            r"[•·▪▫-]\s*([^.!?\n]{15,150})",
            r"\d+\.\s*([^.!?\n]{15,150})",
            r"[a-z]\)\s*([^.!?\n]{15,150})"
        ]
        
        for pattern in bullet_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                requirement = match.group(1).strip()
                if any(indicator in requirement.lower() for indicator in self.requirement_indicators):
                    requirement = re.sub(r'\s+', ' ', requirement)
                    requirements.append(requirement)
        
        return list(set(requirements))  # Remove duplicates
    
    def _generate_category_items(self, category: str, keywords: List[str], 
                                content: str, requirements: List[str]) -> List[Dict[str, Any]]:
        """Generate checklist items for a specific category."""
        items = []
        
        # Check if category is relevant to this tender
        content_lower = content.lower()
        keyword_matches = sum(1 for keyword in keywords if keyword in content_lower)
        
        if keyword_matches == 0:
            return items  # Skip irrelevant categories
        
        # Generate items based on category
        if category == "Documentation":
            items.extend(self._generate_documentation_items(content, requirements))
        elif category == "Technical Requirements":
            items.extend(self._generate_technical_items(content, requirements))
        elif category == "Financial":
            items.extend(self._generate_financial_items(content, requirements))
        elif category == "Timeline & Delivery":
            items.extend(self._generate_timeline_items(content, requirements))
        elif category == "Legal & Compliance":
            items.extend(self._generate_legal_items(content, requirements))
        elif category == "Experience & Qualifications":
            items.extend(self._generate_experience_items(content, requirements))
        elif category == "Contact & Communication":
            items.extend(self._generate_contact_items(content, requirements))
        elif category == "Submission Requirements":
            items.extend(self._generate_submission_items(content, requirements))
        
        return items
    
    def _generate_documentation_items(self, content: str, requirements: List[str]) -> List[Dict[str, Any]]:
        """Generate documentation checklist items."""
        items = []
        content_lower = content.lower()
        
        # Base documentation items
        base_items = []
        
        if any(word in content_lower for word in ["certificate", "certification"]):
            base_items.append("Obtain all required certificates and certifications")
        
        if any(word in content_lower for word in ["license", "permit"]):
            base_items.append("Gather current licenses and permits")
        
        if any(word in content_lower for word in ["registration", "company"]):
            base_items.append("Prepare company registration documents")
        
        if any(word in content_lower for word in ["form", "application"]):
            base_items.append("Complete all required forms and applications")
        
        if any(word in content_lower for word in ["copy", "copies", "original"]):
            base_items.append("Prepare required number of document copies")
        
        for item_text in base_items:
            items.append({
                "id": f"doc_{len(items) + 1}",
                "text": item_text,
                "completed": False,
                "priority": "high",
                "estimated_hours": 2,
                "notes": "",
                "attachments": []
            })
        
        # Add requirement-specific items
        for req in requirements:
            req_lower = req.lower()
            if any(word in req_lower for word in ["certificate", "document", "proof", "record", "form"]):
                items.append({
                    "id": f"doc_{len(items) + 1}",
                    "text": f"Address requirement: {req}",
                    "completed": False,
                    "priority": "high",
                    "estimated_hours": 3,
                    "notes": f"Specific requirement from document: {req}",
                    "attachments": []
                })
        
        return items
    
    def _generate_financial_items(self, content: str, requirements: List[str]) -> List[Dict[str, Any]]:
        """Generate financial checklist items."""
        items = []
        content_lower = content.lower()
        
        base_items = []
        
        if any(word in content_lower for word in ["budget", "cost", "funding"]):
            base_items.append("Prepare detailed budget breakdown")
        
        if any(word in content_lower for word in ["grant", "funding", "sponsorship"]):
            base_items.append("Calculate total funding request amount")
        
        if any(word in content_lower for word in ["bank", "guarantee", "security"]):
            base_items.append("Arrange bank guarantee or security bond")
        
        if any(word in content_lower for word in ["payment", "invoice", "financial"]):
            base_items.append("Review payment terms and financial obligations")
        
        for item_text in base_items:
            items.append({
                "id": f"fin_{len(items) + 1}",
                "text": item_text,
                "completed": False,
                "priority": "high",
                "estimated_hours": 3,
                "notes": "",
                "attachments": []
            })
        
        return items
    
    def _generate_timeline_items(self, content: str, requirements: List[str]) -> List[Dict[str, Any]]:
        """Generate timeline and delivery checklist items."""
        items = []
        content_lower = content.lower()
        
        base_items = []
        
        if any(word in content_lower for word in ["deadline", "due", "submit"]):
            base_items.append("Note all submission deadlines and due dates")
        
        if any(word in content_lower for word in ["timeline", "schedule", "milestone"]):
            base_items.append("Create project timeline with key milestones")
        
        if any(word in content_lower for word in ["start", "begin", "commence"]):
            base_items.append("Confirm project start date and initial requirements")
        
        if any(word in content_lower for word in ["completion", "finish", "end"]):
            base_items.append("Plan for project completion and final deliverables")
        
        for item_text in base_items:
            items.append({
                "id": f"time_{len(items) + 1}",
                "text": item_text,
                "completed": False,
                "priority": "medium",
                "estimated_hours": 2,
                "notes": "",
                "attachments": []
            })
        
        return items
    
    def _generate_technical_items(self, content: str, requirements: List[str]) -> List[Dict[str, Any]]:
        """Generate technical requirements checklist items."""
        items = []
        content_lower = content.lower()
        
        base_items = []
        
        if any(word in content_lower for word in ["specification", "technical", "system"]):
            base_items.append("Review all technical specifications and requirements")
        
        if any(word in content_lower for word in ["equipment", "hardware", "software"]):
            base_items.append("Verify technical capacity and equipment requirements")
        
        if any(word in content_lower for word in ["standard", "quality", "performance"]):
            base_items.append("Ensure compliance with quality and performance standards")
        
        for item_text in base_items:
            items.append({
                "id": f"tech_{len(items) + 1}",
                "text": item_text,
                "completed": False,
                "priority": "high",
                "estimated_hours": 4,
                "notes": "",
                "attachments": []
            })
        
        return items
    
    def _generate_legal_items(self, content: str, requirements: List[str]) -> List[Dict[str, Any]]:
        """Generate legal and compliance checklist items."""
        items = []
        content_lower = content.lower()
        
        base_items = []
        
        if any(word in content_lower for word in ["legal", "law", "regulation"]):
            base_items.append("Review all legal requirements and regulations")
        
        if any(word in content_lower for word in ["contract", "agreement", "terms"]):
            base_items.append("Understand contract terms and conditions")
        
        if any(word in content_lower for word in ["insurance", "liability", "coverage"]):
            base_items.append("Verify insurance coverage and liability requirements")
        
        for item_text in base_items:
            items.append({
                "id": f"legal_{len(items) + 1}",
                "text": item_text,
                "completed": False,
                "priority": "high",
                "estimated_hours": 3,
                "notes": "",
                "attachments": []
            })
        
        return items
    
    def _generate_experience_items(self, content: str, requirements: List[str]) -> List[Dict[str, Any]]:
        """Generate experience and qualifications checklist items."""
        items = []
        content_lower = content.lower()
        
        base_items = []
        
        if any(word in content_lower for word in ["experience", "background", "history"]):
            base_items.append("Document relevant experience and track record")
        
        if any(word in content_lower for word in ["qualification", "skill", "competency"]):
            base_items.append("Prepare team qualifications and skills documentation")
        
        if any(word in content_lower for word in ["reference", "testimonial", "portfolio"]):
            base_items.append("Gather references and testimonials")
        
        for item_text in base_items:
            items.append({
                "id": f"exp_{len(items) + 1}",
                "text": item_text,
                "completed": False,
                "priority": "medium",
                "estimated_hours": 4,
                "notes": "",
                "attachments": []
            })
        
        return items
    
    def _generate_contact_items(self, content: str, requirements: List[str]) -> List[Dict[str, Any]]:
        """Generate contact and communication checklist items."""
        items = []
        content_lower = content.lower()
        
        base_items = []
        
        if any(word in content_lower for word in ["contact", "phone", "email"]):
            base_items.append("Update all contact information and details")
        
        if any(word in content_lower for word in ["representative", "coordinator", "manager"]):
            base_items.append("Identify key contacts and representatives")
        
        for item_text in base_items:
            items.append({
                "id": f"contact_{len(items) + 1}",
                "text": item_text,
                "completed": False,
                "priority": "low",
                "estimated_hours": 1,
                "notes": "",
                "attachments": []
            })
        
        return items
    
    def _generate_submission_items(self, content: str, requirements: List[str]) -> List[Dict[str, Any]]:
        """Generate submission requirements checklist items."""
        items = []
        content_lower = content.lower()
        
        base_items = []
        
        if any(word in content_lower for word in ["submit", "submission", "deadline"]):
            base_items.append("Prepare final submission package")
        
        if any(word in content_lower for word in ["format", "copies", "signed"]):
            base_items.append("Ensure correct submission format and signatures")
        
        if any(word in content_lower for word in ["deadline", "due date", "closing"]):
            base_items.append("Confirm submission deadline and delivery method")
        
        for item_text in base_items:
            items.append({
                "id": f"sub_{len(items) + 1}",
                "text": item_text,
                "completed": False,
                "priority": "high",
                "estimated_hours": 2,
                "notes": "",
                "attachments": []
            })
        
        return items
    
    def _calculate_complexity(self, content: str) -> float:
        """Calculate document complexity score (0-1)."""
        sentences = re.split(r'[.!?]+', content)
        words = content.split()
        
        if not sentences or not words:
            return 0.0
        
        avg_sentence_length = len(words) / len([s for s in sentences if s.strip()])
        unique_words = len(set(word.lower() for word in words))
        total_words = len(words)
        
        complexity = min((avg_sentence_length / 20) + (unique_words / total_words), 1.0)
        return round(complexity, 2)
    
    def _identify_key_sections(self, content: str) -> List[str]:
        """Identify key sections in the document."""
        sections = []
        
        # Look for common section headers
        section_patterns = [
            r"\b(requirements?|specifications?|terms?|conditions?)\b",
            r"\b(scope\s+of\s+work|deliverables?)\b",
            r"\b(timeline|schedule|deadline)\b",
            r"\b(evaluation\s+criteria|selection\s+criteria)\b",
            r"\b(application|eligibility|criteria)\b"
        ]
        
        for pattern in section_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                sections.append(match.group(0))
        
        return list(set(sections))
    
    def _identify_document_type(self, content: str) -> str:
        """Identify the type of tender document."""
        content_lower = content.lower()
        
        if "grant" in content_lower and "application" in content_lower:
            return "Grant Application"
        elif "rfp" in content_lower or "request for proposal" in content_lower:
            return "RFP"
        elif "rfq" in content_lower or "request for quotation" in content_lower:
            return "RFQ"
        elif "tender" in content_lower:
            return "Tender"
        elif "bid" in content_lower:
            return "Bid"
        elif "application" in content_lower:
            return "Application"
        else:
            return "Document"
    
    def _calculate_priority(self, category: str, content: str) -> str:
        """Calculate priority level for a category."""
        high_priority_categories = ["Financial", "Legal & Compliance", "Submission Requirements", "Documentation"]
        
        if category in high_priority_categories:
            return "high"
        elif category in ["Technical Requirements", "Timeline & Delivery"]:
            return "medium"
        else:
            return "low"
    
    def _estimate_completion_time(self, requirements: List[str]) -> Dict[str, int]:
        """Estimate time needed to complete checklist."""
        base_hours = 15  # Base time for any application/tender
        additional_hours = len(requirements) * 1.5  # 1.5 hours per requirement
        
        total_hours = int(base_hours + additional_hours)
        
        return {
            "total_hours": total_hours,
            "estimated_days": max(1, total_hours // 8)
        }
    
    def _extract_deadlines(self, content: str) -> List[Dict[str, str]]:
        """Extract deadline information from content."""
        deadlines = []
        
        # Look for date patterns
        date_patterns = [
            r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{4})\b",
            r"\b(\d{4}[/-]\d{1,2}[/-]\d{1,2})\b",
            r"\b(\w+\s+\d{1,2},?\s+\d{4})\b",
            r"\b(\d{1,2}\s+\w+\s+\d{4})\b"
        ]
        
        deadline_keywords = ["deadline", "due date", "submission date", "closing date", "final date", "by"]
        
        for keyword in deadline_keywords:
            for date_pattern in date_patterns:
                # Look for dates near deadline keywords
                pattern = f"{keyword}[^.]*?{date_pattern}"
                matches = re.finditer(pattern, content, re.IGNORECASE)
                
                for match in matches:
                    date_match = re.search(date_pattern, match.group(0))
                    if date_match:
                        deadlines.append({
                            "type": keyword,
                            "date": date_match.group(1),
                            "context": match.group(0)
                        })
        
        return deadlines