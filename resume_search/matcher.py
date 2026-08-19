"""Вакансия -> фильтры поиска резюме («Найти человека»)."""
from storage.models import Vacancy


def build_query(vacancy: Vacancy) -> dict:
    """Собрать поисковый запрос из данных вакансии."""
    title = vacancy.title.split("(")[0].strip()  # убираем уточнение в скобках
    skills = [s.strip() for s in (vacancy.skills or "").split(",") if s.strip()]
    return {
        "title": title,
        "city": vacancy.city,
        "salary_from": vacancy.salary_from,
        "skills": skills,
        "experience": vacancy.experience,
    }

