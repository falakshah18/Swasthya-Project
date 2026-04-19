from __future__ import annotations

import json
import math
import re
import difflib
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import pandas as pd
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from sklearn.ensemble import RandomForestClassifier
from django.core.mail import send_mail
from django.conf import settings

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
FACILITY_FILE = DATA_DIR / "facilities.json"
TRAIN_FILE = DATA_DIR / "Training.csv"
DESC_FILE = DATA_DIR / "symptom_Description.csv"
PRECAUTION_FILE = DATA_DIR / "symptom_precaution.csv"
SEVERITY_FILE = DATA_DIR / "Symptom_severity.csv"


UI_TEXT = {
    "en": {
        "app_title": "SwasthyaSaathi",
        "tagline": "AI rural health triage assistant for patients and ASHA workers",
        "chat": "Chat",
        "nearby": "Nearby Care",
        "emergency": "Emergency Guide",
        "asha": "ASHA Worker",
        "reminders": "Medicine",
        "profile": "Profile",
        "placeholder": "Describe symptoms, age, duration, or severity...",
        "send": "Send",
        "voice": "Voice",
        "quick_title": "Quick symptom buttons",
        "nearby_title": "Nearby Care",
        "nearby_subtitle": "Hospitals, clinics and pharmacies close to you",
        "all": "All",
        "hospital": "Hospital",
        "clinic": "Clinic",
        "pharmacy": "Pharmacy",
        "call": "Call",
        "directions": "Directions",
        "open_now": "Open now",
        "emergency_header": "Emergency First Aid",
        "emergency_sub": "Quick help for common emergencies",
        "call_108": "Call 108",
        "tap_steps": "Tap to view steps",
        "warning": "Warning",
        "asha_title": "ASHA Worker Mode",
        "asha_subtitle": "Manage patient follow-up and quick triage",
        "patients": "Patients",
        "high_priority": "High Priority",
        "today": "Today",
        "pending": "Pending",
        "add_patient": "Add New Patient",
        "full_name": "Full Name",
        "age": "Age",
        "gender": "Gender",
        "village": "Village",
        "phone": "Phone",
        "condition": "Condition",
        "priority": "Priority",
        "low": "Low",
        "medium": "Medium",
        "high": "High",
        "add_patient_btn": "Add Patient",
        "quick_triage": "Quick Triage",
        "medicine_title": "Medicine Reminder",
        "medicine_subtitle": "Track doses and daily medicines",
        "daily": "Daily",
        "pending_label": "Pending",
        "taken": "Taken",
        "mark_taken": "Mark Taken",
        "mark_untaken": "Mark Untaken",
        "profile_subtitle": "Support, helplines and app details",
        "emergency_numbers": "Emergency Numbers",
        "about": "About",
        "about_text": "This multilingual symptom checker supports rural patients, ASHA workers and district health teams.",
        "disclaimer": "Disclaimer",
        "disclaimer_text": "This app does not replace a doctor. In emergencies, go to the nearest hospital or call 108.",
        "prof_age": "Age",
        "prof_gen": "Gender",
        "prof_med": "Major Health Conditions",
        "prof_history": "Past Consultations",
        "prof_symp": "Symptoms:",
        "prof_diag": "Likely Condition:",
        "prof_no_history": "No past consultations found.",
        "prof_edit": "Edit",
        "prof_edit_title": "Edit Profile",
        "prof_allergies": "Allergies",
        "btn_cancel": "Cancel",
        "btn_save": "Save Changes",
        "chat_greeting": "Hello! I am SwasthyaSaathi. Tell me your symptoms in your language. You can type things like fever, chest pain, vomiting, child, 3 days, severe.",
        "typing": "Analyzing symptoms and matching them with the health knowledge base...",
        "result_reason": "Reason",
        "recommended_facility": "Recommended facility",
        "view_nearby": "View Nearby",
        "likely_conditions": "Likely conditions",
        "matched_symptoms": "Matched symptoms",
        "next_question": "Suggested next question",
        "assistant_insight": "Assistant insight",
        "no_recognized": "I could not clearly identify the symptoms yet. Please mention the main symptom, age group, and how long it has been happening.",
        "self_care": "Self-care",
        "visit_clinic": "Visit clinic",
        "emergency_level": "Emergency",
        "desktop_hint": "Works on full desktop and mobile screens",
        "voice_not_supported": "Speech recognition is not supported in this browser.",
        "bot_error": "Could not reach assistant. Please try again.",
    },
    "hi": {
        "app_title": "स्वास्थ्यसाथी",
        "tagline": "मरीजों, परिवारों और आशा कार्यकर्ताओं के लिए एआई ग्रामीण स्वास्थ्य ट्रायेज सहायक",
        "chat": "चैट",
        "nearby": "नज़दीकी सेवा",
        "emergency": "आपात गाइड",
        "asha": "आशा कार्यकर्ता",
        "reminders": "दवा",
        "profile": "प्रोफ़ाइल",
        "placeholder": "लक्षण, उम्र, कितने दिन से है, या गंभीरता लिखें...",
        "send": "भेजें",
        "voice": "आवाज़",
        "quick_title": "त्वरित लक्षण बटन",
        "nearby_title": "नज़दीकी सेवा",
        "nearby_subtitle": "आपके पास के अस्पताल, क्लिनिक और फार्मेसी",
        "all": "सभी",
        "hospital": "अस्पताल",
        "clinic": "क्लिनिक",
        "pharmacy": "फार्मेसी",
        "call": "कॉल",
        "directions": "दिशा",
        "open_now": "अभी खुला",
        "emergency_header": "आपात प्राथमिक सहायता",
        "emergency_sub": "सामान्य आपात स्थितियों के लिए त्वरित सहायता",
        "call_108": "108 पर कॉल करें",
        "tap_steps": "कदम देखने के लिए टैप करें",
        "warning": "चेतावनी",
        "asha_title": "आशा कार्यकर्ता मोड",
        "asha_subtitle": "रोगी फॉलो-अप और त्वरित ट्रायेज प्रबंधित करें",
        "patients": "रोगी",
        "high_priority": "उच्च प्राथमिकता",
        "today": "आज",
        "pending": "लंबित",
        "add_patient": "नया रोगी जोड़ें",
        "full_name": "पूरा नाम",
        "age": "उम्र",
        "gender": "लिंग",
        "village": "गाँव",
        "phone": "फोन",
        "condition": "स्थिति",
        "priority": "प्राथमिकता",
        "low": "कम",
        "medium": "मध्यम",
        "high": "उच्च",
        "add_patient_btn": "रोगी जोड़ें",
        "quick_triage": "त्वरित ट्रायेज",
        "medicine_title": "दवा रिमाइंडर",
        "medicine_subtitle": "खुराक और रोज़ की दवाएँ ट्रैक करें",
        "daily": "दैनिक",
        "pending_label": "लंबित",
        "taken": "ली गई",
        "mark_taken": "ली गई चिह्नित करें",
        "mark_untaken": "न ली गई चिह्नित करें",
        "profile_subtitle": "सहायता, हेल्पलाइन और ऐप विवरण",
        "emergency_numbers": "आपात नंबर",
        "about": "परिचय",
        "about_text": "यह बहुभाषी लक्षण चेकर ग्रामीण मरीजों, आशा कार्यकर्ताओं और जिला स्वास्थ्य टीमों की मदद करता है।",
        "disclaimer": "अस्वीकरण",
        "disclaimer_text": "यह ऐप डॉक्टर का विकल्प नहीं है। आपात स्थिति में नज़दीकी अस्पताल जाएँ या 108 पर कॉल करें।",
        "prof_age": "उम्र",
        "prof_gen": "लिंग",
        "prof_med": "पिछली स्वास्थ्य स्थितियां",
        "prof_history": "पिछले परामर्श",
        "prof_symp": "लक्षण:",
        "prof_diag": "संभावित स्थिति:",
        "prof_no_history": "कोई पिछला परामर्श नहीं मिला।",
        "prof_edit": "संपादित करें",
        "prof_edit_title": "प्रोफ़ाइल संपादित करें",
        "prof_allergies": "एलर्जी",
        "btn_cancel": "रद्द करें",
        "btn_save": "परिवर्तन सहेजें",
        "chat_greeting": "नमस्ते! मैं स्वास्थ्यसाथी हूँ। अपनी भाषा में लक्षण बताइए। आप बुखार, छाती में दर्द, उल्टी, बच्चा, 3 दिन, गंभीर जैसे शब्द लिख सकते हैं।",
        "typing": "लक्षणों का विश्लेषण कर रहा हूँ और स्वास्थ्य ज्ञान आधार से मिला रहा हूँ...",
        "result_reason": "कारण",
        "recommended_facility": "सुझाई गई सुविधा",
        "view_nearby": "नज़दीकी देखें",
        "likely_conditions": "संभावित स्थितियाँ",
        "matched_symptoms": "पहचाने गए लक्षण",
        "next_question": "अगला सुझाया सवाल",
        "assistant_insight": "सहायक की समझ",
        "no_recognized": "मैं अभी लक्षणों को स्पष्ट रूप से नहीं पहचान पाया। कृपया मुख्य लक्षण, उम्र और कितने समय से है यह बताइए।",
        "self_care": "स्व-देखभाल",
        "visit_clinic": "क्लिनिक जाएँ",
        "emergency_level": "आपातकाल",
        "desktop_hint": "पूर्ण डेस्कटॉप और मोबाइल स्क्रीन पर काम करता है",
        "voice_not_supported": "इस ब्राउज़र में स्पीच रिकग्निशन उपलब्ध नहीं है।",
        "bot_error": "सहायक से संपर्क नहीं हो सका। कृपया फिर से प्रयास करें।",
    },
    "gu": {
        "app_title": "સ્વાસ્થ્યસાથી",
        "tagline": "દર્દીઓ, પરિવાર અને આશા કાર્યકર્તાઓ માટે એઆઇ ગ્રામ્ય આરોગ્ય ટ્રાયેજ સહાયક",
        "chat": "ચેટ",
        "nearby": "નજીકની સેવા",
        "emergency": "ઇમર્જન્સી માર્ગદર્શિકા",
        "asha": "આશા કાર્યકર",
        "reminders": "દવા",
        "profile": "પ્રોફાઇલ",
        "placeholder": "લક્ષણ, ઉંમર, કેટલા દિવસથી છે, અથવા ગંભીરતા લખો...",
        "send": "મોકલો",
        "voice": "આવાજ",
        "quick_title": "ઝડપી લક્ષણ બટન",
        "nearby_title": "નજીકની સેવા",
        "nearby_subtitle": "તમારા નજીકની હોસ્પિટલ, ક્લિનિક અને ફાર્મસી",
        "all": "બધું",
        "hospital": "હોસ્પિટલ",
        "clinic": "ક્લિનિક",
        "pharmacy": "ફાર્મસી",
        "call": "કૉલ",
        "directions": "દિશા",
        "open_now": "હમણાં ખુલ્લું",
        "emergency_header": "ઇમર્જન્સી પ્રાથમિક સહાય",
        "emergency_sub": "સામાન્ય ઇમર્જન્સી માટે ઝડપી મદદ",
        "call_108": "108 પર કૉલ કરો",
        "tap_steps": "સ્ટેપ્સ જોવા માટે ટેપ કરો",
        "warning": "ચેતવણી",
        "asha_title": "આશા કાર્યકર મોડ",
        "asha_subtitle": "દર્દી ફોલોઅપ અને ઝડપી ટ્રાયેજ મેનેજ કરો",
        "patients": "દર્દીઓ",
        "high_priority": "ઉચ્ચ પ્રાથમિકતા",
        "today": "આજે",
        "pending": "બાકી",
        "add_patient": "નવો દર્દી ઉમેરો",
        "full_name": "પૂર્ણ નામ",
        "age": "ઉંમર",
        "gender": "લિંગ",
        "village": "ગામ",
        "phone": "ફોન",
        "condition": "સ્થિતિ",
        "priority": "પ્રાથમિકતા",
        "low": "ઓછી",
        "medium": "મધ્યમ",
        "high": "ઉચ્ચ",
        "add_patient_btn": "દર્દી ઉમેરો",
        "quick_triage": "ઝડપી ટ્રાયેજ",
        "medicine_title": "દવા રિમાઇન્ડર",
        "medicine_subtitle": "ડોઝ અને દૈનિક દવાઓ ટ્રૅક કરો",
        "daily": "દૈનિક",
        "pending_label": "બાકી",
        "taken": "લીધી",
        "mark_taken": "લીધી તરીકે ચિહ્નિત કરો",
        "mark_untaken": "ન લીધી તરીકે ચિહ્નિત કરો",
        "profile_subtitle": "મદદ, હેલ્પલાઇન અને એપ વિગતો",
        "emergency_numbers": "ઇમર્જન્સી નંબર",
        "about": "વિશે",
        "about_text": "આ બહુભાષી લક્ષણ ચેકર ગ્રામ્ય દર્દીઓ, આશા કાર્યકર્તાઓ અને જિલ્લા આરોગ્ય ટીમોને મદદ કરે છે.",
        "disclaimer": "ડિસ્ક્લેમર",
        "disclaimer_text": "આ એપ ડૉક્ટરનું સ્થાન લેતી નથી. ઇમર્જન્સીમાં નજીકની હોસ્પિટલ જાઓ અથવા 108 પર કૉલ કરો.",
        "prof_age": "ઉંમર",
        "prof_gen": "લિંગ",
        "prof_med": "અગાઉની સ્વાસ્થ્ય સ્થિતિ",
        "prof_history": "ભૂતકાળના પરામર્શ",
        "prof_symp": "લક્ષણો:",
        "prof_diag": "સંભવિત સ્થિતિ:",
        "prof_no_history": "કોઈ ભૂતકાળનો પરામર્શ મળ્યો નથી.",
        "prof_edit": "સંપાદિત કરો",
        "prof_edit_title": "પ્રોફાઇલ સંપાદિત કરો",
        "prof_allergies": "એલર્જી",
        "btn_cancel": "રદ કરો",
        "btn_save": "ફેરફારો સાચવો",
        "chat_greeting": "નમસ્તે! હું સ્વાસ્થ્યસાથી છું. તમારી ભાષામાં લક્ષણ લખો. તમે તાવ, છાતીમાં દુખાવો, ઊલટી, બાળક, 3 દિવસ, ગંભીર જેવા શબ્દો લખી શકો છો.",
        "typing": "લક્ષણોનું વિશ્લેષણ કરી રહ્યો છું અને આરોગ્ય જ્ઞાન આધાર સાથે મેળ ખવડાવી રહ્યો છું...",
        "result_reason": "કારણ",
        "recommended_facility": "ભલામણ કરાયેલ સુવિધા",
        "view_nearby": "નજીક જુઓ",
        "likely_conditions": "સંભવિત સ્થિતિઓ",
        "matched_symptoms": "ઓળખાયેલા લક્ષણો",
        "next_question": "આગળ પૂછવાનું સૂચિત પ્રશ્ન",
        "assistant_insight": "સહાયકની સમજ",
        "no_recognized": "હું હજી લક્ષણોને સ્પષ્ટ રીતે ઓળખી શક્યો નથી. કૃપા કરીને મુખ્ય લક્ષણ, ઉંમર અને કેટલા સમયથી છે તે લખો.",
        "self_care": "સ્વ-સંભાળ",
        "visit_clinic": "ક્લિનિક જાઓ",
        "emergency_level": "ઇમર્જન્સી",
        "desktop_hint": "પૂર્ણ ડેસ્કટોપ અને મોબાઇલ સ્ક્રીન પર કામ કરે છે",
        "voice_not_supported": "આ બ્રાઉઝરમાં સ્પીચ રેકગ્નિશન ઉપલબ્ધ નથી.",
        "bot_error": "સહાયક સુધી પહોંચી શકાયું નથી. કૃપા કરીને ફરી પ્રયાસ કરો.",
    },
    "mr": {
        "app_title": "स्वास्थ्यसाथी",
        "tagline": "रुग्ण, कुटुंबे आणि आशा कार्यकर्त्यांसाठी एआय ग्रामीण आरोग्य ट्रायेज सहाय्यक",
        "chat": "चॅट",
        "nearby": "जवळची सेवा",
        "emergency": "आपत्कालीन मार्गदर्शक",
        "asha": "आशा कार्यकर्ता",
        "reminders": "औषध",
        "profile": "प्रोफाइल",
        "placeholder": "लक्षणे, वय, किती दिवसांपासून आहे, किंवा तीव्रता लिहा...",
        "send": "पाठवा",
        "voice": "आवाज",
        "quick_title": "जलद लक्षण बटणे",
        "nearby_title": "जवळची सेवा",
        "nearby_subtitle": "तुमच्या जवळची रुग्णालये, क्लिनिक आणि फार्मसी",
        "all": "सर्व",
        "hospital": "रुग्णालय",
        "clinic": "क्लिनिक",
        "pharmacy": "फार्मसी",
        "call": "कॉल",
        "directions": "दिशा",
        "open_now": "आता खुले",
        "emergency_header": "आपत्कालीन प्रथमोपचार",
        "emergency_sub": "सामान्य आपत्कालीन स्थितीसाठी जलद मदत",
        "call_108": "108 ला कॉल करा",
        "tap_steps": "पायऱ्या पाहण्यासाठी टॅप करा",
        "warning": "इशारा",
        "asha_title": "आशा कार्यकर्ता मोड",
        "asha_subtitle": "रुग्ण फॉलो-अप आणि जलद ट्रायेज व्यवस्थापित करा",
        "patients": "रुग्ण",
        "high_priority": "उच्च प्राधान्य",
        "today": "आज",
        "pending": "प्रलंबित",
        "add_patient": "नवीन रुग्ण जोडा",
        "full_name": "पूर्ण नाव",
        "age": "वय",
        "gender": "लिंग",
        "village": "गाव",
        "phone": "फोन",
        "condition": "स्थिती",
        "priority": "प्राधान्य",
        "low": "कमी",
        "medium": "मध्यम",
        "high": "उच्च",
        "add_patient_btn": "रुग्ण जोडा",
        "quick_triage": "जलद ट्रायेज",
        "medicine_title": "औषध स्मरणपत्र",
        "medicine_subtitle": "डोस आणि दैनंदिन औषधे ट्रॅक करा",
        "daily": "दैनंदिन",
        "pending_label": "प्रलंबित",
        "taken": "घेतले",
        "mark_taken": "घेतले म्हणून चिन्हांकित करा",
        "mark_untaken": "न घेतले म्हणून चिन्हांकित करा",
        "profile_subtitle": "मदत, हेल्पलाइन आणि अॅप तपशील",
        "emergency_numbers": "आपत्कालीन क्रमांक",
        "about": "माहिती",
        "about_text": "हा बहुभाषिक लक्षण तपासक ग्रामीण रुग्ण, आशा कार्यकर्ते आणि जिल्हा आरोग्य पथकांना मदत करतो.",
        "disclaimer": "अस्वीकरण",
        "disclaimer_text": "हे अॅप डॉक्टरची जागा घेत नाही. आपत्कालीन स्थितीत जवळच्या रुग्णालयात जा किंवा 108 ला कॉल करा.",
        "prof_age": "वय",
        "prof_gen": "लिंग",
        "prof_med": "पूर्वीची आरोग्याची स्थिती",
        "prof_history": "मागील सल्लामसलत",
        "prof_symp": "लक्षणे:",
        "prof_diag": "संभाव्य स्थिती:",
        "prof_no_history": "कोणतीही मागील सल्लामसलत आढळली नाही.",
        "prof_edit": "संपादित करा",
        "prof_edit_title": "प्रोफाइल संपादित करा",
        "prof_allergies": "ऍलर्जी",
        "btn_cancel": "रद्द करा",
        "btn_save": "बदल जतन करा",
        "chat_greeting": "नमस्कार! मी स्वास्थ्यसाथी आहे. तुमच्या भाषेत लक्षणे सांगा. ताप, छातीत दुखणे, उलटी, मूल, 3 दिवस, गंभीर असे शब्द लिहू शकता.",
        "typing": "लक्षणांचे विश्लेषण करून आरोग्य ज्ञानाधाराशी जुळवत आहे...",
        "result_reason": "कारण",
        "recommended_facility": "शिफारस केलेली सुविधा",
        "view_nearby": "जवळचे पहा",
        "likely_conditions": "संभाव्य स्थिती",
        "matched_symptoms": "ओळखलेली लक्षणे",
        "next_question": "पुढचा सुचवलेला प्रश्न",
        "assistant_insight": "सहाय्यक समज",
        "no_recognized": "मी अजून लक्षणे स्पष्टपणे ओळखू शकलो नाही. कृपया मुख्य लक्षण, वयोगट आणि किती काळापासून आहे ते सांगा.",
        "self_care": "स्वतःची काळजी",
        "visit_clinic": "क्लिनिकला जा",
        "emergency_level": "आपत्कालीन",
        "desktop_hint": "पूर्ण डेस्कटॉप आणि मोबाइल स्क्रीनवर चालते",
        "voice_not_supported": "या ब्राउझरमध्ये स्पीच रिकग्निशन उपलब्ध नाही.",
        "bot_error": "सहाय्यकाशी संपर्क होऊ शकला नाही. कृपया पुन्हा प्रयत्न करा.",
    },
    "ta": {
        "app_title": "ஸ்வாஸ்த்யசாத்தி",
        "tagline": "நோயாளிகள், குடும்பங்கள் மற்றும் ஆஷா பணியாளர்களுக்கான AI கிராமப்புற சுகாதார ட்ரயாஜ் உதவி",
        "chat": "அரட்டை",
        "nearby": "அருகிலுள்ள சேவை",
        "emergency": "அவசர வழிகாட்டி",
        "asha": "ஆஷா பணியாளர்",
        "reminders": "மருந்து",
        "profile": "சுயவிவரம்",
        "placeholder": "அறிகுறி, வயது, எத்தனை நாட்களாக உள்ளது, அல்லது தீவிரம் எழுதுங்கள்...",
        "send": "அனுப்பு",
        "voice": "குரல்",
        "quick_title": "விரைவு அறிகுறி பொத்தான்கள்",
        "nearby_title": "அருகிலுள்ள சேவை",
        "nearby_subtitle": "உங்கள் அருகிலுள்ள மருத்துவமனை, கிளினிக் மற்றும் மருந்தகம்",
        "all": "அனைத்தும்",
        "hospital": "மருத்துவமனை",
        "clinic": "கிளினிக்",
        "pharmacy": "மருந்தகம்",
        "call": "அழைப்பு",
        "directions": "வழி",
        "open_now": "இப்போது திறந்துள்ளது",
        "emergency_header": "அவசர முதல் உதவி",
        "emergency_sub": "பொதுவான அவசர நிலைகளுக்கு விரைவு உதவி",
        "call_108": "108 அழைக்கவும்",
        "tap_steps": "படிகளை பார்க்க தட்டவும்",
        "warning": "எச்சரிக்கை",
        "asha_title": "ஆஷா பணியாளர் முறை",
        "asha_subtitle": "நோயாளர் பின்தொடர்பு மற்றும் விரைவு ட்ரயாஜ் மேலாண்மை",
        "patients": "நோயாளிகள்",
        "high_priority": "உயர் முன்னுரிமை",
        "today": "இன்று",
        "pending": "நிலுவை",
        "add_patient": "புதிய நோயாளியை சேர்க்கவும்",
        "full_name": "முழுப் பெயர்",
        "age": "வயது",
        "gender": "பாலினம்",
        "village": "கிராமம்",
        "phone": "தொலைபேசி",
        "condition": "நிலை",
        "priority": "முன்னுரிமை",
        "low": "குறைவு",
        "medium": "நடுத்தரம்",
        "high": "உயர்",
        "add_patient_btn": "நோயாளியை சேர்க்கவும்",
        "quick_triage": "விரைவு ட்ரயாஜ்",
        "medicine_title": "மருந்து நினைவூட்டல்",
        "medicine_subtitle": "மாத்திரை நேரம் மற்றும் தினசரி மருந்துகளை கண்காணிக்கவும்",
        "daily": "தினசரி",
        "pending_label": "நிலுவை",
        "taken": "எடுத்தது",
        "mark_taken": "எடுத்ததாக குறிக்கவும்",
        "mark_untaken": "எடுக்காததாக குறிக்கவும்",
        "profile_subtitle": "உதவி, உதவி எண்கள் மற்றும் செயலி விவரங்கள்",
        "emergency_numbers": "அவசர எண்கள்",
        "about": "பற்றி",
        "about_text": "இந்த பலமொழி அறிகுறி சரிபார்ப்பான் கிராமப்புற நோயாளிகள், ஆஷா பணியாளர்கள் மற்றும் மாவட்ட சுகாதார குழுக்களுக்கு உதவுகிறது.",
        "disclaimer": "பொறுப்புத்துறப்பு",
        "disclaimer_text": "இந்த செயலி மருத்துவருக்கு மாற்றாகாது. அவசரநிலையில் அருகிலுள்ள மருத்துவமனைக்கு செல்லவும் அல்லது 108 அழைக்கவும்.",
        "prof_age": "வயது",
        "prof_gen": "பாலினம்",
        "prof_med": "முந்தைய சுகாதார நிலைகள்",
        "prof_history": "கடந்த ஆலோசனைகள்",
        "prof_symp": "அறிகுறிகள்:",
        "prof_diag": "சாத்தியமான நிலை:",
        "prof_no_history": "முந்தைய ஆலோசனைகள் எதுவும் இல்லை.",
        "prof_edit": "திருத்து",
        "prof_edit_title": "சுயவிவரத்தை திருத்து",
        "prof_allergies": "ஒவ்வாமை",
        "btn_cancel": "ரத்துசெய்",
        "btn_save": "மாற்றங்களைச் சேமி",
        "chat_greeting": "வணக்கம்! நான் ஸ்வாஸ்த்யசாத்தி. உங்கள் மொழியில் அறிகுறிகளை எழுதுங்கள். காய்ச்சல், மார்பு வலி, வாந்தி, குழந்தை, 3 நாட்கள், கடுமை போன்ற சொற்களை எழுதலாம்.",
        "typing": "அறிகுறிகளை பகுப்பாய்வு செய்து சுகாதார அறிவு தரவுடன் பொருத்துகிறேன்...",
        "result_reason": "காரணம்",
        "recommended_facility": "பரிந்துரைக்கப்படும் சிகிச்சை மையம்",
        "view_nearby": "அருகிலுள்ளவை பார்க்கவும்",
        "likely_conditions": "சாத்தியமான நிலைகள்",
        "matched_symptoms": "பொருந்திய அறிகுறிகள்",
        "next_question": "அடுத்த பரிந்துரைக்கப்பட்ட கேள்வி",
        "assistant_insight": "உதவியாளர் கருத்து",
        "no_recognized": "அறிகுறிகளை நான் தெளிவாக அடையாளம் காண முடியவில்லை. முக்கிய அறிகுறி, வயது குழு மற்றும் எத்தனை நாட்களாக உள்ளது என்பதை எழுதுங்கள்.",
        "self_care": "சுய பராமரிப்பு",
        "visit_clinic": "கிளினிக்குச் செல்லவும்",
        "emergency_level": "அவசரம்",
        "desktop_hint": "முழு டெஸ்க்டாப் மற்றும் மொபைல் திரைகளில் வேலை செய்கிறது",
        "voice_not_supported": "இந்த உலாவியில் குரல் அடையாளம் ஆதரிக்கப்படவில்லை.",
        "bot_error": "உதவியாளரை அணுக முடியவில்லை. மீண்டும் முயற்சிக்கவும்.",
    },
}

