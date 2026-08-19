"""Поиск резюме по вакансии через адаптеры сайтов («Найти человека»)."""
from sqlalchemy.orm import Session

from adapters.registry import all_sites, get_adapter
from resume_search.matcher import build_query
from storage.models import Vacancy, ResumeMatch


async def search_for_vacancy(db: Session, vacancy: Vacancy) -> list[ResumeMatch]:
    """Найти резюме по всем сайтам, сохранить результаты в БД."""
    query = build_query(vacancy)
    matches: list[ResumeMatch] = []
    for site in all_sites(db):
        key = site["key"]
        adapter = get_adapter(key, db)
        if not adapter.supports_resume_search():
            continue
        try:
            results = await adapter.search_resumes(query)
        except Exception:  # noqa: BLE001
            continue
        for r in results:
            m = ResumeMatch(
                vacancy_id=vacancy.id,
                site=key,
                resume_url=r.resume_url,
                candidate_name=r.candidate_name,
                title=r.title,
                match_score=r.match_score,
            )
            db.add(m)
            matches.append(m)
    db.commit()
    return matches

