import re
import pdfplumber
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging
import base64
from PIL import Image
try:
    import cv2
    import numpy as np
except Exception:  # pragma: no cover - optional dependency at runtime
    cv2 = None
    np = None

logger = logging.getLogger(__name__)

class CVParser:
    """Service for parsing CV files and extracting candidate information"""
    
    def __init__(self):
        # Regex patterns for extracting information
        self.patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'(?:\+33|0)[1-9](?:[0-9]{8}|[0-9]{2}(?:[0-9]{2}){2})',
            'linkedin': r'(https?:\/\/(?:[\w]+\.)?linkedin\.com\/[^\s,]+)',
            'date': r'\b(?:0?[1-9]|[12][0-9]|3[01])[/\-](?:0?[1-9]|1[012])[/\-](?:19|20)\d{2}\b',
            'gender_indicators': {
                'male': [r'\b(?:homme|male|m\.|monsieur|mr\.?)\b', r'\b(?:né|né le)\b'],
                'female': [r'\b(?:femme|female|f\.|madame|mme\.?)\b', r'\b(?:née|née le)\b']
            }
        }
        # Common country and city keywords to help locate addresses
        self.country_keywords = {
            'maroc', 'morocco', 'france', 'tunisie', 'algerie', 'algérie', 'algeria',
            'espagne', 'spain', 'italie', 'italy', 'allemagne', 'germany', 'belgique', 'belgium',
            'canada', 'suisse', 'switzerland', 'royaume-uni', 'united kingdom', 'uk',
            'pays-bas', 'netherlands', 'portugal', 'usa', 'états-unis', 'etats-unis', 'united states',
            'qatar', 'uae', 'emirats arabes unis', 'émirats arabes unis', 'arabie saoudite', 'saudi arabia'
        }
        self.city_keywords = {
            # Morocco
            'casablanca', 'rabat', 'marrakech', 'agadir', 'fes', 'fès', 'meknes', 'meknès', 'tanger', 'tangier',
            'tetouan', 'tétouan', 'kenitra', 'kénitra', 'oujda', 'safi', 'essaouira', 'laayoune', 'el jadida',
            'settat', 'nador', 'berrechid', 'mohammedia', 'beni mellal', 'béni mellal',
            # France
            'paris', 'lyon', 'marseille', 'toulouse', 'lille', 'bordeaux', 'nice', 'nantes', 'strasbourg', 'montpellier', 'rennes', 'grenoble',
            # International (examples)
            'london', 'new york', 'madrid', 'rome', 'berlin', 'ottawa', 'montreal', 'montréal', 'doha', 'dubai', 'dubaï', 'abu dhabi', 'abou dhabi',
            'lisbon', 'lisbonne', 'bruxelles', 'brussels', 'geneva', 'genève', 'zurich', 'zürich', 'amsterdam', 'barcelona'
        }
    
    def parse_single_cv(self, file_path: str) -> Dict:
        """Parse a single CV file and extract candidate information"""
        try:
            if file_path.lower().endswith('.pdf'):
                return self._parse_pdf(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_path}")
        except Exception as e:
            logger.error(f"Error parsing CV {file_path}: {str(e)}")
            return self._create_default_candidate()
    
    def parse_multiple_cvs(self, pdf_files: List[str]) -> List[Dict]:
        """Parse multiple CVs from a list of PDF files"""
        candidates = []
        try:
            for pdf_file in pdf_files:
                try:
                    candidate = self.parse_single_cv(pdf_file)
                    candidates.append(candidate)
                except Exception as e:
                    logger.error(f"Error parsing CV {pdf_file}: {str(e)}")
                    candidates.append(self._create_default_candidate())
        except Exception as e:
            logger.error(f"Error parsing multiple CVs: {str(e)}")
        
        return candidates
    
    def _parse_pdf(self, file_path: str) -> Dict:
        """Parse PDF file and extract text content"""
        try:
            # Extract text using pdfplumber
            text_content = ""
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    if page.extract_text():
                        text_content += page.extract_text() + "\n"
            
            # Extract information from text
            candidate_data = self._extract_information(text_content)
            # Try to extract a profile photo
            candidate_data['photo'] = self._extract_profile_photo(file_path)
            
            return candidate_data
            
        except Exception as e:
            logger.error(f"Error reading PDF {file_path}: {str(e)}")
            return self._create_default_candidate()

    def _extract_profile_photo(self, file_path: str) -> Optional[str]:
        """Attempt to extract a profile photo (face) from the first pages of a PDF.
        Returns a data URL (base64) if found, else None.
        """
        try:
            if cv2 is None or np is None:
                return None
            with pdfplumber.open(file_path) as pdf:
                pages = pdf.pages[:2] if len(pdf.pages) >= 1 else pdf.pages
                for page in pages:
                    try:
                        pil_page_img = page.to_image(resolution=200).original  # PIL Image
                        rgb = pil_page_img.convert('RGB')
                        arr = np.array(rgb)
                        gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
                        cascade_path = getattr(cv2.data, 'haarcascades', '') + 'haarcascade_frontalface_default.xml'
                        face_cascade = cv2.CascadeClassifier(cascade_path)
                        faces = face_cascade.detectMultiScale(
                            gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80)
                        )
                        if len(faces) == 0:
                            continue
                        # Choose the face most likely to be a profile photo: largest area near top half
                        h, w = gray.shape[:2]
                        def score(face):
                            x, y, fw, fh = face
                            area = fw * fh
                            top_bias = max(0, (h * 0.6 - y))  # prefer faces in top 60%
                            return area + top_bias * 50
                        best = max(faces, key=score)
                        x, y, fw, fh = best
                        # Add padding and clamp
                        pad = int(max(fw, fh) * 0.25)
                        x0 = max(0, x - pad)
                        y0 = max(0, y - pad)
                        x1 = min(w, x + fw + pad)
                        y1 = min(h, y + fh + pad)
                        face_crop = arr[y0:y1, x0:x1]
                        if face_crop.size == 0:
                            continue
                        # Encode to JPEG base64
                        face_img = Image.fromarray(face_crop)
                        from io import BytesIO
                        buf = BytesIO()
                        face_img.save(buf, format='JPEG', quality=90)
                        b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
                        return f'data:image/jpeg;base64,{b64}'
                    except Exception:
                        continue
        except Exception as e:
            logger.warning(f"Photo extraction failed: {e}")
        return None
    
    def _extract_information(self, text: str) -> Dict:
        """Extract candidate information from text content"""
        text_lower = text.lower()
        
        # Extract email
        email_match = re.search(self.patterns['email'], text, re.IGNORECASE)
        email = email_match.group() if email_match else ""
        
        # Extract phone with improved validation
        phone = self._extract_phone_number(text)
        
        # Extract LinkedIn profile with improved regex
        linkedin = self._extract_linkedin_profile(text)
        
        # Extract birth date
        birth_date = self._extract_birth_date(text)
        
        # Determine gender
        gender = self._detect_gender(text_lower)
        
        # Extract name with improved NLP-like detection
        name_info = self._extract_name_improved(text)
        
        # Extract address
        address = self._extract_address(text)
        
        return {
            'last_name': name_info.get('last_name', ''),
            'first_name': name_info.get('first_name', ''),
            'email': email,
            'phone': phone,
            'birth_date': birth_date,
            'address': address,
            'gender': gender,
            'photo': None,  # Will be set by photo extraction
            'linkedin_profile': linkedin
        }
    
    def _normalize_moroccan_phone(self, raw: str) -> str:
        """Normalize Moroccan phone numbers to the canonical format +212XXXXXXXXX.
        Rules:
        - Remove separators (spaces, dots, hyphens, parentheses)
        - If starts with +212 or 00212 or 212 → keep last 9 digits after 212
        - If starts with 0 → replace leading 0 by +212 and keep next 9 digits
        - Otherwise return empty string
        """
        try:
            if not raw:
                return ""
            # Keep digits only to simplify handling
            digits = re.sub(r"\D", "", raw)
            if not digits:
                return ""
            # Handle international prefix 00
            if digits.startswith("00212"):
                digits = digits[2:]  # drop leading 00 → 212...
            # With 212 prefix
            if digits.startswith("212"):
                remaining = digits[3:]
                if len(remaining) >= 9:
                    return "+212" + remaining[:9]
                return ""
            # Local leading zero
            if digits.startswith("0"):
                remaining = digits[1:]
                if len(remaining) >= 9:
                    return "+212" + remaining[:9]
                return ""
            return ""
        except Exception:
            return ""

    def _extract_phone_number(self, text: str) -> str:
        """Extract and normalize Moroccan phone number to +212XXXXXXXXX.
        We search for common representations (with spaces, hyphens, dots, parentheses)
        and return the first valid normalized number.
        """
        # Tolerant pattern starting with Moroccan prefixes and capturing digits with separators
        pattern = r'(?:\+212|00212|212|0)[\d\s\-\.()]{7,20}'
        for match in re.finditer(pattern, text):
            candidate_raw = match.group(0)
            normalized = self._normalize_moroccan_phone(candidate_raw)
            if normalized:
                return normalized
        return ""
    
    def _extract_linkedin_profile(self, text: str) -> str:
        """Extract LinkedIn profile with improved regex"""
        # Try multiple LinkedIn patterns
        linkedin_patterns = [
            r'(https?:\/\/(?:[\w]+\.)?linkedin\.com\/[^\s,]+)',
            r'(linkedin\.com\/[^\s,]+)',
            r'(https?:\/\/[^\s]*linkedin[^\s]*)',
        ]
        
        for pattern in linkedin_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                linkedin = match.group(1)
                
                # Clean and validate the URL
                if not linkedin.startswith('http'):
                    linkedin = 'https://' + linkedin
                
                # Remove trailing punctuation
                linkedin = re.sub(r'[.,;!?]+$', '', linkedin)
                
                return linkedin
        
        return ""
    
    def _extract_birth_date(self, text: str) -> Optional[datetime.date]:
        """Extract birth date with improved pattern matching"""
        # Multiple date patterns
        date_patterns = [
            r'\b(?:0?[1-9]|[12][0-9]|3[01])[/\-](?:0?[1-9]|1[012])[/\-](?:19|20)\d{2}\b',
            r'\b(?:19|20)\d{2}[/\-](?:0?[1-9]|1[012])[/\-](?:0?[1-9]|[12][0-9]|3[01])\b',
            r'\b(?:0?[1-9]|[12][0-9]|3[01])\s+(?:janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+(?:19|20)\d{2}\b',
            r'\b(?:janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+(?:0?[1-9]|[12][0-9]|3[01])\s*,\s*(?:19|20)\d{2}\b',
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    date_str = match.group()
                    
                    # Handle French month names
                    month_map = {
                        'janvier': '01', 'février': '02', 'mars': '03', 'avril': '04',
                        'mai': '05', 'juin': '06', 'juillet': '07', 'août': '08',
                        'septembre': '09', 'octobre': '10', 'novembre': '11', 'décembre': '12'
                    }
                    
                    for month_name, month_num in month_map.items():
                        date_str = date_str.replace(month_name, month_num)
                    
                    # Try different date formats
                    for fmt in ['%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d', '%d %m %Y', '%d %m, %Y']:
                        try:
                            return datetime.strptime(date_str, fmt).date()
                        except ValueError:
                            continue
                            
                except Exception as e:
                    logger.error(f"Error parsing date {date_str}: {str(e)}")
                    continue
        
        return None
    
    def _extract_name_improved(self, text: str) -> Dict:
        """Extract name using explicit Moroccan-friendly rules.
        Rule:
        - Take the first plausible full-name line.
        - Last name = first token (with support for compounds like 'El Amrani', 'Ait Ben').
        - First name = remaining tokens joined.
        - Title-case the result.
        """
        lines = text.split('\n')

        # Common words that should not appear in a name line
        skip_words = {
            'email', 'e-mail', 'téléphone', 'telephone', 'phone', 'tel', 'adresse', 'address',
            'cv', 'resume', 'profil', 'profile', 'linkedin', 'github', 'portefeuille', 'portfolio',
            'développeur', 'developer', 'ingénieur', 'engineer', 'manager', 'directeur', 'objective'
        }

        # Known Moroccan/Maghrebi last-name prefixes to consider as part of the last name
        last_name_prefixes = {'el', 'al', 'ait', 'ben', 'ibn', 'oulad', 'ould', 'bni'}

        def parse_fullname(line: str) -> Optional[Dict]:
            # Keep letters, apostrophes and hyphens; normalize spaces
            cleaned = re.sub(r"[^A-Za-zÀ-ÿ'\-\s]", ' ', line)
            cleaned = re.sub(r"\s+", ' ', cleaned).strip()
            if len(cleaned) < 4:
                return None
            tokens = [t for t in cleaned.split(' ') if t]
            if len(tokens) < 2:
                return None

            # Detect compound last names starting with a known prefix
            first = tokens[0].lower()
            last_name_tokens = [tokens[0]]
            start_index_for_firstname = 1
            if first in last_name_prefixes and len(tokens) >= 3:
                # Include the second token in the last name (e.g., 'El Amrani')
                last_name_tokens.append(tokens[1])
                start_index_for_firstname = 2

            last_name = ' '.join(last_name_tokens).title()
            first_name = ' '.join(tokens[start_index_for_firstname:]).title()
            if not first_name:
                return None
            return {'first_name': first_name, 'last_name': last_name}

        # Scan early lines for the first plausible name line
        for line in lines[:20]:
            line_stripped = line.strip()
            if not line_stripped or len(line_stripped) > 80:
                continue
            lower = line_stripped.lower()
            if any(w in lower for w in skip_words):
                continue
            # Must contain at least two alphabetic tokens
            if len(re.findall(r"[A-Za-zÀ-ÿ]+", line_stripped)) < 2:
                continue
            parsed = parse_fullname(line_stripped)
            if parsed:
                return parsed

        return {'first_name': '', 'last_name': ''}
    
    def _extract_address(self, text: str) -> str:
        """Extract the most plausible address from free text.
        Strategy: scan lines for street-like patterns or the presence of a known city/country,
        score candidates, and return the best one cleaned and nicely formatted.
        """
        def normalize_spaces(s: str) -> str:
            s = re.sub(r'\s+', ' ', s)
            s = re.sub(r'\s*,\s*', ', ', s)
            return s.strip()

        def has_city_or_country(s_lower: str) -> bool:
            return any(k in s_lower for k in self.city_keywords) or any(k in s_lower for k in self.country_keywords)

        # Break into lines; also consider merging short lines with the following line
        raw_lines = [ln.strip() for ln in text.split('\n') if ln.strip()]
        if not raw_lines:
            return ""

        street_pattern = re.compile(
            r'\b(\d{1,4}\s+)?(rue|avenue|av\.?|bd\.?|boulevard|impasse|place|allée|allee|quartier|lotissement|lot|residence|res\.|appartement|appt|chemin|route|street|st\.?|road|rd\.?|lane|ln\.?|drive|dr\.?)\b',
            re.IGNORECASE)
        postal_pattern = re.compile(r'\b\d{4,6}\b')

        best_line = ''
        best_score = 0

        for idx, line in enumerate(raw_lines):
            # Remove common labels
            line_wo_label = re.sub(r'^(adresse|address|city|ville|pays|country)\s*[:\-]\s*', '', line, flags=re.IGNORECASE)
            candidate = line_wo_label
            if len(candidate) < 10 and idx + 1 < len(raw_lines):
                # merge with next line if too short
                candidate = candidate + ', ' + raw_lines[idx + 1]
            cand_lower = candidate.lower()

            score = 0
            if street_pattern.search(candidate):
                score += 3
            if postal_pattern.search(candidate):
                score += 2
            if any(city in cand_lower for city in self.city_keywords):
                score += 3
            if any(country in cand_lower for country in self.country_keywords):
                score += 2

            if score == 0 and has_city_or_country(cand_lower):
                score = 2  # minimal score if contains a city or country

            if score > 0:
                candidate = normalize_spaces(candidate)
                # Expand to include next line if it likely continues the address
                if idx + 1 < len(raw_lines):
                    nxt = raw_lines[idx + 1]
                    nxt_lower = nxt.lower()
                    if (has_city_or_country(nxt_lower) or street_pattern.search(nxt) or postal_pattern.search(nxt)) and len(nxt) <= 80:
                        extended = normalize_spaces(candidate + ', ' + nxt)
                        # increase score slightly if extension adds value
                        ext_score = score + 1
                        if ext_score > best_score:
                            best_line = extended
                            best_score = ext_score
                            continue

                if score > best_score:
                    best_line = candidate
                    best_score = score

        if not best_line:
            return ""

        # Title-case for nicer formatting (handles 'rabat,maroc' → 'Rabat, Maroc')
        formatted = best_line.title()
        # Preserve common prepositions in lower-case
        for small in [' De ', ' Du ', ' Des ', ' Et ', ' La ', ' Le ', ' Les ', " D'", " L'"]:
            formatted = formatted.replace(small, small.lower())

        # Limit overly long addresses
        if len(formatted) > 150:
            formatted = formatted[:150].rstrip()

        return formatted
    
    def _detect_gender(self, text: str) -> str:
        """Detect gender from text content"""
        male_score = 0
        female_score = 0
        
        for pattern in self.patterns['gender_indicators']['male']:
            if re.search(pattern, text, re.IGNORECASE):
                male_score += 1
        
        for pattern in self.patterns['gender_indicators']['female']:
            if re.search(pattern, text, re.IGNORECASE):
                female_score += 1
        
        if male_score > female_score:
            return "Homme"
        elif female_score > male_score:
            return "Femme"
        else:
            return ""
    
    def _create_default_candidate(self) -> Dict:
        """Create a default candidate structure when parsing fails"""
        return {
            'last_name': '',
            'first_name': '',
            'email': '',
            'phone': '',
            'birth_date': None,
            'address': '',
            'gender': '',
            'photo': None,
            'linkedin_profile': ''
        }
    
    def validate_candidate_data(self, data: Dict) -> Tuple[bool, List[str]]:
        """Validate extracted candidate data"""
        errors = []
        
        if not data.get('last_name'):
            errors.append("Nom de famille requis")
        if not data.get('first_name'):
            errors.append("Prénom requis")
        if not data.get('email'):
            errors.append("Email requis")
        elif not re.match(self.patterns['email'], data['email']):
            errors.append("Format d'email invalide")
        
        # Phone validation: strictly '+212' followed by 9 digits
        if data.get('phone'):
            if not re.match(r'^\+212\d{9}$', data['phone']):
                errors.append("Format de téléphone invalide (+212XXXXXXXXX)")
        
        return len(errors) == 0, errors