QUICK_REPLIES = {
    "en": ["fever", "cough", "vomiting", "chest pain", "breathing problem", "child", "elderly", "3 days", "severe"],
    "hi": ["बुखार", "खांसी", "उल्टी", "छाती में दर्द", "सांस की तकलीफ़", "बच्चा", "बुज़ुर्ग", "3 दिन", "गंभीर"],
    "gu": ["તાવ", "ઉધરસ", "ઉલટી", "છાતીમાં દુખાવો", "શ્વાસમાં તકલીફ", "બાળક", "વૃદ્ધ", "3 દિવસ", "ગંભીર"],
    "mr": ["ताप", "खोकला", "उलटी", "छातीत दुखणे", "श्वास घेण्यास त्रास", "मूल", "ज्येष्ठ", "3 दिवस", "गंभीर"],
    "ta": ["காய்ச்சல்", "இருமல்", "வாந்தி", "மார்பு வலி", "மூச்சுத்திணறல்", "குழந்தை", "முதியவர்", "3 நாட்கள்", "கடுமை"],
}

EMERGENCY_ITEMS = {
    "en": [
        {"title": "Chest Pain", "icon": "❤️", "warning": "Possible cardiac emergency. Call 108.", "steps": ["Call 108 immediately", "Make the person sit and rest", "Loosen tight clothes", "Go to the nearest hospital"]},
        {"title": "Heavy Bleeding", "icon": "🩸", "warning": "Apply pressure and seek urgent care.", "steps": ["Apply direct pressure", "Keep injured area raised", "Do not remove soaked cloth", "Get emergency transport"]},
        {"title": "High Fever", "icon": "🌡️", "warning": "High fever in children or prolonged fever needs review.", "steps": ["Check temperature", "Give fluids", "Use light clothing", "Visit clinic if persistent"]},
        {"title": "Poisoning", "icon": "☠️", "warning": "Do not induce vomiting unless advised.", "steps": ["Call 108", "Keep poison sample", "Do not force food or drink", "Monitor breathing"]},
        {"title": "Choking", "icon": "🫁", "warning": "Act quickly if person cannot speak or breathe.", "steps": ["Encourage coughing if possible", "Give back blows if trained", "Call emergency help", "Go to the nearest hospital"]},
        {"title": "Seizure", "icon": "⚡", "warning": "Do not put anything in the mouth.", "steps": ["Clear the area", "Turn person on one side", "Time the seizure", "Call 108 if it lasts more than 5 minutes"]},
    ],
    "hi": [
        {"title": "छाती में दर्द", "icon": "❤️", "warning": "हृदय संबंधी आपात स्थिति हो सकती है। 108 पर कॉल करें।", "steps": ["तुरंत 108 पर कॉल करें", "व्यक्ति को बैठाकर आराम दें", "कसे कपड़े ढीले करें", "नज़दीकी अस्पताल जाएँ"]},
        {"title": "अधिक रक्तस्राव", "icon": "🩸", "warning": "दबाव डालें और तुरंत इलाज लें।", "steps": ["सीधा दबाव डालें", "घायल भाग ऊपर रखें", "भीगा कपड़ा न हटाएँ", "आपात वाहन की व्यवस्था करें"]},
        {"title": "तेज़ बुखार", "icon": "🌡️", "warning": "बच्चों में तेज़ बुखार या लंबे समय का बुखार जाँच योग्य है।", "steps": ["तापमान जाँचें", "तरल दें", "हल्के कपड़े पहनाएँ", "जारी रहे तो क्लिनिक जाएँ"]},
        {"title": "ज़हर", "icon": "☠️", "warning": "सलाह बिना उल्टी न कराएँ।", "steps": ["108 पर कॉल करें", "ज़हर का नमूना रखें", "खाना-पानी ज़बरदस्ती न दें", "सांस पर नज़र रखें"]},
        {"title": "दम घुटना", "icon": "🫁", "warning": "यदि व्यक्ति बोल या सांस नहीं ले पा रहा है तो तुरंत कार्रवाई करें।", "steps": ["संभव हो तो खांसने को कहें", "प्रशिक्षित हों तो बैक ब्लो दें", "आपात मदद बुलाएँ", "अस्पताल जाएँ"]},
        {"title": "दौरा", "icon": "⚡", "warning": "मुंह में कुछ न डालें।", "steps": ["आसपास की जगह खाली करें", "व्यक्ति को करवट दें", "समय नोट करें", "5 मिनट से ज़्यादा हो तो 108 पर कॉल करें"]},
    ],
    "gu": [
        {"title": "છાતીમાં દુખાવો", "icon": "❤️", "warning": "હૃદય સંબંધિત ઇમર્જન્સી હોઈ શકે. 108 પર કૉલ કરો.", "steps": ["તાત્કાલિક 108 પર કૉલ કરો", "વ્યક્તિને બેસાડીને આરામ આપો", "ટાઇટ કપડાં ઢીલા કરો", "નજીકની હોસ્પિટલ જાઓ"]},
        {"title": "વધારે રક્તસ્રાવ", "icon": "🩸", "warning": "દબાણ કરો અને તાત્કાલિક સારવાર લો.", "steps": ["સીધું દબાણ કરો", "ઇજાગ્રસ્ત ભાગ ઊંચો રાખો", "ભીનું કપડું ન કાઢો", "ઇમર્જન્સી વાહન ગોઠવો"]},
        {"title": "ઊંચો તાવ", "icon": "🌡️", "warning": "બાળકોમાં ઊંચો તાવ અથવા લાંબો તાવ ધ્યાનપાત્ર છે.", "steps": ["તાપમાન ચેક કરો", "દ્રવ આપો", "હળવા કપડાં પહેરાવો", "ચાલું રહે તો ક્લિનિક જાઓ"]},
        {"title": "ઝેર", "icon": "☠️", "warning": "સલાહ વિના ઊલટી ન કરાવો.", "steps": ["108 પર કૉલ કરો", "ઝેરનું નમૂનું રાખો", "જબરદસ્તી ખાવા-પીવા ન આપો", "શ્વાસ પર નજર રાખો"]},
        {"title": "ઘૂંટાવો", "icon": "🫁", "warning": "વ્યક્તિ બોલી કે શ્વાસ લઈ ન શકે તો ઝડપથી કાર્ય કરો.", "steps": ["શક્ય હોય તો ખાંસી કરવા કહો", "ટ્રેઇન્ડ હો તો બેક બ્લો આપો", "ઇમર્જન્સી મદદ બોલાવો", "હોસ્પિટલ જાઓ"]},
        {"title": "ઝટકા", "icon": "⚡", "warning": "મોઢામાં કશું ન મૂકો.", "steps": ["આસપાસ જગ્યા ખાલી કરો", "વ્યક્તિને બાજુ પર ફેરવો", "સમય નોંધો", "5 મિનિટથી વધુ થાય તો 108 પર કૉલ કરો"]},
    ],
    "mr": [
        {"title": "छातीत दुखणे", "icon": "❤️", "warning": "हृदयविकाराची आपत्कालीन स्थिती असू शकते. 108 ला कॉल करा.", "steps": ["ताबडतोब 108 ला कॉल करा", "व्यक्तीला बसवून विश्रांती द्या", "घट्ट कपडे सैल करा", "जवळच्या रुग्णालयात जा"]},
        {"title": "जास्त रक्तस्त्राव", "icon": "🩸", "warning": "दाब द्या आणि त्वरित उपचार घ्या.", "steps": ["थेट दाब द्या", "जखमी भाग वर ठेवा", "भिजलेले कापड काढू नका", "आपत्कालीन वाहन मिळवा"]},
        {"title": "उच्च ताप", "icon": "🌡️", "warning": "मुलांमध्ये उच्च ताप किंवा लांबकाळ ताप तपासणे आवश्यक आहे.", "steps": ["तापमान तपासा", "द्रव द्या", "हलके कपडे वापरा", "टिकून राहिल्यास क्लिनिकला जा"]},
        {"title": "विषबाधा", "icon": "☠️", "warning": "सल्ल्याशिवाय उलटी करू नका.", "steps": ["108 ला कॉल करा", "विषाचा नमुना ठेवा", "जबरीने खाऊ-पिऊ देऊ नका", "श्वासावर लक्ष ठेवा"]},
        {"title": "गुदमरल्यासारखे", "icon": "🫁", "warning": "व्यक्ती बोलू किंवा श्वास घेऊ शकत नसेल तर त्वरित कृती करा.", "steps": ["शक्य असल्यास खोकायला सांगा", "प्रशिक्षित असाल तर बॅक ब्लोज द्या", "आपत्कालीन मदत मागवा", "रुग्णालयात जा"]},
        {"title": "आकडी", "icon": "⚡", "warning": "तोंडात काहीही टाकू नका.", "steps": ["आसपासची जागा मोकळी करा", "व्यक्तीला एका बाजूला वळवा", "वेळ नोंदवा", "5 मिनिटांपेक्षा जास्त असल्यास 108 ला कॉल करा"]},
    ],
    "ta": [
        {"title": "மார்பு வலி", "icon": "❤️", "warning": "இதய அவசரநிலை இருக்கலாம். 108 அழைக்கவும்.", "steps": ["உடனே 108 அழைக்கவும்", "நபரை அமர வைத்து ஓய்வளிக்கவும்", "இறுக்கமான உடைகளை தளர்த்தவும்", "அருகிலுள்ள மருத்துவமனைக்குச் செல்லவும்"]},
        {"title": "அதிக இரத்தப்போக்கு", "icon": "🩸", "warning": "அழுத்தம் கொடுத்து உடனடி சிகிச்சை பெறவும்.", "steps": ["நேரடி அழுத்தம் கொடுக்கவும்", "காயம் பட்ட பகுதியை உயர்த்தி வைக்கவும்", "நனைந்த துணியை அகற்ற வேண்டாம்", "அவசர போக்குவரத்து ஏற்பாடு செய்யவும்"]},
        {"title": "அதிக காய்ச்சல்", "icon": "🌡️", "warning": "குழந்தைகளில் அதிக காய்ச்சல் அல்லது நீண்டகால காய்ச்சல் கவனிக்கப்பட வேண்டும்.", "steps": ["வெப்பநிலை பார்க்கவும்", "திரவம் கொடுக்கவும்", "லேசான உடை அணியவும்", "தொடர்ந்தால் கிளினிக்குச் செல்லவும்"]},
        {"title": "நச்சு தாக்கம்", "icon": "☠️", "warning": "ஆலோசனை இல்லாமல் வாந்தி வரவழைக்க வேண்டாம்.", "steps": ["108 அழைக்கவும்", "நச்சுப் பொருள் மாதிரியை வைத்திருங்கள்", "பலவந்தமாக உணவு அல்லது தண்ணீர் கொடுக்க வேண்டாம்", "மூச்சை கண்காணிக்கவும்"]},
        {"title": "மூச்சுத்திணறல்", "icon": "🫁", "warning": "நபர் பேசவோ மூச்செடுக்கவோ முடியாவிட்டால் உடனடி நடவடிக்கை அவசியம்.", "steps": ["இயன்றால் இருமச் சொல்லுங்கள்", "பயிற்சி இருந்தால் பின் தட்டுங்கள்", "அவசர உதவி அழைக்கவும்", "மருத்துவமனைக்குச் செல்லவும்"]},
        {"title": "விலக்கு", "icon": "⚡", "warning": "வாயில் எதையும் வைக்க வேண்டாம்.", "steps": ["சுற்றுப் பகுதியை காலியாக்கவும்", "நபரை ஓரமாக திருப்பவும்", "நேரம் பதிவு செய்யவும்", "5 நிமிடங்களுக்கு மேல் நீண்டால் 108 அழைக்கவும்"]},
    ],
}

