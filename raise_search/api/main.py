from fastapi import FastAPI, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from raise_search.api import utils
import enum
from raise_search.api.models import SearchResults

app = FastAPI(title="RAISE Search API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class FilterOptions(str, enum.Enum):
    TEACHER = 'teacher'
    STUDENT = 'student'


@app.get("/v1/search")
def search_v1(
    q: str = Query(..., title="Query string", description="The search query"),
    version: str = Query(..., title="Version", description="Content version"),
    filter: FilterOptions = Query(
        None, title="Filter", description="Filter by 'student' or 'teacher'"
    ),
    client=Depends(utils.get_opensearch_client),
) -> SearchResults :
    teacher_only = False
    if filter == FilterOptions.TEACHER.value:
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
        "size": 100,
    }

    if filter is None:
        search_api_query["query"] = {
            "simple_query_string": {
                "query": q,
                "fields": ["visible_content", "lesson_page", "activity_name"],
                "default_operator": "AND",
            }
        }
    else:
        search_api_query["query"] = {
            "bool": {
                "filter": {"term": {"teacher_only": teacher_only}},
                "must": {
                    "simple_query_string": {
                        "query": q,
                        "fields": ["visible_content", "lesson_page", "activity_name"],
                        "default_operator": "AND",
                    }
                },
            }
        }

    search_results = client.search(index="test-index2", body=search_api_query)
    for hit in search_results["hits"]["hits"]:
        del hit["_source"]["visible_content"]

    return search_results
