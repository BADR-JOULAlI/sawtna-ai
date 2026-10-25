"""Server-side assessment bank with source references."""
QUESTIONS = [
    {
        "id": "vote", "article": "Article 30",
        "fr": ["Quel principe la Constitution associe-t-elle au vote ?", ["Un droit personnel et un devoir national", "Une obligation de soutenir un parti", "Un mandat transmissible"]],
        "ar": ["كيف يصف الدستور التصويت؟", ["حق شخصي وواجب وطني", "واجب دعم حزب معين", "تفويض قابل للنقل"]],
        "darija": ["Kifach kaywsef الدستور التصويت؟", ["7e9 chakhsi w wajib watani", "Khassek tsaned chi 7izb", "T9der t3ti sotek l chi wa7ed"]],
        "answer": 0,
    },
    {
        "id": "chambers", "article": "Article 60",
        "fr": ["De combien de Chambres le Parlement est-il composé ?", ["Une", "Deux", "Trois"]],
        "ar": ["من كم مجلس يتكون البرلمان؟", ["مجلس واحد", "مجلسين", "ثلاثة مجالس"]],
        "darija": ["Ch7al men majlis kayn f lbarlaman?", ["Wa7ed", "Jouj", "Tlata"]],
        "answer": 1,
    },
    {
        "id": "mandate", "article": "Article 62",
        "fr": ["Quelle durée est prévue pour l'élection des représentants dans le texte de 2011 ?", ["Trois ans", "Six ans", "Cinq ans"]],
        "ar": ["ما مدة انتخاب أعضاء مجلس النواب حسب نص 2011؟", ["ثلاث سنوات", "ست سنوات", "خمس سنوات"]],
        "darija": ["Ch7al katdoum mandat dyal nowab f nass 2011?", ["3 snin", "6 snin", "5 snin"]],
        "answer": 2,
    },
    {
        "id": "territories", "article": "Article 135",
        "fr": ["Quel élément est une collectivité territoriale ?", ["Une commune", "Un parti politique", "Une commission parlementaire"]],
        "ar": ["أي عنصر يعتبر جماعة ترابية؟", ["الجماعة", "حزب سياسي", "لجنة برلمانية"]],
        "darija": ["Chkon men hadou jama3a torabiya?", ["Jama3a", "7izb siyasi", "Lajna barlamaniya"]],
        "answer": 0,
    },
]


def public_quiz(language):
    return {"id": "constitution-basics-v1", "title": {"fr": "Les fondamentaux du vote", "ar": "أساسيات التصويت", "darija": "L'asasiyat dyal tswit"}[language],
        "questions": [{"id": q["id"], "question": q[language][0], "options": q[language][1]} for q in QUESTIONS]}


def grade(answers, language):
    corrections = []
    for item in QUESTIONS:
        corrections.append({"id": item["id"], "correct": answers.get(item["id"]) == item["answer"], "answer": item["answer"], "explanation": item[language][1][item["answer"]], "source": item["article"], "source_url": "https://maroc.ma/sites/default/files/2024-10/constitution_du_1er_juillet_2011.pdf"})
    correct = sum(c["correct"] for c in corrections)
    return {"correct": correct, "total": len(QUESTIONS), "score": round(100 * correct / len(QUESTIONS)), "corrections": corrections}