SYMPTOM_ALIASES = {
    "itching": ["itching", "itchy", "खुजली", "ખંજવાળ", "खाज", "அரிப்பு"],
    "skin_rash": ["rash", "skin rash", "चकत्ते", "ચામડી પર દાદ", "पुरळ", "சரும சிரங்கு"],
    "continuous_sneezing": ["sneezing", " छींक", "છીંક", "शिंक", "தும்மல்"],
    "shivering": ["shivering", "कंपकंपी", "કાંપણી", "कापरे", "நடுக்கம்"],
    "chills": ["chills", "cold feeling", "ठंड लगना", "ઠંડી લાગી", "थंडी वाजणे", "சில்லு"],
    "joint_pain": ["joint pain", "body joint pain", "जोड़ों में दर्द", "સાંધાનો દુખાવો", "सांधेदुखी", "மூட்டு வலி"],
    "stomach_pain": ["stomach pain", "abdominal pain", "stomach ache", "belly ache", "tummy ache", "पेट दर्द", "પેટમાં દુખાવો", "पोटदुखी", "வயிற்று வலி"],
    "acidity": ["acidity", "acid reflux", "एसिडिटी", "એસિડિટી", "अॅसिडिटी", "அமிலத்தன்மை"],
    "ulcers_on_tongue": ["mouth ulcer", "tongue ulcer", "मुंह में छाले", "મોઢામાં છાલા", "तोंडात जखम", "வாய் புண்"],
    "muscle_wasting": ["weak muscles", "muscle loss"],
    "vomiting": ["vomiting", "vomit", "nausea", "throw up", "puking", "उल्टी", "ઉલટી", "उलटी", "வாந்தி"],
    "burning_micturition": ["burning urination", "urine burning", "पेशाब में जलन", "મૂત્રમાં દાહ", "लघवीत जळजळ", "சிறுநீரில் எரிச்சல்"],
    "spotting_ urination": ["spotting urination", "urine spotting"],
    "fatigue": ["fatigue", "weakness", "tired", "थकान", "નબળાઈ", "थकवा", "சோர்வு"],
    "weight_gain": ["weight gain", "वजन बढ़ना", "વજન વધવું", "वजन वाढणे", "எடை அதிகரித்தல்"],
    "anxiety": ["anxiety", "घबराहट", "ગભરાટ", "चि चिंता", "பதட்டம்"],
    "cold_hands_and_feets": ["cold hands", "cold feet", "हाथ पैर ठंडे", "હાથ પગ ઠંડા", "हात पाय थंड", "கை கால் குளிர்ச்சி"],
    "mood_swings": ["mood swings", "मूड बदलना", "મૂડ બદલાય", "मनःस्थिती बदल", "மனநிலை மாற்றம்"],
    "weight_loss": ["weight loss", "वजन कम", "વજન ઘટવું", "वजन कमी", "எடை குறைதல்"],
    "restlessness": ["restless", "बेचैनी", "બેચેની", "अस्वस्थ", "அமைதியின்மை"],
    "lethargy": ["lethargy", "low energy", "सुस्ती", "સુસ્તી", "आळस", "மந்தம்"],
    "patches_in_throat": ["throat patches", "गले में दाग", "ગળામાં પેચ"],
    "irregular_sugar_level": ["high sugar", "low sugar", "sugar", "शुगर", "સુગર", "साखर", "சர்க்கரை"],
    "cough": ["cough", "cold", "खांसी", "ઉધરસ", "खोकला", "இருமல்"],
    "high_fever": ["fever", "high fever", "temperature", "बुखार", "તાવ", "ताप", "காய்ச்சல்"],
    "sunken_eyes": ["sunken eyes", "धंसी आंखें", "આંખો અંદર પડેલી", "खोल गेलेले डोळे", "உள்ளிழுந்த கண்கள்"],
    "breathlessness": ["breathlessness", "difficulty breathing", "breathing problem", "shortness of breath", "breath problem", "hard to breathe", "hard to breath",
                       "सांस", "सांस की तकलीफ", "सांस लेने में दिक्कत",
                       "શ્વાસ", "શ્વાસ લેવામાં તકલીફ", "શ્વાસ ફૂલે", "શ્વાસ ફૂલવો", "શ્વાસ ચઢે",
                       "श्वास घेण्यास त्रास", "श्वास",
                       "மூச்சுத்திணறல்", "மூச்சு"],
    "sweating": ["sweating", "sweat", "पसीना", "ઘમો", "घाम", "வியர்வை"],
    "dehydration": ["dehydration", "dry mouth", "डिहाइड्रेशन", "ડિહાઇડ્રેશન", "निर्जलीकरण", "நீரிழப்பு"],
    "indigestion": ["indigestion", "अपच", "અપચો", "अपचन", "செரிமானக்கேடு"],
    "headache": ["headache", "head pain", "सिर दर्द", "માથાનો દુખાવો", "डोकेदुखी", "தலைவலி"],
    "yellowish_skin": ["yellow skin", "पीली त्वचा", "પીળી ચામડી", "पिवळी त्वचा", "மஞ்சள் தோல்"],
    "dark_urine": ["dark urine", "गहरा पेशाब", "ઘાટો મૂત્ર", "गडद लघवी", "கருந்திறுநீர்"],
    "nausea": ["nausea", "feel like vomiting", "मितली", "ઊલટી જેવું", "મળમળ", "குமட்டல்"],
    "loss_of_appetite": ["loss of appetite", "not eating", "भूख नहीं", "ભૂખ નથી", "भूक नाही", "சாப்பிட விருப்பமில்லை"],
    "pain_behind_the_eyes": ["pain behind eyes", "eye pain", "eyes pain", "आंख के पीछे दर्द", "આંખ પાછળ દુખાવો", "डोळ्यांच्या मागे दुखणे", "கண்களுக்கு பின்னால் வலி"],
    "back_pain": ["back pain", "पीठ दर्द", "પીઠનું દુખાવો", "पाठदुखी", "முதுகுவலி"],
    "constipation": ["constipation", "कब्ज", "કબજિયાત", "बद्धकोष्ठता", "மலச்சிக்கல்"],
    "abdominal_pain": ["abdominal pain", "stomach pain", "पेट दर्द", "પેટમાં દુખાવો", "पोटदुखी", "வயிற்று வலி"],
    "diarrhoea": ["diarrhea", "diarrhoea", "loose motion", "दस्त", "ઝાડા", "जुलाब", "வயிற்றுப்போக்கு"],
    "mild_fever": ["mild fever", "low fever", "हल्का बुखार", "હળવો તાવ", "सौम्य ताप", "லேசான காய்ச்சல்"],
    "yellow_urine": ["yellow urine", "पीला पेशाब", "પીળો મૂત્ર", "पिवळी लघवी", "மஞ்சள் சிறுநீர்"],
    "yellowing_of_eyes": ["yellow eyes", "आंख पीली", "આંખ પીળી", "डोळे पिवळे", "மஞ்சள் கண்கள்"],
    "acute_liver_failure": ["liver failure"],
    "fluid_overload": ["swelling with breathlessness", "body fluid overload"],
    "swelling_of_stomach": ["swollen stomach", "पेट फूलना", "પેટ ફૂલવું", "पोट सूजणे", "வயிறு வீக்கம்"],
    "swelled_lymph_nodes": ["swollen nodes", "गांठ", "ગાંઠ", "गाठी", "வீங்கிய லிம்ப்"],
    "malaise": ["malaise", "not feeling well", "feel sick", "feeling sick", "अस्वस्थ", "બરાબર નથી લાગતું", "अस्वस्थ वाटणे", "உடல்நலமில்லை"],
    "blurred_and_distorted_vision": ["blurred vision", "धुंधला दिखना", "ધૂંધળી દ્રષ્ટિ", "धूसर दिसणे", "மங்கலான பார்வை"],
    "phlegm": ["phlegm", "mucus", "बलगम", "કફ", "कफ", "சளி"],
    "throat_irritation": ["throat irritation", "sore throat", "throat pain", "throat ache", "गले में जलन", "ગળામાં ખંજવાળ", "घसा खवखवणे", "தொண்டை எரிச்சல்"],
    "redness_of_eyes": ["red eyes", "eye redness", "eyes redness", "आंख लाल", "આંખ લાલ", "डोळे लाल", "கண் சிவப்பு"],
    "sinus_pressure": ["sinus pressure", "नाक भारी", "સાયનસ", "सायनस", "சைனஸ் அழுத்தம்"],
    "runny_nose": ["runny nose", "नाक बहना", "नाक વહેવું", "नाक वाहणे", "மூக்கு ஒழுகுதல்"],
    "congestion": ["congestion", "blocked nose", "नाक बंद", "नाक બંધ", "नाक बंद", "மூக்கு அடைப்பு"],
    "chest_pain": ["chest pain", "heart pain", "छाती में दर्द", "છાતીમાં દુખાવો", "छातीत दुखणे", "மார்பு வலி"],
    "weakness_in_limbs": ["weakness in limbs", "हाथ पैर में कमजोरी", "હાથ પગમાં નબળાઈ", "हात पाय कमजोर", "கை கால் பலவீனம்"],
    "fast_heart_rate": ["fast heart rate", "palpitations", "दिल तेज", "હૃદય ધબકારા તેજ", "हृदयाचे ठोके वेगाने", "இதய துடிப்பு வேகம்"],
    "pain_during_bowel_movements": ["pain during stool", "मल त्याग में दर्द", "શૌચ વખતે દુખાવો", "शौचावेळी वेदना", "மல வெளியிடும் போது வலி"],
    "pain_in_anal_region": ["anal pain", "गुदा दर्द", "ગુદા દુખાવો", "गुदद्वार वेदना", "குடல்பகுதி வலி"],
    "bloody_stool": ["blood in stool", "मल में खून", "મલમાં લોહી", "शौचात रक्त", "மலத்தில் இரத்தம்"],
    "irritation_in_anus": ["anus irritation", "गुदा जलन", "ગુદામાં જળન", "गुदप्रदेश खाज", "குடல்பகுதி எரிச்சல்"],
    "neck_pain": ["neck pain", "गर्दन दर्द", "ગરદન દુખાવો", "मान दुखणे", "கழுத்து வலி"],
    "dizziness": ["dizziness", "giddiness", "चक्कर", "ચક્કર", "गरगरणे", "தலைச்சுற்றல்"],
    "cramps": ["cramps", "ऐंठन", "એંઠણ", "गोळे येणे", "வலி பிடித்தல்"],
    "bruising": ["bruising", "नील पड़ना", "સોજા સાથે કાળો ડાઘ", "सूज आणि काळे डाग", "அடிபட்ட தழும்பு"],
    "obesity": ["obesity", "overweight", "मोटापा", "મોટાપો", "लठ्ठपणा", "அதிக எடை"],
    "swollen_legs": ["swollen legs", "पैर सूजन", "પગમાં સોજો", "पाय सुजणे", "கால் வீக்கம்"],
    "swollen_blood_vessels": ["swollen veins", "सूजी नसें", "સૂજી ગયેલી નસો", "सुजलेल्या शिरा", "வீங்கிய இரத்த நாளங்கள்"],
    "puffy_face_and_eyes": ["puffy face", "चेहरा सूजा", "સૂજેલો ચહેરો", "सुजलेला चेहरा", "முக வீக்கம்"],
    "enlarged_thyroid": ["thyroid swelling", "थायराइड सूजन", "થાયરોઇડ સોજો", "थायरॉईड सूज", "தைராய்டு வீக்கம்"],
    "brittle_nails": ["brittle nails", "नाखून टूटना", "નખ તૂટે", "नखे तुटणे", "நகம் உடைதல்"],
    "swollen_extremeties": ["swollen hands feet", "हाथ पैर सूजना", "હાથ પગ સૂજવું", "हात पाय सुजणे", "கை கால் வீக்கம்"],
    "excessive_hunger": ["excessive hunger", "बहुत भूख", "ઘણી ભૂખ", "जास्त भूक", "அதிக பசி"],
    "extra_marital_contacts": ["unsafe sex"],
    "drying_and_tingling_lips": ["dry lips", "tingling lips", "होंठ सूखना", "હોઠ સૂકાય", "ओठ सुकणे", "உதடு உலர்வு"],
    "slurred_speech": ["slurred speech", "बोली लड़खड़ाना", "અસ્પષ્ટ બોલવું", "अस्पष्ट बोलणे", "தெளிவில்லா பேச்சு"],
    "knee_pain": ["knee pain", "घुटने दर्द", "ઘૂંટણમાં દુખાવો", "गुडघेदुखी", "முட்டி வலி"],
    "hip_joint_pain": ["hip pain", "कूल्हे दर्द", "હિપમાં દુખાવો", "नितंब सांधा वेदना", "இடுப்பு மூட்டு வலி"],
    "muscle_weakness": ["muscle weakness", "मांसपेशी कमजोरी", "સ્નાયુ નબળાઈ", "स्नायू कमजोरी", "தசை பலவீனம்"],
    "stiff_neck": ["stiff neck", "गर्दन अकड़ना", "ગરદન કઠોર", "मान आखडणे", "கழுத்து இறுக்கு"],
    "swelling_joints": ["joint swelling", "जोड़ सूजन", "સાંધામાં સોજો", "सांधे सुजणे", "மூட்டு வீக்கம்"],
    "movement_stiffness": ["stiff movement", "चलने में जकड़न", "હલનચલનમાં કઠોરતા", "हालचालीत कडकपणा", "இயக்க இறுக்கு"],
    "spinning_movements": ["vertigo", "spinning", "चक्कर घूमना", "ચક્કર ફરી વળે", "गरगर फिरणे", "சுற்றுவது போல"],
    "loss_of_balance": ["loss of balance", "संतुलन बिगड़ना", "સંતુલન ખોવાય", "समतोल बिघडणे", "சமநிலை இழப்பு"],
    "unsteadiness": ["unsteady", "अस्थिर", "અસ્થિર", "अस्थिर", "தடுமாறுதல்"],
    "weakness_of_one_body_side": ["one side weakness", "एक तरफ कमजोरी", "શરીરના એક ભાગમાં નબળાઈ", "शरीराच्या एका बाजूला कमजोरी", "ஒருபுற பலவீனம்"],
    "loss_of_smell": ["loss of smell", "सूंघने की शक्ति कम", "સુગંધ ન આવવી", "वास न येणे", "மணத்தை இழத்தல்"],
    "bladder_discomfort": ["bladder discomfort", "मूत्राशय दर्द", "મૂત્રાશયમાં દુખાવો", "मूत्राशय अस्वस्थता", "சிறுநீர்ப்பை இடர்ப்பு"],
    "foul_smell_of urine": ["foul urine smell", "पेशाब से बदबू", "મૂત્રમાં દુર્ગંધ", "लघवी वास", "துர்நாற்ற சிறுநீர்"],
    "continuous_feel_of_urine": ["frequent urge urine", "बार-बार पेशाब", "વારંવાર મૂત્રની લાગણી", "वारंवार लघवीची इच्छा", "அடிக்கடி சிறுநீர் உணர்வு"],
    "passage_of_gases": ["gas", "पेट में गैस", "ગેસ", "गॅस", "வயிற்று வாயு"],
    "internal_itching": ["internal itching", "भीतर खुजली", "અંદર ખંજવાળ", "आतली खाज", "உள் அரிப்பு"],
    "toxic_look_(typhos)": ["toxic look", "very sick appearance"],
    "depression": ["depression", "उदासी", "ઉદાસીનતા", "नैराश्य", "மனச்சோர்வு"],
    "irritability": ["irritability", "चिड़चिड़ापन", "ચિડચિડાપણું", "चिडचिड", "எரிச்சல்"],
    "muscle_pain": ["muscle pain", "मांसपेशी दर्द", "સ્નાયુમાં દુખાવો", "स्नायूदुखी", "தசை வலி"],
    "altered_sensorium": ["confusion", "altered sensorium", "बेहोशी जैसा", "ગૂંચવણ", "गोंधळ", "மயக்கம்/குழப்பம்"],
    "red_spots_over_body": ["red spots", "लाल दाने", "લાલ દાણા", "लाल पुरळ", "சிவப்பு புள்ளிகள்"],
    "belly_pain": ["belly pain", "पेट दर्द", "પેટ દુખે", "पोटदुखी", "வயிற்று வலி"],
    "abnormal_menstruation": ["abnormal periods", "अनियमित पीरियड", "અનિયમિત માસિક", "अनियमित मासिक", "அசாதாரண மாதவிடாய்"],
    "dischromic _patches": ["skin patches", "त्वचा पर धब्बे", "ચામડી પર ડાઘ", "त्वचेवर डाग", "சரும தழும்புகள்"],
    "watering_from_eyes": ["watering eyes", "आंखों से पानी", "આંખમાંથી પાણી", "डोळ्यातून पाणी", "கண்களில் நீர்"],
    "increased_appetite": ["increased appetite", "भूख बढ़ना", "ભૂખ વધવી", "भूक वाढणे", "பசி அதிகரித்தல்"],
    "polyuria": ["frequent urination", "बार बार पेशाब", "વારંવાર મૂત્ર", "वारंवार लघवी", "அடிக்கடி சிறுநீர்"],
    "family_history": ["family history", "परिवार में", "કુટુંબ ઇતિહાસ", "कौटुंबिक इतिहास", "குடும்ப வரலாறு"],
    "mucoid_sputum": ["mucus sputum", "बलगम", "કફ", "कफ", "சளி"],
    "rusty_sputum": ["blood sputum", "जंग जैसा कफ", "ઝાંખો કફ", "रक्तमिश्रित कफ", "துரு நிற சளி"],
    "lack_of_concentration": ["lack of concentration", "ध्यान नहीं", "ધ્યાન નથી રહેતું", "लक्ष केंद्रित नाही", "கவனம் குறைவு"],
    "visual_disturbances": ["visual disturbance", "दृष्टि समस्या", "દ્રષ્ટિ સમસ્યા", "दृष्टी त्रास", "காட்சி சிக்கல்"],
    "receiving_blood_transfusion": ["blood transfusion history"],
    "receiving_unsterile_injections": ["unsafe injection history"],
    "coma": ["coma", "बेहोश", "બેભાન", "कोमा", "கோமா"],
    "stomach_bleeding": ["vomiting blood", "stomach bleeding", "खून की उल्टी", "લોહીની ઊલટી", "रक्ताची उलटी", "இரத்த வாந்தி"],
    "distention_of_abdomen": ["abdomen swelling", "पेट फूलना", "પેટ ફૂલે", "पोट फुगणे", "வயிறு விரிவடைதல்"],
    "history_of_alcohol_consumption": ["alcohol history", "शराब", "દારૂ", "दारू", "மது"],
    "blood_in_sputum": ["blood in sputum", "खून वाला कफ", "કફમાં લોહી", "कफात रक्त", "சளியில் இரத்தம்"],
    "prominent_veins_on_calf": ["prominent veins", "नसें उभरी", "નસો દેખાય", "शिरा दिसणे", "வீங்கிய நரம்புகள்"],
    "palpitations": ["palpitations", "धड़कन तेज", "ધબકારા", "धडधड", "இதயத் துடிப்பு"],
    "painful_walking": ["painful walking", "चलने में दर्द", "ચાલવામાં દુખાવો", "चालताना वेदना", "நடப்பதில் வலி"],
    "pus_filled_pimples": ["pus pimples", "मवाद वाले दाने", "પસવાળા દાણા", "पूयुक्त मुरुम", "புண் நிரம்பிய முகப்பரு"],
    "blackheads": ["blackheads", "ब्लैकहेड", "બ્લેકહેડ", "ब्लॅकहेड", "பிளாக்ஹெட்"],
    "scurring": ["scarring", "scar marks", "दाग", "ડાઘ", "व्रण", "மரு"],
    "skin_peeling": ["skin peeling", "त्वचा छिलना", "ચામડી ઊખડવી", "त्वचा निघणे", "சரும உரிதல்"],
    "silver_like_dusting": ["silvery scales", "चांदी जैसे परत", "ચાંદી જેવી પડ", "चंदेरी परत", "வெள்ளி போன்ற துகள்"],
    "small_dents_in_nails": ["nail pits", "नाखून में गड्ढे", "નખમાં ખાડા", "नखात खळगे", "நகங்களில் சிறு குழிகள்"],
    "inflammatory_nails": ["inflamed nails", "नाखून सूजन", "નખ સોજો", "नखांची सूज", "நக அழற்சி"],
    "blister": ["blister", "फफोला", "છાલો", "फोड", "நீர்க்கட்டி"],
    "red_sore_around_nose": ["sore around nose", "नाक के आसपास घाव", "नाक આજુબાજુ ઘા", "नाकाभोवती जखम", "மூக்கைச் சுற்றிய புண்"],
    "yellow_crust_ooze": ["yellow crust", "पीली परत", "પીળી પડ", "पिवळी क्रस्ट", "மஞ்சள் மேல்தட்டு"],
}

