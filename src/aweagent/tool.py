import requests
import os
import csv
import datetime
import json
from pydantic import BaseModel, Field
from typing import Literal, List, Optional
from .db import Paper, get_database_session


def search_papers(
    query: str,
    publication_types: Optional[List[Literal[
        "Review", "JournalArticle", "CaseReport", "ClinicalTrial", "Conference", "Dataset", "Editorial", "LettersAndComments", "MetaAnalysis", "News", "Study", "Book", "BookSection"
    ]]] = ["Review", "JournalArticle"],
    open_access_pdf: bool | None = None,
    venue: list | None = None,
    fields_of_study: Optional[List[Literal[
        "Computer Science", "Medicine", "Chemistry", "Biology", "Materials Science", "Physics", "Geology", "Psychology", "Art", "History", "Geography", "Sociology", "Business", "Political Science", "Economics", "Philosophy", "Mathematics", "Engineering", "Environmental Science", "Agricultural and Food Sciences", "Education", "Law", "Linguistics"
    ]]] = None,
    fields: Optional[List[Literal[
        "paperId", "corpusId", "externalIds", "url", "title", "abstract", "venue", "publicationVenue", "year", "referenceCount", "citationCount", "influentialCitationCount", "isOpenAccess", "openAccessPdf", "fieldsOfStudy", "s2FieldsOfStudy", "publicationTypes", "publicationDate", "journal", "citationStyles", "authors", "citations", "references", "embedding", "tldr"
    ]]] = None,
    publication_date_or_year: str | None = None,
    min_citation_count: int | None = None,
    limit: int = 100,
    bulk: bool = False,
    sort: str | None = None,
    match_title: bool = False
):
    """
    Search for papers from the Semantic Scholar according to the query keyword.

    Args:
        query (str): Plain-text search query string.
        publication_types (list of Literal, optional): Restrict results to the given publication type list. 可选值：
            - Review
            - JournalArticle
            - CaseReport
            - ClinicalTrial
            - Conference
            - Dataset
            - Editorial
            - LettersAndComments
            - MetaAnalysis
            - News
            - Study
            - Book
            - BookSection
        open_access_pdf (bool, optional): Restrict results to papers with public PDFs.
        venue (list, optional): Restrict results to the given venue list.
        fields_of_study (list of Literal, optional): Restrict results to given field-of-study list. 可选值：
            - Computer Science
            - Medicine
            - Chemistry
            - Biology
            - Materials Science
            - Physics
            - Geology
            - Psychology
            - Art
            - History
            - Geography
            - Sociology
            - Business
            - Political Science
            - Economics
            - Philosophy
            - Mathematics
            - Engineering
            - Environmental Science
            - Agricultural and Food Sciences
            - Education
            - Law
            - Linguistics
        fields (list, optional): List of the fields to be returned.
        publication_date_or_year (str, optional): Restrict results to the given range of publication date in the format <start_date>:<end_date>, where dates are in the format YYYY-MM-DD, YYYY-MM, or YYYY.
        min_citation_count (int, optional): Restrict results to papers with at least the given number of citations.
        limit (int, optional): Maximum number of results to return (must be <= 100).
        bulk (bool, optional): Bulk retrieval of basic paper data without search relevance (ignores the limit parameter if True and returns up to 1,000 results in each page).
        sort (str, optional): Sorts results (only if bulk=True) using <field>:<order> format, where "field" is either paperId, publicationDate, or citationCount, and "order" is asc (ascending) or desc (descending).
        match_title (bool, optional): Retrieve a single paper whose title best matches the given query.

    Returns:
        list: Query results.
    """
    from semanticscholar import SemanticScholar

    # You'll need an instance of the client to request d
    # ata from the API
    sch = SemanticScholar(api_key=os.getenv("SEMANTICSCHOLAR_API_KEY"))
    papers = sch.search_paper(
        query, 
        publication_types=publication_types, 
        open_access_pdf=open_access_pdf, 
        venue=venue, 
        fields_of_study=fields_of_study, 
        fields=fields, 
        publication_date_or_year=publication_date_or_year, 
        min_citation_count=min_citation_count, 
        limit=limit, 
        bulk=bulk, 
        sort=sort, 
        match_title=match_title)
    papers = [paper for paper in papers.items if paper.authors is not None and paper.authors[-1].authorId is not None]
    if len(papers) == 0:
        return "No papers found"
    author_ids = [paper.authors[-1].authorId for paper in papers]
    authors = sch.get_authors(author_ids=author_ids, fields=["name", "affiliations"])
    author_to_paper = {author["authorId"]: author for author in authors}
    paper_ls = []
    session = get_database_session()
    for idx, paper in enumerate(papers):
        if paper.externalIds is None:
            continue
        if paper.externalIds.get("DOI", None) is None:
            continue
        if paper.authors is None:
            continue
        if paper.authors[-1].authorId is None:
            authors = paper.authors[-1].name
        else:
            authors = author_to_paper[paper.authors[-1].authorId]
        existing = session.query(Paper).filter_by(doi=paper.externalIds.get("DOI")).first()
        if not existing:
            db_paper = Paper(
                paper_id=getattr(paper, 'paperId', None),
                title=getattr(paper, 'title', None),
                authors= str(authors),
                year=getattr(paper, 'year', None),
                venue=getattr(paper, 'venue', None),
                url=getattr(paper, 'url', None),
                publication_types=",".join(paper.publicationTypes) if paper.publicationTypes else None,
                journal=paper.journal.name if paper.journal else None,
                doi=paper.externalIds.get("DOI", None) if paper.externalIds else None,
                abstract=getattr(paper, 'abstract', None),
                citationCount=getattr(paper, 'citationCount', None),
                citationStyles=str(getattr(paper, 'citationStyles', None)),
                citations=str(getattr(paper, 'citations', None)),
                corpusId=getattr(paper, 'corpusId', None),
                fieldsOfStudy=",".join(paper.fieldsOfStudy) if paper.fieldsOfStudy else None,
                influentialCitationCount=getattr(paper, 'influentialCitationCount', None),
                isOpenAccess=getattr(paper, 'isOpenAccess', None),
                openAccessPdf=str(getattr(paper, 'openAccessPdf', None)),
                publicationDate=getattr(paper, 'publicationDate', None),
                referenceCount=getattr(paper, 'referenceCount', None),
            )
            session.add(db_paper)
        paper_ls.append(f"""
                <paper>
                    <doi>{paper.externalIds.get("DOI")}</doi>
                    <title> {paper.title}</title>
                    <journal> {paper.journal.name if paper.journal else None}</journal>
                </paper>
            """)
    session.commit()
    return "\n".join(paper_ls)
