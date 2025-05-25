"""Simple dictionaryu2011based localisation."""

def _(key: str, lang: str) -> str:
    _map = {
        "upload": {"FR": "Téléverser le modèle", "AR": "رفع القالب"},
        "upload_prompt": {"FR": "Téléversez le fichier .xlsx du modèle.", "AR": "يرجى رفع ملف .xlsx للقالب."},
        "time_limit": {"FR": "Limite de temps (s)", "AR": "حد الزمن (ثانية)"},
        "file_loaded": {"FR": "Fichier chargé", "AR": "تم تحميل الملف"},
        "generate": {"FR": "Générer le planning", "AR": "إنشاء الجدول"},
        "download": {"FR": "Télécharger le planning", "AR": "تحميل الجدول"},
        "teachers": {"FR": "enseignants", "AR": "أساتذة"},
        "rooms": {"FR": "salles", "AR": "قاعات"},
        "sessions": {"FR": "séances", "AR": "حصص"},
        "log": {"FR": "Journal", "AR": "السجل"},
    }
    return _map.get(key, {}).get(lang, key)