DISEASE_URGENCY = {
    "Heart attack": "EMERGENCY",
    "Paralysis (brain hemorrhage)": "EMERGENCY",
    "Hypoglycemia": "EMERGENCY",
    "Pneumonia": "VISIT CLINIC",
    "Dengue": "VISIT CLINIC",
    "Malaria": "VISIT CLINIC",
    "Typhoid": "VISIT CLINIC",
    "Tuberculosis": "VISIT CLINIC",
    "Hepatitis B": "VISIT CLINIC",
    "Hepatitis C": "VISIT CLINIC",
    "Hepatitis D": "VISIT CLINIC",
    "Hepatitis E": "VISIT CLINIC",
    "Alcoholic hepatitis": "VISIT CLINIC",
    "hepatitis A": "VISIT CLINIC",
    "Common Cold": "SELF-CARE",
    "Allergy": "SELF-CARE",
    "Fungal infection": "SELF-CARE",
    "Acne": "SELF-CARE",
    "Psoriasis": "VISIT CLINIC",
    "Impetigo": "VISIT CLINIC",
}

ADVICE_TEXT = {
    "en": {
        "SELF-CARE": "Likely mild. Rest, drink fluids, and monitor symptoms. Visit a clinic if symptoms worsen or continue.",
        "VISIT CLINIC": "A clinic visit is recommended within 24 hours. Carry current medicines and previous prescriptions if available.",
        "EMERGENCY": "This may be urgent. Go to the nearest hospital immediately or call 108.",
    },
    "hi": {
        "SELF-CARE": "लक्षण हल्के लग रहे हैं। आराम करें, तरल लें और निगरानी रखें। बढ़ने या बने रहने पर क्लिनिक जाएँ।",
        "VISIT CLINIC": "24 घंटे के भीतर क्लिनिक जाना उचित है। यदि संभव हो तो दवाएँ और पुरानी पर्चियाँ साथ लें।",
        "EMERGENCY": "यह आपात स्थिति हो सकती है। तुरंत नज़दीकी अस्पताल जाएँ या 108 पर कॉल करें।",
    },
    "gu": {
        "SELF-CARE": "લક્ષણો હળવા લાગે છે. આરામ કરો, પાણી પીવો અને નજર રાખો. વધે અથવા ચાલુ રહે તો ક્લિનિક જાઓ.",
        "VISIT CLINIC": "24 કલાકમાં ક્લિનિકની મુલાકાત લેવી યોગ્ય છે. શક્ય હોય તો હાલની દવાઓ અને જૂની પર્ચી સાથે લો.",
        "EMERGENCY": "આ તાત્કાલિક હોઈ શકે. તુરંત નજીકની હોસ્પિટલ જાઓ અથવા 108 પર કૉલ કરો.",
    },
    "mr": {
        "SELF-CARE": "लक्षणे सौम्य वाटत आहेत. विश्रांती घ्या, द्रव घ्या आणि लक्ष ठेवा. वाढल्यास किंवा टिकल्यास क्लिनिकला जा.",
        "VISIT CLINIC": "24 तासांत क्लिनिकला जाणे योग्य आहे. शक्य असल्यास चालू औषधे आणि जुनी चिठ्ठी सोबत घ्या.",
        "EMERGENCY": "ही आपत्कालीन स्थिती असू शकते. तात्काळ जवळच्या रुग्णालयात जा किंवा 108 ला कॉल करा.",
    },
    "ta": {
        "SELF-CARE": "அறிகுறிகள் லேசாகத் தெரிகின்றன. ஓய்வு எடுத்துக் கொண்டு, திரவம் குடித்து கண்காணிக்கவும். மோசமாவிட்டால் அல்லது தொடர்ந்தால் கிளினிக்குச் செல்லவும்.",
        "VISIT CLINIC": "24 மணி நேரத்திற்குள் கிளினிக்குச் செல்ல பரிந்துரைக்கப்படுகிறது. முடிந்தால் தற்போது எடுத்துவரும் மருந்துகளும் பழைய சிகிச்சை விவரங்களும் எடுத்துச் செல்லுங்கள்.",
        "EMERGENCY": "இது அவசரமான நிலையாக இருக்கலாம். உடனே அருகிலுள்ள மருத்துவமனைக்கு செல்லவும் அல்லது 108 அழைக்கவும்.",
    },
}

QUESTION_TEXT = {
    "en": {
        "mild_fever": "Do you also have vomiting, rash, or fever for more than 3 days?",
        "breathlessness": "Is the patient able to speak full sentences or having severe breathing difficulty?",
        "chest_pain": "Is there sweating, weakness, or pain spreading to arm or jaw?",
        "vomiting": "Is the patient able to drink fluids and pass urine normally?",
        "default": "Please add age group, days since symptoms started, and whether it is mild, moderate, or severe.",
    },
    "hi": {
        "mild_fever": "क्या साथ में उल्टी, दाने, या 3 दिन से ज्यादा बुखार है?",
        "breathlessness": "क्या मरीज पूरे वाक्य बोल पा रहा है या सांस बहुत ज्यादा फूल रही है?",
        "chest_pain": "क्या पसीना, कमजोरी, या दर्द हाथ/जबड़े तक जा रहा है?",
        "vomiting": "क्या मरीज तरल पी पा रहा है और सामान्य पेशाब हो रहा है?",
        "default": "कृपया उम्र समूह, कितने दिन से है, और हल्का/मध्यम/गंभीर बताइए।",
    },
    "gu": {
        "mild_fever": "સાથે ઊલટી, દાણા, અથવા 3 દિવસથી વધુ તાવ છે?",
        "breathlessness": "દર્દી પૂરું વાક્ય બોલી શકે છે કે શ્વાસ ખૂબ ફૂલે છે?",
        "chest_pain": "ઘમો, નબળાઈ, અથવા હાથ/જડબા સુધી દુખાવો ફેલાય છે?",
        "vomiting": "દર્દી પ્રવાહી પી શકે છે અને સામાન્ય મૂત્ર થાય છે?",
        "default": "કૃપા કરીને ઉંમર જૂથ, કેટલા દિવસથી છે, અને હલકી/મધ્યમ/ગંભીર જણાવો.",
    },
    "mr": {
        "mild_fever": "उलटी, पुरळ, किंवा 3 दिवसांपेक्षा जास्त ताप आहे का?",
        "breathlessness": "रुग्ण पूर्ण वाक्य बोलू शकतो का की श्वास खूप लागतो आहे?",
        "chest_pain": "घाम, कमजोरी, किंवा वेदना हात/जबड्याकडे जाते का?",
        "vomiting": "रुग्ण द्रव घेऊ शकतो का आणि लघवी नीट होते का?",
        "default": "कृपया वयोगट, किती दिवसांपासून आहे, आणि सौम्य/मध्यम/गंभीर सांगा.",
    },
    "ta": {
        "mild_fever": "வாந்தி, சிவப்பு புள்ளிகள், அல்லது 3 நாட்களுக்கு மேல் காய்ச்சல் உள்ளதா?",
        "breathlessness": "நோயாளர் முழு வாக்கியம் பேச முடியிற்றா அல்லது மூச்சு மிகவும் திணறுகிறதா?",
        "chest_pain": "வியர்வை, பலவீனம், அல்லது வலி கை/தாடை நோக்கி செல்கிறதா?",
        "vomiting": "நோயாளர் திரவம் குடிக்க முடியிற்றா, சிறுநீர் சரியாக வருகிறதா?",
        "default": "வயது குழு, எத்தனை நாட்களாக உள்ளது, மற்றும் லேசு/நடுத்தரம்/கடுமை என்பதைச் சொல்லுங்கள்.",
    },
}

TYPE_LABELS = {
    "en": {"hospital": "Hospital", "clinic": "Clinic", "pharmacy": "Pharmacy"},
    "hi": {"hospital": "अस्पताल", "clinic": "क्लिनिक", "pharmacy": "फार्मेसी"},
    "gu": {"hospital": "હોસ્પિટલ", "clinic": "ક્લિનિક", "pharmacy": "ફાર્મસી"},
    "mr": {"hospital": "रुग्णालय", "clinic": "क्लिनिक", "pharmacy": "फार्मसी"},
    "ta": {"hospital": "மருத்துவமனை", "clinic": "கிளினிக்", "pharmacy": "மருந்தகம்"},
}

@dataclass
class HealthEngine:
    symptom_columns: list[str]
    model: RandomForestClassifier
    grouped_symptoms: dict[str, set[str]]
    descriptions: dict[str, str]
    precautions: dict[str, list[str]]
    severity: dict[str, int]


def _clean(text: str) -> str:
    return " ".join(str(text).replace("_", " ").replace("  ", " ").strip().split())


def _human_symptom(symptom: str) -> str:
    return _clean(symptom)


@lru_cache(maxsize=1)
def get_engine() -> HealthEngine:
    train = pd.read_csv(TRAIN_FILE)
    train.columns = [c.strip() for c in train.columns]
    train["prognosis"] = train["prognosis"].astype(str).str.strip()
    symptom_columns = [c for c in train.columns if c != "prognosis"]
    model = RandomForestClassifier(n_estimators=160, random_state=42, class_weight="balanced_subsample")
    model.fit(train[symptom_columns], train["prognosis"])

    grouped = train.groupby("prognosis")[symptom_columns].max()
    grouped_symptoms = {disease: set(grouped.columns[grouped.loc[disease] == 1]) for disease in grouped.index}

    desc_df = pd.read_csv(DESC_FILE)
    descriptions = {}
    disease_col = desc_df.columns[0]
    desc_col = desc_df.columns[1]
    # Include the header row itself as a data entry
    descriptions[_clean(disease_col)] = _clean(desc_col)
    for _, r in desc_df.iterrows():
        descriptions[_clean(r[disease_col])] = _clean(r[desc_col])

    pr_df = pd.read_csv(PRECAUTION_FILE)
    precautions = {}
    # First column is disease name, rest are precaution columns
    disease_col = pr_df.columns[0]
    for _, row in pr_df.iterrows():
        disease = _clean(row[disease_col])
        steps = [_clean(x) for x in row.iloc[1:].dropna().tolist() if _clean(x)]
        precautions[disease] = steps

    sev_df = pd.read_csv(SEVERITY_FILE, header=None, names=["symptom", "score"])
    severity = {_clean(r["symptom"]): int(r["score"]) for _, r in sev_df.iterrows() if str(r["score"]).isdigit()}

    return HealthEngine(
        symptom_columns=symptom_columns,
        model=model,
        grouped_symptoms=grouped_symptoms,
        descriptions=descriptions,
        precautions=precautions,
        severity=severity,
    )


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def _extract_context(message: str) -> dict[str, Any]:
    text = _normalize(message)
    severity = "mild"
    if any(x in text for x in ["severe", "serious", "very bad", "गंभीर", "ગંભીર", "गंभीर", "கடுமை"]):
        severity = "severe"
    elif any(x in text for x in ["moderate", "medium", "मध्यम", "મધ્યમ", "मध्यम", "நடுத்தரம்"]):
        severity = "moderate"

    age_group = "adult"
    if any(x in text for x in ["child", "baby", "kid", "बच्चा", "બાળક", "मूल", "குழந்தை"]):
        age_group = "child"
    elif any(x in text for x in ["elderly", "old", "senior", "बुज़ुर्ग", "વૃદ્ધ", "ज्येष्ठ", "முதியவர்"]):
        age_group = "elderly"

    duration_days = 1
    m = re.search(r"(\d+)\s*(day|days|दिन|દિવસ|दिवस|நாள்|நாட்கள்)", text)
    if m:
        duration_days = int(m.group(1))
    elif any(x in text for x in ["since morning", "आज", "આજે", "आजपासून", "இன்று"]):
        duration_days = 1

    return {"severity": severity, "age_group": age_group, "duration_days": duration_days}


def _fuzzy_match(query: str, text: str, text_words: list[str], cutoff=0.8) -> bool:
    if query in text: return True
    if len(query) < 4: return False
    query_words = query.split()
    n = len(query_words)
    if n == 1:
        return bool(difflib.get_close_matches(query, text_words, n=1, cutoff=cutoff))
    for i in range(len(text_words) - n + 1):
        phrase = " ".join(text_words[i:i+n])
        if difflib.SequenceMatcher(None, query, phrase).ratio() >= cutoff:
            return True
    return False

