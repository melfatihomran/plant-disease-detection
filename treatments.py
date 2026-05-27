"""
treatments.py
Disease treatment recommendations — English + Arabic
"""

TREATMENTS = {
    "Tomato___Early_blight": {
        "en": {
            "description": "Early Blight is a fungal disease causing dark brown spots with yellow rings on leaves.",
            "steps": [
                "Remove and destroy all infected leaves immediately.",
                "Apply copper-based fungicide (e.g. Bordeaux mixture) every 7-10 days.",
                "Avoid overhead watering — water at the base of the plant.",
                "Ensure good spacing between plants for airflow.",
                "Rotate crops — don't plant tomatoes in the same spot next season."
            ]
        },
        "ar": {
            "description": "اللفحة المبكرة مرض فطري يسبب بقعاً بنية داكنة بحلقات صفراء على الأوراق.",
            "steps": [
                "قم بإزالة وإتلاف جميع الأوراق المصابة فوراً.",
                "رش مبيد فطري نحاسي (مثل مزيج بوردو) كل 7-10 أيام.",
                "تجنب الري من الأعلى — اسقِ من قاعدة النبات.",
                "تأكد من التباعد الجيد بين النباتات لتحسين تدفق الهواء.",
                "دوّر المحاصيل — لا تزرع الطماطم في نفس المكان الموسم القادم."
            ]
        },
        "severity": "Medium",
        "spread_risk": "High",
        "color": "orange"
    },

    "Tomato___Late_blight": {
        "en": {
            "description": "Late Blight is a fast-spreading fungal disease causing dark water-soaked lesions.",
            "steps": [
                "Act immediately — Late Blight spreads extremely fast.",
                "Remove all infected plant parts and burn them (do not compost).",
                "Apply systemic fungicide (e.g. Metalaxyl or Mancozeb) urgently.",
                "Spray neighboring healthy plants as a precaution.",
                "Improve drainage to reduce moisture around roots."
            ]
        },
        "ar": {
            "description": "اللفحة المتأخرة مرض فطري سريع الانتشار يسبب آفات داكنة مشبعة بالماء.",
            "steps": [
                "تصرف فوراً — اللفحة المتأخرة تنتشر بسرعة شديدة.",
                "أزل جميع أجزاء النبات المصابة وأحرقها (لا تضعها في السماد).",
                "رش مبيداً فطرياً جهازياً (مثل ميتالاكسيل أو مانكوزيب) بشكل عاجل.",
                "رش النباتات السليمة المجاورة كإجراء احترازي.",
                "حسّن الصرف لتقليل الرطوبة حول الجذور."
            ]
        },
        "severity": "High",
        "spread_risk": "Very High",
        "color": "red"
    },

    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": {
        "en": {
            "description": "Yellow Leaf Curl Virus is spread by whiteflies, causing leaves to curl and turn yellow.",
            "steps": [
                "There is no cure — remove and destroy infected plants immediately.",
                "Control whitefly population using yellow sticky traps.",
                "Apply insecticide (e.g. Imidacloprid) to kill whiteflies.",
                "Use reflective mulch to repel whiteflies.",
                "Plant resistant tomato varieties in the next season."
            ]
        },
        "ar": {
            "description": "فيروس تجعد وصفار أوراق الطماطم ينتشر عن طريق الذباب الأبيض ويسبب تجعد الأوراق واصفرارها.",
            "steps": [
                "لا يوجد علاج — أزل النباتات المصابة وأتلفها فوراً.",
                "تحكم في أعداد الذباب الأبيض باستخدام مصائد لاصقة صفراء.",
                "رش مبيد حشري (مثل إيميداكلوبريد) للقضاء على الذباب الأبيض.",
                "استخدم غطاء تربة عاكساً لطرد الذباب الأبيض.",
                "ازرع أصناف طماطم مقاومة في الموسم القادم."
            ]
        },
        "severity": "High",
        "spread_risk": "High",
        "color": "red"
    },

    "Tomato___Septoria_leaf_spot": {
        "en": {
            "description": "Septoria Leaf Spot causes small circular spots with dark borders on lower leaves.",
            "steps": [
                "Remove infected lower leaves as soon as spots appear.",
                "Apply fungicide containing chlorothalonil or copper.",
                "Water at the base — avoid wetting the foliage.",
                "Mulch around plants to prevent soil splash.",
                "Destroy infected plant debris after harvest."
            ]
        },
        "ar": {
            "description": "تبقع سبتوريا يسبب بقعاً دائرية صغيرة بحدود داكنة على الأوراق السفلية.",
            "steps": [
                "أزل الأوراق السفلية المصابة فور ظهور البقع.",
                "رش مبيداً فطرياً يحتوي على كلوروثالونيل أو نحاس.",
                "اسقِ من القاعدة — تجنب ترطيب الأوراق.",
                "ضع غطاء حول النباتات لمنع تناثر التربة.",
                "أتلف بقايا النباتات المصابة بعد الحصاد."
            ]
        },
        "severity": "Medium",
        "spread_risk": "Medium",
        "color": "orange"
    },

    "Tomato___healthy": {
        "en": {
            "description": "This plant is healthy. No disease detected.",
            "steps": [
                "Continue regular watering and fertilization schedule.",
                "Monitor weekly for early signs of disease.",
                "Maintain good spacing for airflow.",
                "Keep weeds away from plant base."
            ]
        },
        "ar": {
            "description": "هذا النبات سليم. لم يتم اكتشاف أي مرض.",
            "steps": [
                "استمر في جدول الري والتسميد المنتظم.",
                "راقب أسبوعياً للكشف المبكر عن علامات الأمراض.",
                "حافظ على التباعد الجيد لتدفق الهواء.",
                "أبعد الأعشاب الضارة عن قاعدة النبات."
            ]
        },
        "severity": "None",
        "spread_risk": "None",
        "color": "green"
    },

    "Potato___Early_blight": {
        "en": {
            "description": "Early Blight on potato causes dark concentric ring spots on older leaves.",
            "steps": [
                "Remove and dispose of infected leaves carefully.",
                "Apply fungicide (Mancozeb or Chlorothalonil) every 10-14 days.",
                "Ensure adequate plant nutrition — stressed plants are more vulnerable.",
                "Avoid excessive nitrogen fertilizer.",
                "Harvest tubers promptly when mature to avoid tuber infection."
            ]
        },
        "ar": {
            "description": "اللفحة المبكرة على البطاطس تسبب بقعاً داكنة بحلقات متحدة المركز على الأوراق القديمة.",
            "steps": [
                "أزل الأوراق المصابة وتخلص منها بعناية.",
                "رش مبيداً فطرياً (مانكوزيب أو كلوروثالونيل) كل 10-14 يوماً.",
                "تأكد من التغذية الكافية للنبات — النباتات المجهدة أكثر عرضة للإصابة.",
                "تجنب الإفراط في استخدام الأسمدة النيتروجينية.",
                "احصد الدرنات فور نضجها لتجنب إصابة الدرنات."
            ]
        },
        "severity": "Medium",
        "spread_risk": "Medium",
        "color": "orange"
    },

    "Potato___Late_blight": {
        "en": {
            "description": "Late Blight on potato is the most devastating disease — caused by the same pathogen that caused the Irish Famine.",
            "steps": [
                "Act immediately — this disease can destroy an entire field in days.",
                "Remove all infected plants and burn them.",
                "Apply systemic fungicide (Metalaxyl + Mancozeb) urgently.",
                "Do NOT harvest infected tubers — they will rot in storage.",
                "Treat remaining healthy plants preventatively every 5-7 days."
            ]
        },
        "ar": {
            "description": "اللفحة المتأخرة على البطاطس هي أشد الأمراض تدميراً — سببها نفس الممرض الذي أحدث المجاعة الأيرلندية.",
            "steps": [
                "تصرف فوراً — هذا المرض يمكن أن يدمر حقلاً بأكمله في أيام.",
                "أزل جميع النباتات المصابة وأحرقها.",
                "رش مبيداً فطرياً جهازياً (ميتالاكسيل + مانكوزيب) بشكل عاجل.",
                "لا تحصد الدرنات المصابة — ستتعفن أثناء التخزين.",
                "عالج النباتات السليمة المتبقية وقائياً كل 5-7 أيام."
            ]
        },
        "severity": "Critical",
        "spread_risk": "Very High",
        "color": "darkred"
    }
}


def get_treatment(disease_name, language="en"):
    """
    Returns treatment info for a given disease.
    language: 'en' for English, 'ar' for Arabic
    """
    if disease_name not in TREATMENTS:
        return None
    t = TREATMENTS[disease_name]
    return {
        "disease"     : disease_name,
        "description" : t[language]["description"],
        "steps"       : t[language]["steps"],
        "severity"    : t["severity"],
        "spread_risk" : t["spread_risk"],
        "color"       : t["color"]
    }
