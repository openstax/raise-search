from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="RAISE Search API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/v1/search")
def search_v1(
    q: str = Query(..., title="Query string", description="The search query"),
    version: str = Query(..., title="Version", description="API version"),
    filter: str = Query(None, title="Filter",
                        description="Filter by 'student' or 'teacher'"),
):
    teacher_only = False
    if filter and filter == "teacher":
        teacher_only = True

    search_api_query = {
        "highlight": {
            "fields": {
                "visible_content": {},
                "lesson_page": {},
                "activity_name": {},
            },
            "pre_tags": ["<strong>"],
            "post_tags": ["</strong>"],
        },
        "query": {},
        "size": 100
    }

    if filter is None:
        search_api_query["query"] = {
            "simple_query_string": {
                "query": q,
                "fields": ["visible_content", "lesson_page", "activity_name"],
                "default_operator": "AND"
            }
        }
    else:
        search_api_query["query"] = {
            "bool": {
                "filter": {
                    "term": {"teacher_only": teacher_only}
                },
                "must": {
                    "simple_query_string": {
                        "query": q,
                        "fields": ["visible_content", "lesson_page", "activity_name"],
                        "default_operator": "AND"
                    }
                }
            }
        }

    return search_api_query