def _extract_symptoms(message: str) -> tuple[list[str], list[str]]:
    text = _normalize(message)
    text_words = text.split()
    found: list[str] = []
    display: list[str] = []
    for canonical, aliases in SYMPTOM_ALIASES.items():
        for alias in aliases:
            if not alias: continue
            al = alias.lower()
            if _fuzzy_match(al, text, text_words):
                found.append(canonical)
                display.append(alias)
                break

    # direct symptom phrase match using dataset symptom names
    engine = get_engine()
    for col in engine.symptom_columns:
        phrase = _human_symptom(col).lower()
        if col not in found and _fuzzy_match(phrase, text, text_words):
            found.append(col)
            display.append(phrase)

    return sorted(set(found)), sorted(set(display))

def _get_pending_symptom(symptoms: list[str]) -> str | None:
    if "breathlessness" in symptoms and "chest_pain" not in symptoms: return "chest_pain"
    if "chest_pain" in symptoms and "sweating" not in symptoms: return "sweating"
    if ("vomiting" in symptoms or "diarrhoea" in symptoms) and "dehydration" not in symptoms: return "dehydration"
    if ("high_fever" in symptoms or "mild_fever" in symptoms) and "vomiting" not in symptoms: return "vomiting"
    return None


def _predict_diseases(symptoms: list[str]) -> list[dict[str, Any]]:
    if len(symptoms) < 1:
        return []
    engine = get_engine()
    # Use DataFrame with proper column names to avoid sklearn warning
    input_row = pd.DataFrame(
        [[1 if col in symptoms else 0 for col in engine.symptom_columns]],
        columns=engine.symptom_columns
    )
    proba = engine.model.predict_proba(input_row)
    classes = list(engine.model.classes_)
    top_model = sorted(zip(classes, proba[0]), key=lambda x: x[1], reverse=True)[:5]

    scored = []
    symptom_set = set(symptoms)
    for disease, disease_symptoms in engine.grouped_symptoms.items():
        inter = len(symptom_set & disease_symptoms)
        if inter == 0:
            continue
        union = len(symptom_set | disease_symptoms)
        jaccard = inter / union
        overlap = inter / max(1, len(symptom_set))
        score = 0.65 * overlap + 0.35 * jaccard
        scored.append((disease, score))
    overlap_top = dict(sorted(scored, key=lambda x: x[1], reverse=True)[:5])

    merged: dict[str, float] = {}
    for disease, score in top_model:
        merged[disease] = merged.get(disease, 0) + float(score) * 0.55
    for disease, score in overlap_top.items():
        merged[disease] = merged.get(disease, 0) + float(score) * 0.45

    final = []
    for disease, score in sorted(merged.items(), key=lambda x: x[1], reverse=True)[:3]:
        final.append({
            "name": disease,
            "score": round(min(0.99, score), 2),
            "description": engine.descriptions.get(_clean(disease), ""),
            "precautions": engine.precautions.get(_clean(disease), [])[:3],
        })
    return final


# Localized reason strings keyed by reason_key
REASON_TEXT = {
    "cardiac_emergency": {
        "en": "Chest pain with breathlessness or sweating may indicate a cardiac emergency.",
        "hi": "सांस की तकलीफ या पसीने के साथ छाती में दर्द हृदय संबंधी आपात स्थिति हो सकती है।",
        "gu": "શ્વાસ ફૂલવા અથવા ઘમ સાથે છાતીનો દુખાવો હૃદય સંબંધિત ઇમર્જન્સી હોઈ શકે.",
        "mr": "श्वास लागणे किंवा घाम येणे सोबत छातीत दुखणे हृदयविकाराची आपत्कालीन स्थिती असू शकते.",
        "ta": "மூச்சுத்திணறல் அல்லது வியர்வையுடன் மார்பு வலி இதய அவசரநிலையாக இருக்கலாம்.",
    },
    "brain_emergency": {
        "en": "Confusion, one-sided weakness, or unclear speech can be signs of a brain emergency.",
        "hi": "भ्रम, एक तरफ कमजोरी, या अस्पष्ट बोली मस्तिष्क संबंधी आपात स्थिति के संकेत हो सकते हैं।",
        "gu": "ગૂંચવણ, એક બાજુ નબળાઈ, અથવા અસ્પષ્ટ બોલી મગજ સંબંધિત ઇમર્જન્સીના સંકેત હોઈ શકે.",
        "mr": "गोंधळ, एका बाजूची कमजोरी, किंवा अस्पष्ट बोलणे मेंदूच्या आपत्कालीन स्थितीची चिन्हे असू शकतात.",
        "ta": "குழப்பம், ஒருபுற பலவீனம், அல்லது தெளிவற்ற பேச்சு மூளை அவசரநிலையின் அறிகுறியாக இருக்கலாம்.",
    },
    "blood_loss": {
        "en": "Blood loss symptoms need urgent medical attention.",
        "hi": "रक्त हानि के लक्षणों को तत्काल चिकित्सा ध्यान की आवश्यकता है।",
        "gu": "રક્ત ગુમાવવાના લક્ષણોને તાત્કાલિક તબીબી ધ્યાનની જરૂર છે.",
        "mr": "रक्त कमी होण्याच्या लक्षणांना तातडीने वैद्यकीय मदत आवश्यक आहे.",
        "ta": "இரத்த இழப்பு அறிகுறிகளுக்கு உடனடி மருத்துவ கவனிப்பு தேவை.",
    },
    "severe_breathing": {
        "en": "Severe breathing difficulty should be treated urgently.",
        "hi": "गंभीर सांस की तकलीफ का तुरंत इलाज होना चाहिए।",
        "gu": "ગંભીર શ્વાસ ફૂલવાની સ્થિતિ તાત્કાલિક સારવારની જરૂર છે.",
        "mr": "गंभीर श्वास लागणे तातडीने उपचार करणे आवश्यक आहे.",
        "ta": "கடுமையான மூச்சுத்திணறலுக்கு உடனடி சிகிச்சை தேவை.",
    },
    "severe_chest": {
        "en": "Severe chest pain needs immediate medical attention.",
        "hi": "गंभीर छाती दर्द को तत्काल चिकित्सा ध्यान की आवश्यकता है।",
        "gu": "ગંભીર છાતીના દુખાવાને તાત્કાલિક તબીબી ધ્યાનની જરૂર છે.",
        "mr": "गंभीर छातीत दुखणे तातडीने वैद्यकीय मदत आवश्यक आहे.",
        "ta": "கடுமையான மார்பு வலிக்கு உடனடி மருத்துவ கவனிப்பு தேவை.",
    },
    "chest_pain_clinic": {
        "en": "Chest pain should always be evaluated by a doctor, even if mild.",
        "hi": "छाती में दर्द की हमेशा डॉक्टर से जाँच करानी चाहिए, चाहे हल्का हो।",
        "gu": "છાતીના દુખાવાની હંમેશા ડૉક્ટર પાસે તપાસ કરાવવી જોઈએ, ભલે હળવો હોય.",
        "mr": "छातीत दुखणे नेहमी डॉक्टरांकडून तपासले पाहिजे, जरी सौम्य असले तरी.",
        "ta": "மார்பு வலியை எப்போதும் மருத்துவரிடம் பரிசோதிக்க வேண்டும், லேசாக இருந்தாலும்.",
    },
    "breathlessness_clinic": {
        "en": "Breathing difficulty should be assessed at a clinic.",
        "hi": "सांस की तकलीफ की क्लिनिक में जाँच होनी चाहिए।",
        "gu": "શ્વાસ ફૂલવાની ક્લિનિકમાં તપાસ થવી જોઈએ.",
        "mr": "श्वास लागणे क्लिनिकमध्ये तपासले पाहिजे.",
        "ta": "மூச்சுத்திணறலை கிளினிக்கில் பரிசோதிக்க வேண்டும்.",
    },
    "child_fever": {
        "en": "Fever in a child should always be checked by a clinician.",
        "hi": "बच्चे में बुखार की हमेशा डॉक्टर से जाँच करानी चाहिए।",
        "gu": "બાળકમાં તાવ હંમેશા ડૉક્ટર પાસે તપાસ કરાવવો જોઈએ.",
        "mr": "मुलामध्ये ताप नेहमी डॉक्टरांकडून तपासला पाहिजे.",
        "ta": "குழந்தைக்கு காய்ச்சல் இருந்தால் எப்போதும் மருத்துவரிடம் பரிசோதிக்க வேண்டும்.",
    },
    "child_vomiting": {
        "en": "Vomiting or diarrhoea in a child needs clinic assessment.",
        "hi": "बच्चे में उल्टी या दस्त की क्लिनिक में जाँच होनी चाहिए।",
        "gu": "બાળકમાં ઊલટી અથવા ઝાડા ક્લિનિકમાં તપાસ કરાવવી જોઈએ.",
        "mr": "मुलामध्ये उलटी किंवा जुलाब क्लिनिकमध्ये तपासले पाहिजे.",
        "ta": "குழந்தைக்கு வாந்தி அல்லது வயிற்றுப்போக்கு இருந்தால் கிளினிக்கில் பரிசோதிக்க வேண்டும்.",
    },
    "persistent_symptoms": {
        "en": "Persistent fever, vomiting, or dehydration needs clinic assessment.",
        "hi": "लगातार बुखार, उल्टी, या निर्जलीकरण की क्लिनिक में जाँच होनी चाहिए।",
        "gu": "સતત તાવ, ઊલટી, અથવા ડિહાઇડ્રેશન ક્લિનિકમાં તપાસ કરાવવી જોઈએ.",
        "mr": "सतत ताप, उलटी, किंवा निर्जलीकरण क्लिनिकमध्ये तपासले पाहिजे.",
        "ta": "தொடர்ந்த காய்ச்சல், வாந்தி, அல்லது நீரிழப்பு கிளினிக்கில் பரிசோதிக்க வேண்டும்.",
    },
    "multiple_moderate": {
        "en": "Multiple moderate symptoms should be evaluated at a clinic.",
        "hi": "कई मध्यम लक्षणों की क्लिनिक में जाँच होनी चाहिए।",
        "gu": "અનેક મધ્યમ લક્ષણો ક્લિનિકમાં તપાસ કરાવવા જોઈએ.",
        "mr": "अनेक मध्यम लक्षणे क्लिनिकमध्ये तपासली पाहिजेत.",
        "ta": "பல நடுத்தர அறிகுறிகளை கிளினிக்கில் பரிசோதிக்க வேண்டும்.",
    },
    "multiple_symptoms": {
        "en": "Multiple symptoms together warrant a clinic visit.",
        "hi": "कई लक्षण एक साथ होने पर क्लिनिक जाना उचित है।",
        "gu": "અનેક લક્ષણો એકસાથે હોય ત્યારે ક્લિનિક જવું યોગ્ય છે.",
        "mr": "अनेक लक्षणे एकत्र असल्यास क्लिनिकला जाणे योग्य आहे.",
        "ta": "பல அறிகுறிகள் ஒன்றாக இருந்தால் கிளினிக்குச் செல்வது நல்லது.",
    },
    "ml_emergency": {
        "en": "The symptom pattern may indicate a serious condition needing emergency care.",
        "hi": "लक्षणों का पैटर्न एक गंभीर स्थिति का संकेत दे सकता है जिसे आपातकालीन देखभाल की आवश्यकता है।",
        "gu": "લક્ષણોનો પેટર્ન ઇમર્જન્સી સારવારની જરૂર હોય તેવી ગંભીર સ્થિતિ સૂચવી શકે.",
        "mr": "लक्षणांचा नमुना आपत्कालीन काळजी आवश्यक असलेल्या गंभीर स्थितीचे संकेत देऊ शकतो.",
        "ta": "அறிகுறி வடிவம் அவசர சிகிச்சை தேவைப்படும் தீவிர நிலையை சுட்டிக்காட்டலாம்.",
    },
    "ml_clinic": {
        "en": "The symptom pattern suggests a condition that should be assessed at a clinic.",
        "hi": "लक्षणों का पैटर्न एक ऐसी स्थिति का सुझाव देता है जिसे क्लिनिक में जाँचा जाना चाहिए।",
        "gu": "લક્ષણોનો પેટર્ન એવી સ્થિતિ સૂચવે છે જે ક્લિનિકમાં તપાસ કરાવવી જોઈએ.",
        "mr": "लक्षणांचा नमुना अशा स्थितीचे सुचवतो जी क्लिनिकमध्ये तपासली पाहिजे.",
        "ta": "அறிகுறி வடிவம் கிளினிக்கில் பரிசோதிக்க வேண்டிய நிலையை சுட்டிக்காட்டுகிறது.",
    },
    "mild_symptoms": {
        "en": "Symptoms look mild with no immediate red-flag pattern detected.",
        "hi": "लक्षण हल्के लग रहे हैं, कोई तत्काल खतरे का संकेत नहीं मिला।",
        "gu": "લક્ષણો હળવા લાગે છે, કોઈ તાત્કાલિક ખતરાનો સંકેત નથી.",
        "mr": "लक्षणे सौम्य वाटत आहेत, कोणताही तातडीचा धोक्याचा संकेत आढळला नाही.",
        "ta": "அறிகுறிகள் லேசாகத் தெரிகின்றன, உடனடி ஆபத்தான வடிவம் எதுவும் கண்டறியப்படவில்லை.",
    },
    "unidentified": {
        "en": "Symptoms were not clearly identified, so a clinic visit is safer if the problem continues.",
        "hi": "लक्षण स्पष्ट रूप से पहचाने नहीं गए, इसलिए समस्या जारी रहने पर क्लिनिक जाना सुरक्षित है।",
        "gu": "લક્ષણ સ્પષ્ટ રીતે ઓળખાયા નહીં, તેથી સમસ્યા ચાલુ રહે તો ક્લિનિક જવું સુરક્ષિત છે.",
        "mr": "लक्षणे स्पष्टपणे ओळखता आली नाहीत, त्यामुळे समस्या सुरू राहिल्यास क्लिनिकला जाणे सुरक्षित आहे.",
        "ta": "அறிகுறிகள் தெளிவாக அடையாளம் காணப்படவில்லை, எனவே பிரச்சனை தொடர்ந்தால் கிளினிக்குச் செல்வது பாதுகாப்பானது.",
    },
}

PRECAUTION_TRANSLATIONS = {
    "en": {},
    "hi": {
        "call ambulance": "एम्बुलेंस बुलाएं",
        "chew or swallow asprin": "एस्पिरिन चबाएं या निगलें",
        "keep calm": "शांत रहें",
        "cover mouth": "मुंह ढकें",
        "consult doctor": "डॉक्टर से सलाह लें",
        "medication": "दवा लें",
        "lie down": "लेट जाएं",
        "avoid sudden change in body": "शरीर में अचानक बदलाव से बचें",
        "avoid abrupt head movment": "सिर को अचानक न हिलाएं",
        "drink plenty of water": "भरपूर पानी पिएं",
        "rest": "आराम करें"
    },
    "gu": {
        "call ambulance": "એમ્બ્યુલન્સ બોલાવો",
        "chew or swallow asprin": "એસ્પિરિન ચાવો અથવા ગળો",
        "keep calm": "શાંત રહો",
        "cover mouth": "મોં ઢાંકો",
        "consult doctor": "ડૉક્ટરની સલાહ લો",
        "medication": "દવા લો",
        "lie down": "સૂઈ જાઓ",
        "avoid sudden change in body": "શરીરમાં અચાનક બદલાવ ટાળો",
        "avoid abrupt head movment": "માથું અચાનક ન હલાવો",
        "drink plenty of water": "પુષ્કળ પાણી પીવો",
        "rest": "આરામ કરો"
    },
    "mr": {
        "call ambulance": "रुग्णवाहिका बोलवा",
        "chew or swallow asprin": "ऍस्पिरिन चघळा किंवा गिळा",
        "keep calm": "शांत राहा",
        "cover mouth": "तोंड झाका",
        "consult doctor": "डॉक्टरांचा सल्ला घ्या",
        "medication": "औषध घ्या",
        "lie down": "झोपा",
        "avoid sudden change in body": "शरीरातील अचानक बदल टाळा",
        "avoid abrupt head movment": "डोके अचानक हलवू नका",
        "drink plenty of water": "भरपूर पाणी प्या",
        "rest": "विश्रांती घ्या"
    },
    "ta": {
        "call ambulance": "ஆம்புலன்ஸ் அழைக்கவும்",
        "chew or swallow asprin": "ஆஸ்பிரின் மெல்லுங்கள் அல்லது விழுங்குங்கள்",
        "keep calm": "அமைதியாக இருங்கள்",
        "cover mouth": "வாயை மூடுங்கள்",
        "consult doctor": "மருத்துவரை ஆலோசிக்கவும்",
        "medication": "மருந்து உட்கொள்ளவும்",
        "lie down": "படுத்துக்கொள்ளுங்கள்",
        "avoid sudden change in body": "உடலில் திடீர் மாற்றத்தைத் தவிருங்கள்",
        "avoid abrupt head movment": "தலையை திடீரென்று அசைப்பதைத் தவிருங்கள்",
        "drink plenty of water": "நிறைய தண்ணீர் குடிக்கவும்",
        "rest": "ஓய்வெடுக்கவும்"
    }
}

# Localized disease name map (English dataset name → localized)
DISEASE_NAMES = {
    "(vertigo) Paroymsal Positional Vertigo": {"en": "(Vertigo) Paroymsal Positional Vertigo", "hi": "चक्कर (वर्टिगो)", "gu": "ચક્કર (વર્ટિગો)", "mr": "चक्कर (व्हर्टिगो)", "ta": "தலைசுற்றல் (வெர்டிகோ)"},
    "Heart attack": {"en": "Heart attack", "hi": "दिल का दौरा", "gu": "હૃદય રોગ", "mr": "हृदयविकाराचा झटका", "ta": "மாரடைப்பு"},
    "Hypertension ": {"en": "Hypertension", "hi": "उच्च रक्तचाप", "gu": "હાઈ બ્લડ પ્રેશર", "mr": "उच्च रक्तदाब", "ta": "உயர் இரத்த அழுத்தம்"},
    "GERD": {"en": "GERD", "hi": "एसिड रिफ्लक्स", "gu": "એસિડ રિફ્લક્સ", "mr": "अॅसिड रिफ्लक्स", "ta": "அமில ரிஃப்ளக்ஸ்"},
    "Common Cold": {"en": "Common Cold", "hi": "सामान्य सर्दी", "gu": "સામાન્ય શરદી", "mr": "सामान्य सर्दी", "ta": "சாதாரண சளி"},
    "Pneumonia": {"en": "Pneumonia", "hi": "निमोनिया", "gu": "ન્યૂમોનિયા", "mr": "न्यूमोनिया", "ta": "நிமோனியா"},
    "Dengue": {"en": "Dengue", "hi": "डेंगू", "gu": "ડેન્ગ્યૂ", "mr": "डेंग्यू", "ta": "டெங்கு"},
    "Malaria": {"en": "Malaria", "hi": "मलेरिया", "gu": "મેલેરિયા", "mr": "मलेरिया", "ta": "மலேரியா"},
    "Typhoid": {"en": "Typhoid", "hi": "टाइफाइड", "gu": "ટાઇફોઇડ", "mr": "टायफॉइड", "ta": "டைஃபாய்டு"},
    "Tuberculosis": {"en": "Tuberculosis", "hi": "तपेदिक", "gu": "ક્ષય રોગ", "mr": "क्षयरोग", "ta": "காசநோய்"},
    "Diabetes ": {"en": "Diabetes", "hi": "मधुमेह", "gu": "ડાયાબિટીસ", "mr": "मधुमेह", "ta": "நீரிழிவு"},
    "Allergy": {"en": "Allergy", "hi": "एलर्जी", "gu": "એલર્જી", "mr": "ऍलर्जी", "ta": "ஒவ்வாமை"},
    "Migraine": {"en": "Migraine", "hi": "माइग्रेन", "gu": "માઇગ્રેન", "mr": "मायग्रेन", "ta": "ஒற்றைத் தலைவலி"},
    "Jaundice": {"en": "Jaundice", "hi": "पीलिया", "gu": "કમળો", "mr": "कावीळ", "ta": "மஞ்சள் காமாலை"},
    "Gastroenteritis": {"en": "Gastroenteritis", "hi": "गैस्ट्रोएंटेराइटिस", "gu": "ગેસ્ટ્રોએન્ટેરાઇટિસ", "mr": "जठरांत्रशोथ", "ta": "இரைப்பை குடல் அழற்சி"},
    "Paralysis (brain hemorrhage)": {"en": "Paralysis", "hi": "लकवा", "gu": "લકવો", "mr": "अर्धांगवायू", "ta": "பக்கவாதம்"},
    "Hypoglycemia": {"en": "Hypoglycemia", "hi": "हाइपोग्लाइसीमिया", "gu": "હાઇપોગ્લાઇસીમિયા", "mr": "हायपोग्लायसेमिया", "ta": "இரத்தச் சர்க்கரைக் குறைவு"},
    "Fungal infection": {"en": "Fungal infection", "hi": "फंगल संक्रमण", "gu": "ફૂગ ચેપ", "mr": "बुरशीजन्य संसर्ग", "ta": "பூஞ்சை தொற்று"},
    "Acne": {"en": "Acne", "hi": "मुँहासे", "gu": "ખીલ", "mr": "मुरुम", "ta": "முகப்பரு"},
    "Psoriasis": {"en": "Psoriasis", "hi": "सोरायसिस", "gu": "સૉરાઇસિસ", "mr": "सोरायसिस", "ta": "சொரியாசிஸ்"},
    "Impetigo": {"en": "Impetigo", "hi": "इम्पेटिगो", "gu": "ઇમ્પેટિગો", "mr": "इम्पेटिगो", "ta": "இம்பெடிகோ"},
    "Hepatitis B": {"en": "Hepatitis B", "hi": "हेपेटाइटिस बी", "gu": "હેપેટાઇટિસ બી", "mr": "हिपॅटायटिस बी", "ta": "ஹெபடைடிஸ் பி"},
    "Hepatitis C": {"en": "Hepatitis C", "hi": "हेपेटाइटिस सी", "gu": "હેપેટાઇટિસ સી", "mr": "हिपॅटायटिस सी", "ta": "ஹெபடைடிஸ் சி"},
    "hepatitis A": {"en": "Hepatitis A", "hi": "हेपेटाइटिस ए", "gu": "હેપેટાઇટિસ એ", "mr": "हिपॅटायटिस ए", "ta": "ஹெபடைடிஸ் ஏ"},
    "Hepatitis D": {"en": "Hepatitis D", "hi": "हेपेटाइटिस डी", "gu": "હેપેટાઇટિસ ડી", "mr": "हिपॅटायटिस डी", "ta": "ஹெபடைடிஸ் டி"},
    "Hepatitis E": {"en": "Hepatitis E", "hi": "हेपेटाइटिस ई", "gu": "હેપેટાઇટિસ ઈ", "mr": "हिपॅटायटिस ई", "ta": "ஹெபடைடிஸ் இ"},
    "Alcoholic hepatitis": {"en": "Alcoholic hepatitis", "hi": "शराब से हेपेटाइटिस", "gu": "દારૂ સંબંધિત હેપેટાઇટિસ", "mr": "मद्यपानामुळे हिपॅटायटिस", "ta": "மது ஹெபடைடிஸ்"},
}

# Localized insight templates
INSIGHT_DETECTED = {
    "en": "Detected: {names}. Closest condition: {top}.",
    "hi": "पहचाने गए लक्षण: {names}। सबसे संभावित स्थिति: {top}।",
    "gu": "ઓળખાયેલા લક્ષણ: {names}. સૌથી સંભવિત સ્થિતિ: {top}.",
    "mr": "ओळखलेली लक्षणे: {names}. सर्वात संभाव्य स्थिती: {top}.",
    "ta": "கண்டறியப்பட்ட அறிகுறிகள்: {names}. மிகவும் சாத்தியமான நிலை: {top}.",
}
INSIGHT_NO_MATCH = {
    "en": "Detected: {names}. Add more details for better matching.",
    "hi": "पहचाने गए लक्षण: {names}। बेहतर मिलान के लिए अधिक विवरण दें।",
    "gu": "ઓળખાયેલા લક્ષણ: {names}. વધુ સારા મેળ માટે વધુ વિગત આપો.",
    "mr": "ओळखलेली लक्षणे: {names}. चांगल्या जुळणीसाठी अधिक तपशील द्या.",
    "ta": "கண்டறியப்பட்ட அறிகுறிகள்: {names}. சிறந்த பொருத்தத்திற்கு மேலும் விவரங்கள் சேர்க்கவும்.",
}


def _risk_from_symptoms(symptoms: list[str], context: dict[str, Any], predicted: list[dict[str, Any]]) -> tuple[str, str]:
    symptom_set = set(symptoms)

    if {"chest_pain", "breathlessness"}.issubset(symptom_set) or {"chest_pain", "sweating"}.issubset(symptom_set):
        return "EMERGENCY", "cardiac_emergency"
    if any(x in symptom_set for x in ["coma", "altered_sensorium", "weakness_of_one_body_side", "slurred_speech"]):
        return "EMERGENCY", "brain_emergency"
    if any(x in symptom_set for x in ["stomach_bleeding", "blood_in_sputum", "bloody_stool"]):
        return "EMERGENCY", "blood_loss"
    if "breathlessness" in symptom_set and context.get("severity") == "severe":
        return "EMERGENCY", "severe_breathing"
    if "chest_pain" in symptom_set and context.get("severity") == "severe":
        return "EMERGENCY", "severe_chest"
    if "chest_pain" in symptom_set:
        return "VISIT CLINIC", "chest_pain_clinic"
    if "breathlessness" in symptom_set:
        return "VISIT CLINIC", "breathlessness_clinic"
    if context.get("age_group") == "child":
        if "high_fever" in symptom_set:
            return "VISIT CLINIC", "child_fever"
        if any(x in symptom_set for x in ["vomiting", "diarrhoea", "dehydration"]):
            return "VISIT CLINIC", "child_vomiting"
    if any(x in symptom_set for x in ["high_fever", "vomiting", "diarrhoea", "dehydration"]) and context.get("duration_days", 1) >= 3:
        return "VISIT CLINIC", "persistent_symptoms"
    if context.get("severity") in {"moderate", "severe"} and len(symptom_set) >= 2:
        return "VISIT CLINIC", "multiple_moderate"
    if len(symptom_set) >= 3:
        return "VISIT CLINIC", "multiple_symptoms"
    if predicted:
        top = predicted[0]["name"]
        mapped = DISEASE_URGENCY.get(top)
        if mapped == "EMERGENCY" and len(symptom_set) >= 2:
            return "EMERGENCY", "ml_emergency"
        if mapped == "VISIT CLINIC":
            return "VISIT CLINIC", "ml_clinic"
    if symptom_set:
        return "SELF-CARE", "mild_symptoms"
    return "VISIT CLINIC", "unidentified"


def _urgency_label(lang: str, urgency: str) -> str:
    mapping = {
        "SELF-CARE": UI_TEXT[lang]["self_care"],
        "VISIT CLINIC": UI_TEXT[lang]["visit_clinic"],
        "EMERGENCY": UI_TEXT[lang]["emergency_level"],
    }
    return mapping[urgency]


def _next_question(lang: str, symptoms: list[str]) -> str:
    q = QUESTION_TEXT.get(lang, QUESTION_TEXT["en"])
    if "breathlessness" in symptoms:
        return q["breathlessness"]
    if "chest_pain" in symptoms:
        return q["chest_pain"]
    if "vomiting" in symptoms or "diarrhoea" in symptoms:
        return q["vomiting"]
    if "high_fever" in symptoms or "mild_fever" in symptoms:
        return q["mild_fever"]
    return q["default"]


def _load_facilities() -> list[dict[str, Any]]:
    return json.loads(FACILITY_FILE.read_text(encoding="utf-8"))


def _choose_facility(urgency: str) -> dict[str, Any]:
    facilities = _load_facilities()
    preferred = {"EMERGENCY": "hospital", "VISIT CLINIC": "clinic", "SELF-CARE": "pharmacy"}[urgency]
    matches = [f for f in facilities if f["type"] == preferred] or facilities
    return sorted(matches, key=lambda x: float(x.get("distance_km", 999)))[0]


def _localized_facility(facility: dict[str, Any], lang: str) -> dict[str, Any]:
    item = dict(facility)
    item["type_label"] = TYPE_LABELS.get(lang, TYPE_LABELS["en"]).get(item["type"], item["type"])
    return item

def _get_live_facility(urgency: str, lat: float, lng: float, lang: str) -> dict:
    import urllib.request, json
    fac_type = {"EMERGENCY": "hospital", "VISIT CLINIC": "clinic", "SELF-CARE": "pharmacy"}.get(urgency, "clinic")
    
    try:
        url = f"https://nominatim.openstreetmap.org/search.php?q={fac_type}&format=jsonv2&lat={lat}&lon={lng}&limit=1"
        req = urllib.request.Request(url, headers={'User-Agent': 'SwasthyaSaathiBot/1.0'})
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if data:
                place = data[0]
                name = place.get("name", f"Nearby {fac_type.capitalize()}")
                if not name or name.isdigit(): name = f"Nearby {fac_type.capitalize()}"
                
                type_label_map = {
                    "en": f"Live {fac_type.capitalize()}",
                    "hi": "लाइव " + ("अस्पताल" if fac_type=="hospital" else "क्लिनिक" if fac_type=="clinic" else "फार्मेसी"),
                    "gu": "લાઇવ " + ("હોસ્પિટલ" if fac_type=="hospital" else "ક્લિનિક" if fac_type=="clinic" else "ફાર્મસી"),
                    "mr": "थेट " + ("रुग्णालय" if fac_type=="hospital" else "क्लिनिक" if fac_type=="clinic" else "फार्मसी"),
                    "ta": "நேரடி " + ("மருத்துவமனை" if fac_type=="hospital" else "கிளினிக்" if fac_type=="clinic" else "மருந்தகம்")
                }
                return {
                    "name": name,
                    "distance_km": None,
                    "type": fac_type,
                    "type_label": type_label_map.get(lang, type_label_map["en"]),
                    "map_url": f"https://www.google.com/maps/search/?api=1&query={place['lat']},{place['lon']}"
                }
    except Exception:
        pass

    query = f"{fac_type} near me"
    type_label_map = {
        "en": "Map Location", "hi": "मैप स्थान", "gu": "નકશા સ્થાન", "mr": "नकाशा स्थान", "ta": "வரைபட இடம்"
    }
    return {
        "name": f"Nearest {fac_type.capitalize()}",
        "distance_km": None,
        "type": fac_type,
        "type_label": type_label_map.get(lang, type_label_map["en"]),
        "map_url": f"https://www.google.com/maps/search/{query.replace(' ', '+')}/@{lat},{lng},14z"
    }

def _get_facility_for_urgency(urgency: str, lang: str, lat: float = None, lng: float = None) -> dict:
    import urllib.parse
    if lat is not None and lng is not None:
        try:
            return _get_live_facility(urgency, float(lat), float(lng), lang)
        except ValueError:
            pass
            
    fac = _localized_facility(_choose_facility(urgency), lang)
    fac["map_url"] = f"https://www.google.com/maps/search/{urllib.parse.quote(fac['name'])}"
    return fac


GREETINGS = {
    "en": ["hi", "hello", "hey", "good morning", "good evening", "good afternoon", "howdy"],
    "hi": ["नमस्ते", "नमस्कार", "हेलो", "हाय", "प्रणाम"],
    "gu": ["નમસ્તે", "નમસ્કાર", "હેલો", "હાય"],
    "mr": ["नमस्कार", "नमस्ते", "हॅलो", "हाय"],
    "ta": ["வணக்கம்", "ஹலோ", "ஹாய்"],
}

GREETING_REPLY = {
    "en": "Hello! I'm SwasthyaSaathi, your health assistant. Please describe your symptoms — for example: fever for 3 days, chest pain, vomiting, or difficulty breathing. The more detail you give, the better I can help.",
    "hi": "नमस्ते! मैं स्वास्थ्यसाथी हूँ। कृपया अपने लक्षण बताइए — जैसे: 3 दिन से बुखार, छाती में दर्द, उल्टी, या सांस लेने में तकलीफ। जितना विस्तार से बताएंगे, उतनी बेहतर मदद मिलेगी।",
    "gu": "નમસ્તે! હું સ્વાસ્થ્યસાથી છું. કૃપા કરીને તમારા લક્ષણ જણાવો — જેમ કે: 3 દિવસથી તાવ, છાતીમાં દુખાવો, ઊલટી, અથવા શ્વાસ લેવામાં તકલીફ.",
    "mr": "नमस्कार! मी स्वास्थ्यसाथी आहे. कृपया तुमची लक्षणे सांगा — उदा: 3 दिवसांपासून ताप, छातीत दुखणे, उलटी, किंवा श्वास घेण्यास त्रास.",
    "ta": "வணக்கம்! நான் ஸ்வாஸ்த்யசாத்தி. உங்கள் அறிகுறிகளை சொல்லுங்கள் — எ.கா: 3 நாட்களாக காய்ச்சல், மார்பு வலி, வாந்தி, அல்லது மூச்சுத்திணறல்.",
}

NO_SYMPTOM_REPLY = {
    "en": "I couldn't detect specific symptoms from your message. Please try describing what you feel — for example: 'I have fever and headache for 2 days' or 'child has vomiting and stomach pain'.",
    "hi": "मैं आपके संदेश से लक्षण नहीं पहचान पाया। कृपया बताइए — जैसे: '2 दिन से बुखार और सिर दर्द है' या 'बच्चे को उल्टी और पेट दर्द है'।",
    "gu": "હું તમારા સંદેશમાંથી લક્ષણ ઓળખી શક્યો નહીં. કૃપા કરીને જણાવો — જેમ કે: '2 દિવસથી તાવ અને માથાનો દુખાવો' અથવા 'બાળકને ઊલટી અને પેટ દુખે છે'.",
    "mr": "मला तुमच्या संदेशातून लक्षणे ओळखता आली नाहीत. कृपया सांगा — उदा: '2 दिवसांपासून ताप आणि डोकेदुखी' किंवा 'मुलाला उलटी आणि पोटदुखी आहे'.",
    "ta": "உங்கள் செய்தியிலிருந்து அறிகுறிகளை கண்டறிய முடியவில்லை. தயவுசெய்து சொல்லுங்கள் — எ.கா: '2 நாட்களாக காய்ச்சல் மற்றும் தலைவலி' அல்லது 'குழந்தைக்கு வாந்தி மற்றும் வயிற்று வலி'.",
}

CONVERSATIONAL_RESPONSE = {
    "en": "I understand you are experiencing **{symptoms}**. Based on this assessment, **{urgency}** is recommended. {advice}",
    "hi": "मैं समझता हूँ कि आपको **{symptoms}** की समस्या हो रही है। इस आधार पर, **{urgency}** की सलाह दी जाती है। {advice}",
    "gu": "હું સમજું છું કે તમને **{symptoms}** ની તકલીફ છે. આના આધારે, **{urgency}** ની સલાહ આપવામાં આવે છે. {advice}",
    "mr": "मला समजते की तुम्हाला **{symptoms}** चा त्रास होत आहे. या आधारावर, **{urgency}** चा सल्ला दिला जातो. {advice}",
    "ta": "உங்களுக்கு **{symptoms}** இருப்பதை நான் புரிந்துகொள்கிறேன். இதன் அடிப்படையில், **{urgency}** பரிந்துரைக்கப்படுகிறது. {advice}",
}


def _is_greeting(message: str, lang: str) -> bool:
    """Return True if the message is just a greeting with no symptoms."""
    text = _normalize(message)
    # Strip only ASCII punctuation — preserve Unicode (Gujarati, Hindi, Tamil scripts)
    clean = re.sub(r"[!?,.\-]", "", text).strip()
    all_greetings = []
    for g_list in GREETINGS.values():
        all_greetings.extend(g_list)
    return clean in [g.lower() for g in all_greetings]

def _is_injury(message: str) -> bool:
    text = message.lower()
    
    # Exclude common contextual false positives
    for fp in ["fall asleep", "fell asleep", "fell ill", "falling asleep"]:
        text = text.replace(fp, "")
        
    en_pattern = r"\b(bleed|bleeding|blood|cut|wound|injur(y|ed)?|broken|fracture|accident|hit|crash|fell down|fall down|fell off)\b"
    if re.search(en_pattern, text):
        return True
        
    # Unicode strings for regional languages (simple substring since script is distinct)
    regional_keywords = ["खून", "गिरा", "चोट", "ઈજા", "લોહી", "ઘા", "रक्त", "जख्म", "இரத்தம்", "காயம்"]
    for k in regional_keywords:
        if k in text:
            return True
            
    return False

def _search_wikipedia(query: str, lang: str) -> str | None:
    import urllib.request, urllib.parse, json
    try:
        wiki_lang = lang if lang in ["hi", "gu", "mr", "ta"] else "en"
        # Append health context to the search generator to force higher ranking of medical pages
        search_query = f"{query} disease OR medicine OR health"
        url = f"https://{wiki_lang}.wikipedia.org/w/api.php?action=query&generator=search&gsrsearch={urllib.parse.quote(search_query)}&gsrlimit=1&prop=extracts&exintro=1&explaintext=1&exchars=300&format=json"
        req = urllib.request.Request(url, headers={'User-Agent': 'SwasthyaSaathiBot/1.0'})
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode())
            pages = data.get("query", {}).get("pages", {})
            if pages:
                first_page = list(pages.values())[0]
                desc = first_page.get("extract", "")
                
                # Fast medical guardrail - reject pop-culture/novelty pages
                lower_desc = desc.lower()
                non_medical_keywords = ["album", "band", "film", "movie", "song", "music", "fictional", "novel", "television", "series", "entertainment"]
                if any(w in lower_desc for w in non_medical_keywords):
                    return None
                    
                if desc and not desc.endswith("may refer to:"):
                    return desc
    except Exception:
        pass
    return None

def _build_ai_reply(request, message: str, lang: str, lat: float = None, lng: float = None) -> dict[str, Any]:
    lang = lang if lang in UI_TEXT else "en"

    # Handle greetings — clear session memory
    if _is_greeting(message, lang):
        request.session["chat_symptoms"] = []
        request.session["pending_symptom"] = None
        facility = _get_facility_for_urgency("VISIT CLINIC", lang, lat, lng)
        reply_text = GREETING_REPLY.get(lang, GREETING_REPLY["en"])
        return {
            "text": reply_text,
            "urgency": None, "urgency_label": "", "reason": "", "advice": "",
            "facility": facility, "symptoms": [], "matched_aliases": [],
            "context": {}, "likely_conditions": [], "next_question": "",
            "assistant_insight": reply_text, "is_greeting": True,
        }

    if _is_injury(message):
        request.session["chat_symptoms"] = []
        request.session["pending_symptom"] = None
        facility = _get_facility_for_urgency("EMERGENCY", lang, lat, lng)
        
        injury_reply = {
            "en": "I understand you have had an injury, fall, or bleeding. Based on this, an **EMERGENCY** visit is recommended. Please seek immediate medical attention.",
            "hi": "मैं समझता हूँ कि आपको चोट लगी है, गिरे हैं या खून बह रहा है। इस आधार पर, **आपातकालीन (EMERGENCY)** चिकित्सा की सलाह दी जाती है। कृपया तुरंत अस्पताल जाएं।",
            "gu": "હું સમજું છું કે તમને ઈજા થઈ છે, પડ્યા છો અથવા લોહી વહી રહ્યું છે. આના આધારે, **તાત્કાલિક (EMERGENCY)** સારવારની સલાહ છે. કૃપા કરીને તાત્કાલિક હોસ્પિટલ પહોંચો.",
            "mr": "मला समजते की तुम्हाला दुखापत झाली आहे, पडला आहात किंवा रक्तस्त्राव होत आहे. या आधारावर, **आणीबाणी (EMERGENCY)** उपचाराचा सल्ला दिला जातो. कृपया त्वरित रुग्णालयात जा.",
            "ta": "உங்களுக்கு காயம், வீழ்ச்சி அல்லது இரத்தப்போக்கு ஏற்பட்டுள்ளதை நான் புரிந்துகொள்கிறேன். இதன் அடிப்படையில் **அவசர (EMERGENCY)** சிகிச்சை பரிந்துரைக்கப்படுகிறது. உடனடியாக மருத்துவமனைக்குச் செல்லவும்."
        }
        return {
            "text": injury_reply.get(lang, injury_reply["en"]),
            "urgency": "EMERGENCY", "urgency_label": _urgency_label(lang, "EMERGENCY"),
            "reason": "Physical trauma, injury, or bleeding reported.",
            "advice": ADVICE_TEXT.get(lang, ADVICE_TEXT["en"])["EMERGENCY"],
            "facility": facility, "symptoms": ["Injury / Bleeding / Trauma"], "matched_aliases": [],
            "context": {}, "likely_conditions": [], "next_question": "",
            "assistant_insight": "Physical trauma suspected based on keywords.", "is_greeting": False,
        }

    text_norm = _normalize(message)
    is_affirmative = text_norm in ["yes", "y", "yeah", "yep", "हां", "हा", "હા", "हो", "ஆம்", "ஆமாம்"]
    is_negative = text_norm in ["no", "n", "nope", "नहीं", "ना", "ના", "नाही", "இல்லை"]

    pending = request.session.get("pending_symptom")
    symptoms, matched_aliases = _extract_symptoms(message)

    if is_affirmative and pending and pending not in symptoms:
        symptoms.append(pending)
        
    bmsg = text_norm.replace("?", "").strip()
    if bmsg in ["what is this", "who are you", "what are you", "what do you do", "help", "about you"]:
        reply_dict = {
            "en": "I am SwasthyaSaathi, an AI health assistant. I can help triage your symptoms and recommend care. Please describe what you are experiencing.",
            "hi": "मैं स्वास्थ्यसाथी, एक AI स्वास्थ्य सहायक हूँ। मैं आपके लक्षणों का आकलन करने में मदद कर सकता हूँ। कृपया अपने लक्षण बताएं।",
            "gu": "હું સ્વાસ્થ્યસાથી, એક AI આરોગ્ય સહાયક છું. કૃપા કરીને તમારા લક્ષણ જણાવો.",
            "mr": "मी स्वास्थ्यसाथी आहे, एक AI आरोग्य सहाय्यक. कृपया तुमची लक्षणे सांगा.",
            "ta": "நான் ஸ்வாஸ்த்யசாத்தி, ஒரு AI சுசுகாதார உதவியாளர். உங்கள் அறிகுறிகளை சொல்லுங்கள்."
        }
        reply_text = reply_dict.get(lang, reply_dict["en"])
        facility = _get_facility_for_urgency("VISIT CLINIC", lang, lat, lng)
        return {
            "text": reply_text,
            "urgency": "Info", "urgency_label": "Information", "reason": "General bot query.", "advice": "",
            "facility": facility, "symptoms": [], "matched_aliases": [],
            "context": _extract_context(message), "likely_conditions": [],
            "next_question": "",
            "assistant_insight": "User asked about the bot.", "is_greeting": False,
        }
        
    if not symptoms and not is_negative and not is_affirmative:
        wiki_summary = _search_wikipedia(message, lang)
        facility = _get_facility_for_urgency("VISIT CLINIC", lang, lat, lng)
        
        if wiki_summary:
            # Found info online
            return {
                "text": wiki_summary,
                "urgency": "Info", "urgency_label": "Information", "reason": "General knowledge query.", "advice": "",
                "facility": facility, "symptoms": [], "matched_aliases": [],
                "context": _extract_context(message), "likely_conditions": [],
                "next_question": QUESTION_TEXT.get(lang, QUESTION_TEXT["en"])["default"],
                "assistant_insight": "Wikipedia search fallback used.", "is_greeting": False,
            }

        reply_text = NO_SYMPTOM_REPLY.get(lang, NO_SYMPTOM_REPLY["en"])
        return {
            "text": reply_text,
            "urgency": None, "urgency_label": "", "reason": "", "advice": "",
            "facility": facility, "symptoms": [], "matched_aliases": [],
            "context": _extract_context(message), "likely_conditions": [],
            "next_question": QUESTION_TEXT.get(lang, QUESTION_TEXT["en"])["default"],
            "assistant_insight": reply_text, "is_greeting": False,
        }
    
    history = request.session.get("chat_symptoms", [])
    merged_symptoms = list(set(history + symptoms))
    request.session["chat_symptoms"] = merged_symptoms
    
    new_pending = _get_pending_symptom(merged_symptoms)
    request.session["pending_symptom"] = new_pending

    context = _extract_context(message)
    predicted = _predict_diseases(merged_symptoms)
    urgency, reason = _risk_from_symptoms(merged_symptoms, context, predicted)
    facility = _get_facility_for_urgency(urgency, lang, lat, lng)
    advice = ADVICE_TEXT.get(lang, ADVICE_TEXT["en"])[urgency]

    if not merged_symptoms:
        reply_text = NO_SYMPTOM_REPLY.get(lang, NO_SYMPTOM_REPLY["en"])
        return {
            "text": reply_text,
            "urgency": None, "urgency_label": "", "reason": "", "advice": "",
            "facility": facility, "symptoms": [], "matched_aliases": [],
            "context": context, "likely_conditions": [],
            "next_question": QUESTION_TEXT.get(lang, QUESTION_TEXT["en"])["default"],
            "assistant_insight": reply_text, "is_greeting": False,
        }

    # Localize reason key → human-readable string in user's language
    localized_reason = REASON_TEXT.get(reason, {}).get(lang) or REASON_TEXT.get(reason, {}).get("en", reason)

    # Localize disease names in predicted list
    localized_predicted = []
    for item in predicted:
        loc = dict(item)
        loc["name"] = DISEASE_NAMES.get(item["name"], {}).get(lang) or DISEASE_NAMES.get(item["name"], {}).get("en") or item["name"]
        
        translated_precautions = []
        for p in item["precautions"]:
            p_clean = p.strip()
            translated_p = PRECAUTION_TRANSLATIONS.get(lang, {}).get(p_clean, p_clean)
            translated_precautions.append(translated_p.capitalize() if lang=="en" else translated_p)
        loc["precautions"] = translated_precautions
        
        localized_predicted.append(loc)

    display_symptoms = [_human_symptom(s).title() for s in merged_symptoms]

    names = ", ".join(display_symptoms)
    if localized_predicted:
        top_name = localized_predicted[0]["name"]
        insight = INSIGHT_DETECTED.get(lang, INSIGHT_DETECTED["en"]).format(names=names, top=top_name)
    else:
        insight = INSIGHT_NO_MATCH.get(lang, INSIGHT_NO_MATCH["en"]).format(names=names)

    conv = CONVERSATIONAL_RESPONSE.get(lang, CONVERSATIONAL_RESPONSE["en"])
    urg_label = _urgency_label(lang, urgency)
    text = conv.format(symptoms=names, urgency=urg_label, advice=advice)
    
    return {
        "text": text,
        "urgency": urgency,
        "urgency_label": urg_label,
        "reason": localized_reason,
        "advice": advice,
        "facility": facility,
        "symptoms": display_symptoms,
        "matched_aliases": matched_aliases,
        "context": context,
        "likely_conditions": localized_predicted,
        "next_question": _next_question(lang, merged_symptoms),
        "assistant_insight": insight,
        "is_greeting": False,
    }

from django.contrib.auth import login
from core.models import User, Patient
from django.shortcuts import redirect

def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        e_contact = request.POST.get('emergency_contact', '').strip()
        e_email = request.POST.get('emergency_email', '').strip()
        
        age_str = request.POST.get('age', '30').strip()
        age = int(age_str) if age_str.isdigit() else 30
        
        gender = request.POST.get('gender', 'O').strip()
        
        med_history_str = request.POST.get('medical_history', '').strip()
        medical_history = [item.strip() for item in med_history_str.split(',')] if med_history_str else []
        
        allergies_str = request.POST.get('allergies', '').strip()
        allergies = [item.strip() for item in allergies_str.split(',')] if allergies_str else []

        if username and password:
            try:
                user = User.objects.create_user(username=username, email=email, password=password, user_type='patient')
                Patient.objects.create(
                    user=user,
                    age=age,
                    gender=gender,
                    medical_history=medical_history,
                    allergies=allergies,
                    emergency_contact=e_contact,
                    emergency_email=e_email
                )
                login(request, user)
                return redirect('home')
            except Exception as e:
                return render(request, "core/signup.html", {"error": str(e)})

    return render(request, "core/signup.html")

@login_required
@require_POST
def api_profile_update(request):
    try:
        profile = request.user.patient_profile
        age_str = request.POST.get('age', '').strip()
        if age_str.isdigit():
            profile.age = int(age_str)
            
        gender = request.POST.get('gender', '').strip()
        if gender in ['M', 'F', 'O']:
            profile.gender = gender
            
        med_history_str = request.POST.get('medical_history', '').strip()
        if med_history_str:
            profile.medical_history = [item.strip() for item in med_history_str.split(',') if item.strip()]
        else:
            profile.medical_history = []
            
        allergies_str = request.POST.get('allergies', '').strip()
        if allergies_str:
            profile.allergies = [item.strip() for item in allergies_str.split(',') if item.strip()]
        else:
            profile.allergies = []
            
        profile.save()
    except Exception as e:
        print(f"Profile update error: {e}")
    return redirect('home')

def home(request):
    lang_payload = {
        "ui": UI_TEXT,
        "quickReplies": QUICK_REPLIES,
        "emergencyItems": EMERGENCY_ITEMS,
        "symptomAliases": SYMPTOM_ALIASES,
    }
    return render(request, "core/index.html", {"lang_payload": json.dumps(lang_payload, ensure_ascii=False)})

def landing(request):
    return render(request, "core/landing.html")



def detect_language_from_text(text: str, default_lang: str) -> str:
    if re.search(r'[\u0b80-\u0bff]', text): return "ta"
    if re.search(r'[\u0a80-\u0aff]', text): return "gu"
    if re.search(r'[\u0900-\u097f]', text):
        return default_lang if default_lang in ["hi", "mr"] else "hi"
    return default_lang

@require_POST
@csrf_exempt
def api_chat(request):
    payload = json.loads(request.body.decode("utf-8"))
    message = payload.get("message", "").strip()
    lang = payload.get("language", "en")
    lat = payload.get("lat")
    lng = payload.get("lng")
    
    if message == "/clear_session":
        request.session["chat_symptoms"] = []
        request.session["pending_symptom"] = None
        return JsonResponse({"cleared": True})
        
    if not message:
        return JsonResponse({"error": "Message is required."}, status=400)
    
    detected_lang = detect_language_from_text(message, lang)
    if detected_lang != lang:
        lang = detected_lang
    
    reply = _build_ai_reply(request, message, lang, lat, lng)
    reply["detected_language"] = lang
    if reply.get("urgency") == "EMERGENCY" and request.user.is_authenticated:
        try:
            from .models import Patient
            patient = Patient.objects.get(user=request.user)
            if patient.emergency_email:
                from django.core.mail import send_mail
                send_mail(
                    subject=f"URGENT: Emergency Medical Alert for {request.user.get_full_name() or request.user.username}",
                    message=f"Hello,\n\nThis is an automated alert from SwasthyaSaathi.\n\n"
                            f"{request.user.get_full_name() or request.user.username} has just reported symptoms that indicate a potential medical EMERGENCY.\n\n"
                            f"Reported Symptoms: {', '.join(reply.get('symptoms', []))}\n"
                            f"AI Assessment: {reply.get('reason', '')}\n\n"
                            f"Please check on them immediately or arrange for emergency services (108).\n\n"
                            f"Thank you,\nSwasthyaSaathi System",
                    from_email="alerts@swasthyasaathi.local",
                    recipient_list=[patient.emergency_email],
                    fail_silently=True,
                )
        except Exception as e:
            print(f"Failed to send emergency email: {e}")

    # Generate a persistent ChatSession UUID to support PDF Referrals and Profile Dashboards
    if request.user.is_authenticated and reply.get("urgency"):
        try:
            from .models import ChatSession
            import uuid
            session_id = str(uuid.uuid4())
            ChatSession.objects.create(
                user=request.user,
                session_id=session_id,
                symptoms=reply.get("symptoms", []),
                predicted_conditions=[c["name"] for c in reply.get("likely_conditions", [])],
                urgency_level=reply.get("urgency", ""),
                recommended_facility_type=reply.get("facility", {}).get("type", "")
            )
            reply["session_id"] = session_id
        except Exception as e:
            print(f"Failed to save ChatSession: {e}")

    return JsonResponse(reply)
import csv
from django.core.cache import cache
from django.http import HttpResponse

class DummyRequest:
    def __init__(self, session_data):
        self.session = session_data

@csrf_exempt
def whatsapp_webhook(request):
    sender = request.POST.get('From', '')
    message = request.POST.get('Body', '').strip()
    if not message:
        return HttpResponse("OK")
    
    # Simple session tracking via Django cache using sender phone number
    cache_key = f"wa_session_{sender}"
    session_data = cache.get(cache_key, {})
    dummy_req = DummyRequest(session_data)
    
    lang = detect_language_from_text(message, "en")
    reply = _build_ai_reply(dummy_req, message, lang)
    
    # Save updated session
    cache.set(cache_key, dummy_req.session, timeout=3600)
    
    # Build SMS / WhatsApp response
    response_text = f"*{reply['urgency_label']}*\n\n{reply['text']}\n\n"
    if reply['symptoms']:
        response_text += f"Symptoms: {', '.join(reply['symptoms'])}\n"
    if reply['likely_conditions']:
        response_text += "\nPossible Conditions:\n"
        for cond in reply['likely_conditions']:
            response_text += f"• {cond['name']} ({cond['score']}%)\n"
    if reply['next_question']:
        response_text += f"\n❓ {reply['next_question']}"
        
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{response_text}</Message>
</Response>"""
    return HttpResponse(xml, content_type="text/xml")


def export_patients_csv(request):
    # Enforce admin dashboard authentication
    if not request.session.get("is_custom_admin"):
        return redirect("admin_login")
        
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="triage_patients_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Patient Name', 'Phone', 'Village', 'Age', 'Gender', 'Medical History', 'Registered Date'])
    
    from core.models import Patient
    for p in Patient.objects.select_related('user').all():
        history = ", ".join(p.medical_history) if p.medical_history else "None"
        writer.writerow([
            p.user.get_full_name() or p.user.username,
            p.user.phone,
            p.user.village,
            p.age,
            p.gender,
            history,
            p.created_at.strftime("%Y-%m-%d %H:%M")
        ])
    return response


def _fetch_live_facilities_osm(lat: float, lng: float, lang: str) -> list[dict]:
    import urllib.request, json, math
    query = f"""
    [out:json];
    (
      node["amenity"="hospital"](around:25000, {lat}, {lng});
      node["amenity"="clinic"](around:25000, {lat}, {lng});
      node["amenity"="pharmacy"](around:25000, {lat}, {lng});
    );
    out;
    """
    url = "https://overpass-api.de/api/interpreter"
    try:
        req = urllib.request.Request(url, data=query.encode('utf-8'), headers={'User-Agent': 'SwasthyaSaathiBot/1.0'})
        with urllib.request.urlopen(req, timeout=5.0) as response:
            data = json.loads(response.read().decode('utf-8'))
            elements = data.get("elements", [])
            
            types_dict = {"hospital": [], "clinic": [], "pharmacy": []}
            
            for el in elements:
                tags = el.get("tags", {})
                fac_type = tags.get("amenity")
                if fac_type not in types_dict: continue
                
                olat, olng = el["lat"], el["lon"]
                
                # Haversine distance
                lat1, lon1 = math.radians(lat), math.radians(lng)
                lat2, lon2 = math.radians(olat), math.radians(olng)
                a = math.sin((lat2-lat1)/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin((lon2-lon1)/2)**2
                dist = 6371 * 2 * math.asin(math.sqrt(a))
                
                name = tags.get("name", f"Nearby {fac_type.capitalize()}")
                if not name or name.isdigit(): name = f"Nearby {fac_type.capitalize()}"
                
                fac = {
                    "id": str(el["id"]),
                    "name": name,
                    "distance_km": round(dist, 1),
                    "type": fac_type,
                    "phone": tags.get("phone", "Not available"),
                    "address": ", ".join(filter(None, [
                        tags.get("addr:street", ""),
                        tags.get("addr:city", "")
                    ])) or "Location on map",
                    "availability": "24/7" if tags.get("opening_hours") == "24/7" else "Open",
                    "map_url": f"https://www.google.com/maps/search/?api=1&query={olat},{olng}"
                }
                types_dict[fac_type].append(fac)
                
            results = []
            for t, lst in types_dict.items():
                lst.sort(key=lambda x: x["distance_km"])
                # Take exactly 10 of each type
                results.extend(lst[:10])
                
            for r in results:
                r["type_label"] = TYPE_LABELS.get(lang, TYPE_LABELS["en"]).get(r["type"], r["type"])
                
            results.sort(key=lambda x: x["distance_km"])
            return results
    except Exception as e:
        print("Overpass error:", e)
        return []

@require_GET
def api_facilities(request):
    """Return facilities from DB, OSM, or falling back to JSON file."""
    import math
    from core.models import Facility
    lang = request.GET.get("language", "en")
    urgency = request.GET.get("urgency")
    facility_type = request.GET.get("type", "all")
    user_lat = request.GET.get("lat")
    user_lng = request.GET.get("lng")
    
    # 1. LIVE OPENSTREETMAP API OVERPASS
    if user_lat and user_lng:
        try:
            live_facs = _fetch_live_facilities_osm(float(user_lat), float(user_lng), lang)
            if live_facs:
                if urgency:
                    preferred = {"emergency": "hospital", "clinic": "clinic", "selfcare": "pharmacy"}.get(urgency.lower())
                    if preferred:
                        live_facs = [f for f in live_facs if f["type"] == preferred]
                if facility_type != "all":
                    live_facs = [f for f in live_facs if f["type"] == facility_type]
                return JsonResponse({"facilities": live_facs})
        except ValueError:
            pass

    # 2. LOCAL DB
    db_facilities = Facility.objects.all()
    if db_facilities.exists():
        if facility_type != "all":
            db_facilities = db_facilities.filter(facility_type=facility_type)
        if urgency:
            preferred = {"emergency": "hospital", "clinic": "clinic", "selfcare": "pharmacy"}.get(urgency.lower())
            if preferred:
                db_facilities = db_facilities.filter(facility_type=preferred)
        result = []
        for f in db_facilities:
            dist = 1.0  # default when no user coords provided
            if user_lat and user_lng and f.latitude and f.longitude:
                try:
                    lat1, lon1 = math.radians(float(user_lat)), math.radians(float(user_lng))
                    lat2, lon2 = math.radians(float(f.latitude)), math.radians(float(f.longitude))
                    a = math.sin((lat2-lat1)/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin((lon2-lon1)/2)**2
                    dist = 6371 * 2 * math.asin(math.sqrt(a))
                except (ValueError, TypeError):
                    pass
            result.append({
                "id": f.id,
                "name": f.name,
                "type": f.facility_type,
                "distance_km": round(dist, 1),
                "phone": f.phone,
                "address": f.address,
                "availability": "24/7" if f.is_24_7 else "Open",
                "type_label": TYPE_LABELS.get(lang, TYPE_LABELS["en"]).get(f.facility_type, f.facility_type),
                "map_url": f"https://www.google.com/maps/search/?api=1&query={f.latitude},{f.longitude}" if (f.latitude and f.longitude) else f"https://www.google.com/maps/search/{urllib.parse.quote(f.name)}"
            })
        if user_lat and user_lng:
            result.sort(key=lambda x: x["distance_km"])
        return JsonResponse({"facilities": result})

    # 3. FALLBACK JSON
    facilities = _load_facilities()
    if urgency:
        preferred = {"emergency": "hospital", "clinic": "clinic", "selfcare": "pharmacy"}.get(urgency.lower())
        if preferred:
            facilities = [f for f in facilities if f["type"] == preferred]
    if facility_type != "all":
        facilities = [f for f in facilities if f["type"] == facility_type]
        
    localized_facs = []
    for f in facilities:
        dist = f.get("distance_km", 1.0)
        if user_lat and user_lng and "latitude" in f and "longitude" in f:
            try:
                lat1, lon1 = math.radians(float(user_lat)), math.radians(float(user_lng))
                lat2, lon2 = math.radians(float(f["latitude"])), math.radians(float(f["longitude"]))
                a = math.sin((lat2-lat1)/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin((lon2-lon1)/2)**2
                dist = 6371 * 2 * math.asin(math.sqrt(a))
            except (ValueError, TypeError):
                pass
        
        lf = _localized_facility(f, lang)
        lf["distance_km"] = round(dist, 1)
        import urllib.parse
        lf["map_url"] = f"https://www.google.com/maps/search/?api=1&query={f['latitude']},{f['longitude']}" if ("latitude" in f and "longitude" in f) else f"https://www.google.com/maps/search/{urllib.parse.quote(f['name'])}"
        localized_facs.append(lf)
    
    localized_facs = sorted(localized_facs, key=lambda x: x["distance_km"])
    return JsonResponse({"facilities": localized_facs})


@require_GET
def api_patients(request):
    """Return patients from DB."""
    from core.models import Patient
    patients = Patient.objects.select_related('user').order_by('-created_at')
    result = []
    for p in patients:
        result.append({
            "id": p.id,
            "name": p.user.get_full_name() or p.user.username,
            "age": p.age,
            "gender": "Male" if p.gender == "M" else "Female" if p.gender == "F" else "Other",
            "village": p.user.village,
            "phone": p.user.phone,
            "condition": ", ".join(p.medical_history) if p.medical_history else "General checkup",
            "priority": "high" if p.medical_history else "medium",
            "last_visit": p.updated_at.strftime("%Y-%m-%d"),
        })
    return JsonResponse({"patients": result})


@require_POST
@csrf_exempt
def api_patients_add(request):
    """Add a patient to the DB (creates a User + Patient record)."""
    from core.models import User, Patient
    import uuid
    data = json.loads(request.body.decode("utf-8"))
    name = data.get("name", "Unknown")
    parts = name.strip().split(" ", 1)
    first_name = parts[0]
    last_name = parts[1] if len(parts) > 1 else ""
    username = f"patient_{uuid.uuid4().hex[:8]}"
    try:
        user = User.objects.create_user(
            username=username,
            email=f"{username}@swasthya.local",
            password=uuid.uuid4().hex,
            user_type='patient',
            phone=data.get("phone", ""),
            village=data.get("village", ""),
            first_name=first_name,
            last_name=last_name,
        )
        condition = data.get("condition", "General checkup")
        patient = Patient.objects.create(
            user=user,
            age=int(data.get("age", 0) or 0),
            gender={"Male": "M", "Female": "F"}.get(data.get("gender", ""), "O"),
            medical_history=[condition] if condition else [],
            allergies=[],
        )
        new_item = {
            "id": patient.id,
            "name": name,
            "age": patient.age,
            "gender": data.get("gender", "Unknown"),
            "village": user.village,
            "phone": user.phone,
            "condition": condition,
            "priority": data.get("priority", "medium"),
            "last_visit": patient.created_at.strftime("%Y-%m-%d"),
        }
        # Return updated list
        all_patients = []
        for p in Patient.objects.select_related('user').order_by('-created_at'):
            all_patients.append({
                "id": p.id,
                "name": p.user.get_full_name() or p.user.username,
                "age": p.age,
                "gender": "Male" if p.gender == "M" else "Female" if p.gender == "F" else "Other",
                "village": p.user.village,
                "phone": p.user.phone,
                "condition": ", ".join(p.medical_history) if p.medical_history else "General checkup",
                "priority": "high" if p.medical_history else "medium",
                "last_visit": p.updated_at.strftime("%Y-%m-%d"),
            })
        return JsonResponse({"patient": new_item, "patients": all_patients})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

@csrf_exempt
def admin_login_view(request):
    if request.method == "POST":
        u = request.POST.get("username", "").strip()
        p = request.POST.get("password", "").strip()
        if u == "admin" and p == "admin":
            request.session['is_custom_admin'] = True
            from django.shortcuts import redirect
            return redirect('admin_dashboard')
        else:
            from django.shortcuts import render
            return render(request, "core/admin_login.html", {"error": "Invalid admin credentials"})
            
    from django.shortcuts import render
    return render(request, "core/admin_login.html")


def admin_dashboard(request):
    # Verify the user has passed the custom manual admin gate
    if not request.session.get('is_custom_admin'):
        from django.shortcuts import redirect
        return redirect('admin_login')

    from core.models import Patient
    import json
    from collections import Counter
    from django.shortcuts import render

    patients = Patient.objects.select_related('user').all()
    
    villages = []
    conditions = []
    patient_list = []
    
    for p in patients:
        vil = p.user.village if p.user.village else 'Unknown'
        villages.append(vil)
        
        conds = p.medical_history if p.medical_history else ['General checkup']
        conditions.extend(conds)
        
        patient_list.append({
            'name': p.user.get_full_name() or p.user.username,
            'age': p.age,
            'gender': p.get_gender_display(),
            'village': vil,
            'condition': ', '.join(conds),
            'date': p.created_at.strftime("%Y-%m-%d")
        })
        
    # Order by dates descending
    patient_list.sort(key=lambda x: x['date'], reverse=True)
        
    village_counts = dict(Counter(villages))
    if 'Unknown' in village_counts and len(village_counts) > 1:
        # Move unknown to the end of the lists for visual tidiness, or just let sorting naturally handle it
        pass
        
    # Sort strictly by value
    village_counts = dict(sorted(village_counts.items(), key=lambda item: item[1], reverse=True))
    condition_counts = dict(Counter(conditions))
    condition_counts = dict(sorted(condition_counts.items(), key=lambda item: item[1], reverse=True)[:10])

    context = {
        'village_labels': json.dumps(list(village_counts.keys())),
        'village_data': json.dumps(list(village_counts.values())),
        'condition_labels': json.dumps(list(condition_counts.keys())),
        'condition_data': json.dumps(list(condition_counts.values())),
        'total_patients': len(patients),
        'recent_patients': patient_list[:50]
    }
    
    return render(request, 'core/admin_dashboard.html', context)



@require_GET
def api_medicines(request):
    """Return medicine reminders from DB, falling back to defaults."""
    from core.models import MedicineReminder, Medicine, MedicineIntake
    reminders = MedicineReminder.objects.select_related('medicine').filter(is_active=True).order_by('next_dose')
    if reminders.exists():
        result = []
        for r in reminders:
            result.append({
                "id": r.id,
                "name": r.medicine.name,
                "time": r.next_dose.astimezone().strftime("%I:%M %p"),
                "taken": MedicineIntake.objects.filter(reminder=r, was_taken=True).exists(),
                "dosage": r.dosage,
                "frequency": r.frequency,
            })
        return JsonResponse({"medicines": result})

    # Fallback: show medicines from Medicine table as a simple list
    medicines = Medicine.objects.all()[:10]
    result = [
        {"id": m.id, "name": m.name, "time": "08:00 AM", "taken": False}
        for m in medicines
    ]
    return JsonResponse({"medicines": result})


@require_POST
@csrf_exempt
def api_medicine_toggle(request, medicine_id: int):
    """Toggle medicine reminder taken status."""
    from core.models import MedicineReminder, MedicineIntake
    try:
        reminder = MedicineReminder.objects.get(id=medicine_id)
        last_intake = MedicineIntake.objects.filter(reminder=reminder).order_by('-taken_at').first()
        currently_taken = last_intake.was_taken if last_intake else False
        MedicineIntake.objects.create(reminder=reminder, was_taken=not currently_taken)
        item = {
            "id": reminder.id,
            "name": reminder.medicine.name,
            "time": reminder.next_dose.astimezone().strftime("%I:%M %p"),
            "taken": not currently_taken,
        }
        return JsonResponse({"medicine": item})
    except MedicineReminder.DoesNotExist:
        return JsonResponse({"error": "Medicine not found"}, status=404)

@login_required
@csrf_exempt
def api_profile_medicines(request):
    """Manage personalized custom medicines."""
    try:
        profile = request.user.patient_profile
        
        if request.method == "GET":
            return JsonResponse({"medicines": profile.custom_medicines})
            
        import json
        data = json.loads(request.body)
        
        if request.method == "POST":
            med_id = data.get("id", "")
            if med_id:
                for m in profile.custom_medicines:
                    if m.get("id") == med_id:
                        m["name"] = data.get("name", "")
                        m["quantity"] = data.get("quantity", "")
                        m["time"] = data.get("time", "")
                profile.save()
                return JsonResponse({"status": "Updated", "id": med_id})
            else:
                import uuid
                new_med = {
                    "id": str(uuid.uuid4()),
                    "name": data.get("name", ""),
                    "quantity": data.get("quantity", ""),
                    "time": data.get("time", ""),
                    "taken": False
                }
                profile.custom_medicines.append(new_med)
            profile.save()
            return JsonResponse({"status": "Added", "medicine": new_med if not med_id else None})
            
        elif request.method == "DELETE":
            target_id = data.get("id")
            profile.custom_medicines = [m for m in profile.custom_medicines if m.get("id") != target_id]
            profile.save()
            return JsonResponse({"status": "Deleted", "id": target_id})
            
        elif request.method == "PUT":
            target_id = data.get("id")
            for m in profile.custom_medicines:
                if m.get("id") == target_id:
                    m["taken"] = not m.get("taken", False)
            profile.save()
            return JsonResponse({"status": "Toggled", "id": target_id})
            
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

@login_required
@require_POST
@csrf_exempt
def api_emergency_sos(request):
    try:
        profile = request.user.patient_profile
        if not profile.emergency_email and not profile.emergency_contact:
            return JsonResponse({"error": "No emergency contact registered in profile"}, status=400)
            
        data = {}
        try:
            data = json.loads(request.body)
        except:
            pass
            
        location_text = "Location: Unknown (GPS disabled on patient device)"
        if data.get('lat') and data.get('lon'):
            location_text = f"Live GPS Coordinates: {data['lat']}, {data['lon']}\nMap: https://maps.google.com/?q={data['lat']},{data['lon']}"
            
        subject = f"URGENT: Emergency SOS Alert from {request.user.get_full_name() or request.user.username}"
        message = f"EMERGENCY SOS ALERT!\n\n{request.user.get_full_name() or request.user.username} has just triggered a high-priority Emergency SOS from the SwasthyaSaathi app. They urgently need your assistance.\n\n{location_text}\n\nPlease contact them immediately at their registered phone number or proceed to their location."
        
        if profile.emergency_email:
            try:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@swasthyasaathi.com'),
                    recipient_list=[profile.emergency_email],
                    fail_silently=False,
                )
            except Exception as mail_err:
                return JsonResponse({"error": f"Failed to send email. Check SMTP credentials: {str(mail_err)}"}, status=500)
        
        return JsonResponse({"status": "Success", "message": "Emergency alerts dispatched successfully."})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@login_required
def api_referral_pdf(request, session_id):
    try:
        from core.models import ChatSession
        from django.shortcuts import render, get_object_or_404
        from django.http import HttpResponse
        
        session = get_object_or_404(ChatSession, session_id=session_id)
        
        # Security: Allow only the owning user (or an ASHA worker acting on behalf, future proof via groups/superusers) to print
        if session.user != request.user and not request.user.is_superuser:
            return HttpResponse("Unauthorized to view this referral slip.", status=403)
            
        patient = getattr(session.user, 'patient_profile', None)
        
        return render(request, "core/referral.html", {
            "session": session,
            "patient": patient
        })
    except Exception as e:
        return HttpResponse(f"Server Error generating PDF: {str(e)}", status=500)
