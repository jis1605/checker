import streamlit as st
from elasticsearch import Elasticsearch
import streamlit.components.v1 as components
import pandas as pd
import datetime
import settings
import math


# Google Analytics 스크립트
ga_tracking_code = """
<script async src="https://www.googletagmanager.com/gtag/js?id=G-78L3J2XG0X"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'G-78L3J2XG0X');
</script>
"""


# Streamlit에 Google Analytics 코드 삽입
components.html("""
<iframe width="560" height="315" src="https://www.youtube.com/embed/dQw4w9WgXcQ" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
""", height=315)

# 이벤트 추적을 위한 JavaScript
def track_button_click():
    components.html("""
    <script>
        gtag('event', 'button_click', {
            'event_category': 'button',
            'event_label': 'example_button',
            'value': 1
        });
    </script>
    """, height=0)
# Streamlit 버튼
if st.button("Click Me"):
    track_button_click()
    st.write("Button clicked! The event is being tracked by Google Analytics.")

def fetch_bunsyo_data(env: str, index_name: str, query: dict, sort: list, page: int, size: int):
    """
    Elasticsearch에서 지정된 쿼리 및 페이지 정보를 기반으로 데이터를 가져옵니다.

    Args:
        env (str): 환경 이름 (예: 'dev', 'stg', 'prod').
        index_name (str): Elasticsearch 인덱스 이름.
        query (dict): 검색 쿼리.
        sort (list): 정렬 기준 리스트.
        page (int): 요청할 페이지 번호.
        size (int): 한 페이지의 데이터 수.

    Returns:
        dict: 검색 결과와 총 데이터 수를 포함한 딕셔너리.
    """
    if env not in ["dev", "stg", "prod"]:
        raise ValueError("환경 파라미터가 잘못되었습니다.")
    # 환경 설정 로직
    elif env == 'dev':
        if settings.DEV_ELASTIC_ENDPOINT is None or settings.DEV_ELASTIC_USER_ID is None or settings.DEV_ELASTIC_PASSWORD is None:
            raise ValueError("환경 변수 설정이 누락되었습니다.")
        ELASTIC_ENDPOINT = settings.DEV_ELASTIC_ENDPOINT
        ELASTIC_USER_ID = settings.DEV_ELASTIC_USER_ID
        ELASTIC_PASSWORD = settings.DEV_ELASTIC_PASSWORD
    elif env in ['stg', 'prod']:
        if settings.PROD_ELASTIC_ENDPOINT is None or settings.PROD_ELASTIC_USER_ID is None or settings.PROD_ELASTIC_PASSWORD is None:
            raise ValueError("환경 변수 설정이 누락되었습니다.")
        ELASTIC_ENDPOINT = settings.PROD_ELASTIC_ENDPOINT
        ELASTIC_USER_ID = settings.PROD_ELASTIC_USER_ID
        ELASTIC_PASSWORD = settings.PROD_ELASTIC_PASSWORD

    # Elasticsearch 연결
    es = Elasticsearch([ELASTIC_ENDPOINT], basic_auth=(ELASTIC_USER_ID, ELASTIC_PASSWORD), request_timeout=30)

    # 초기 검색
    response = es.search(
        index=index_name,
        body={
            "query": query,
            "sort": sort,
            "size": size,
        },
        scroll="3m"
    )

    scroll_id = response["_scroll_id"]
    hits = response["hits"]["hits"]

    # 필요한 페이지로 이동
    for _ in range(page - 1):
        response = es.scroll(scroll_id=scroll_id, scroll="3m")
        scroll_id = response["_scroll_id"]
        hits = response["hits"]["hits"]

    total = response["hits"]["total"]["value"]
    return {"hits": hits, "total": total}


def fetch_filtered_data_count(env: str, index_name: str, query: dict):
    """
    지정된 쿼리 조건에 일치하는 총 데이터 수를 반환합니다.

    Args:
        env (str): 환경 이름 (예: 'dev', 'stg', 'prod').
        index_name (str): Elasticsearch 인덱스 이름.
        query (dict): 검색 쿼리.

    Returns:
        int: 필터링된 데이터의 총 개수.
    """
    if env not in ["dev", "stg", "prod"]:
        raise ValueError("환경 파라미터가 잘못되었습니다.")

    # 환경별 설정
    if env == 'dev':
        ELASTIC_ENDPOINT = settings.DEV_ELASTIC_ENDPOINT
        ELASTIC_USER_ID = settings.DEV_ELASTIC_USER_ID
        ELASTIC_PASSWORD = settings.DEV_ELASTIC_PASSWORD
    elif env in ['stg', 'prod']:
        ELASTIC_ENDPOINT = settings.PROD_ELASTIC_ENDPOINT
        ELASTIC_USER_ID = settings.PROD_ELASTIC_USER_ID
        ELASTIC_PASSWORD = settings.PROD_ELASTIC_PASSWORD

    # Elasticsearch 연결
    es = Elasticsearch([ELASTIC_ENDPOINT], basic_auth=(ELASTIC_USER_ID, ELASTIC_PASSWORD), request_timeout=30)

    # 데이터 개수 조회
    response = es.count(index=index_name, body={"query": query})
    return response["count"]


def reformat_hits(es_response, fields: list):
    """
    Elasticsearch 검색 결과를 지정된 필드 형식으로 재구성합니다.

    Args:
        es_response (dict): Elasticsearch 검색 결과.
        fields (list): 포함할 필드 이름 목록.

    Returns:
        list: 재구성된 검색 결과 리스트.
    """
    output_data = []
    for item in es_response["hits"]:
        new_item = {"_id": item["_id"]} if "_id" in fields else {}
        for field in fields:
            if field in item["_source"]:
                new_item[field] = item["_source"][field]
        output_data.append(new_item)
    return output_data


def fetch_aggregations(env: str, index_name: str, query: dict, aggs: dict):
    """
    Elasticsearch에서 집계 결과를 가져옵니다.

    Args:
        env (str): 환경 이름 (예: 'dev', 'stg', 'prod').
        index_name (str): Elasticsearch 인덱스 이름.
        query (dict): 검색 쿼리.
        aggs (dict): 집계 설정.

    Returns:
        dict: Elasticsearch 집계 결과.
    """
    if env == 'dev':
        ELASTIC_ENDPOINT = settings.DEV_ELASTIC_ENDPOINT
        ELASTIC_USER_ID = settings.DEV_ELASTIC_USER_ID
        ELASTIC_PASSWORD = settings.DEV_ELASTIC_PASSWORD
    elif env in ['stg', 'prod']:
        ELASTIC_ENDPOINT = settings.PROD_ELASTIC_ENDPOINT
        ELASTIC_USER_ID = settings.PROD_ELASTIC_USER_ID
        ELASTIC_PASSWORD = settings.PROD_ELASTIC_PASSWORD

    # Elasticsearch 연결
    es = Elasticsearch([ELASTIC_ENDPOINT], basic_auth=(ELASTIC_USER_ID, ELASTIC_PASSWORD), request_timeout=30)

    # 집계 요청
    response = es.search(
        index=index_name,
        body={
            "query": query,
            "aggs": aggs
        },
        size=0
    )
    return response


def reformat_aggs(es_response):
    """
    Elasticsearch 집계 결과를 재구성합니다.

    Args:
        es_response (dict): Elasticsearch 집계 결과.

    Returns:
        list: 재구성된 집계 결과 리스트.
    """
    output_data = []
    for item in es_response["aggregations"]["aggregated_by_code"]["buckets"]:
        output_data.append({
            "code": item["key"]["code"],
            "count": item["doc_count"]
        })
    return output_data


def download_all_data(env, index_name, query, sort, fields):
    """
    지정된 조건에 맞는 모든 데이터를 다운로드하여 DataFrame으로 반환합니다.

    Args:
        env (str): 환경 이름 (예: 'dev', 'stg', 'prod').
        index_name (str): Elasticsearch 인덱스 이름.
        query (dict): 검색 쿼리.
        sort (list): 정렬 조건.
        fields (list): 포함할 필드 이름 목록.

    Returns:
        pandas.DataFrame: 검색된 데이터를 포함하는 DataFrame.
    """
    PAGE_SIZE = 10000
    all_hits = []
    current_page = 1
    
    while True:
        response = fetch_bunsyo_data(env, index_name, query, sort, current_page, PAGE_SIZE)
        hits = reformat_hits(response, fields)
        all_hits.extend(hits)
        
        if len(hits) < PAGE_SIZE:
            break
        current_page += 1

    return pd.DataFrame(all_hits)

st.title('G-Finder登録文書チェッカー')
st.header('登録文書検索', divider=True)

aggs = {
    "aggregated_by_code": {
        "composite": {
            "size": 1000,
            "sources": [
                {"code": {"terms": { "field": "code" }}},
            ],
        }
    }
}

query = {
    "bool": {
        "must": []
    }
}
sort = [
    {"created_at": {"order": "desc", "format": "strict_date_optional_time_nanos"}},
    {"file_id": {"order": "desc"}}
]

fields = []

env_option = st.selectbox(
    '環境を選択してください',
    [
        "dev",
        "stg",
        "prod",
    ],
    index=2,
)

category_option = st.selectbox(
    '文書カテゴリを選択してください',
    [
        "計画・方針",
        "予算・決算",
        "広報",
        "委員会議事録",
        "その他",
    ],
    index=3,
)
INDICES = {
    "計画・方針": "bunsyo_local_keikakuhoshin_v0.0.1",
    "予算・決算": "bunsyo_local_yosankessan_v0.0.1",
    "広報": "bunsyo_local_kouhou_v0.0.1",
    "委員会議事録": "bunsyo_local_iinkaigijiroku_v0.0.1",
    "その他": "bunsyo_local_sonota_v0.0.1",
}

FIELDS_OPTIONS = [
    "_id",
    "title",
    "category",
    "file_id",
    "file_page",
    "number_of_pages",
    "code",
    "affiliation_code",
    "organization_code",
    "content_text",
    "fiscal_year_start",
    "fiscal_year_end",
    "source_url",
    "source_url_is_alive",
    "tags",
    "published",
    "created_at",
    "updated_at",
    "collected_at",
    "hash"
]
fields_option = st.multiselect(
    '表示する項目を選択してください',
    FIELDS_OPTIONS,
    default=[
        "_id",
        "title",
        "file_id",
        "number_of_pages",
        "code",
        "source_url",
        "created_at",
    ]
)
if fields_option:
    fields = fields_option

only_first_page_option = st.checkbox('資料１ページ目のみを表示する')
if only_first_page_option:
    query["bool"]["must"].append({"term": {"file_page": 1}})

file_id_option = st.text_input('絞り込みたいFile IDを入力してください', None)
if file_id_option:
    query["bool"]["must"].append({"term": {"file_id": file_id_option}})

# 追加
search_text_option = st.text_input('検索語を入力してください (title または content_text)', None)
if search_text_option:
     # Google Analytics 이벤트 전송
    components.html(f"""
    <script>
        gtag('event', 'search_query', {{
            'event_category': 'search',
            'event_label': '{search_text_option}',
            'value': 1
        }});
    </script>
    """, height=0)
    query["bool"]["must"].append({
        "multi_match": {
            "query": search_text_option,
            "fields": ["title", "content_text"],
            "type": "phrase",
            "operator": "and"
        }
    })

code_option = st.text_input('自治体コードを一つ入力してください', None)
if code_option:
    query["bool"]["must"].append({"term": {"code": code_option}})

today = datetime.date.today()
less_than_date_option = st.date_input('選択日以前に登録されたデータのみに絞り込みます', today)
if less_than_date_option:
    query["bool"]["must"].append({"range": {"created_at": {"lte": less_than_date_option}}})

greater_than_date_option = st.date_input('選択日以降に登録されたデータのみに絞り込みます', None)
if greater_than_date_option:
    query["bool"]["must"].append({"range": {"created_at": {"gte": greater_than_date_option}}})

st.header('検索結果・集計結果', divider=True)

PAGE_SIZE = 10000


if "last_category" not in st.session_state or st.session_state["last_category"] != category_option:
    st.session_state["last_category"] = category_option
    st.session_state["last_query"] = None
    st.session_state["total_count"] = None
    st.session_state["current_page"] = 1

if "last_env" not in st.session_state or st.session_state["last_env"] != env_option:
    st.session_state["last_env"] = env_option
    st.session_state["last_query"] = None
    st.session_state["total_count"] = None
    st.session_state["current_page"] = 1

if "last_query" not in st.session_state or st.session_state["last_query"] != query:
    filtered_count = fetch_filtered_data_count(env_option, INDICES[category_option], query)
    st.session_state["total_count"] = filtered_count
    st.session_state["last_query"] = query
    st.session_state["current_page"] = 1

total_count = st.session_state["total_count"]
current_page = st.session_state["current_page"]
total_pages = math.ceil(total_count / PAGE_SIZE)

# st.write(f"総データ数: {total_count}")
st.write(f"全 {total_pages} ページ中のページ {current_page} を表示しています。")

if current_page > total_pages:
    current_page = total_pages
response = fetch_bunsyo_data(env_option, INDICES[category_option], query, sort, current_page, PAGE_SIZE)
df = pd.DataFrame(reformat_hits(response, fields))
st.write(df)

BUTTON_RANGE = 5
start_page = max(1, current_page - BUTTON_RANGE // 2)
end_page = min(total_pages, start_page + BUTTON_RANGE - 1)

if end_page - start_page + 1 < BUTTON_RANGE:
    start_page = max(1, end_page - BUTTON_RANGE + 1)

pagination_buttons = st.columns(end_page - start_page + 3)

with pagination_buttons[0]:
    if st.button("前のページ", disabled=current_page == 1):
        # Google Analytics 이벤트 전송
        components.html("""
        <script>
            gtag('event', 'page_navigation', {
                'event_category': 'pagination',
                'event_label': 'previous_page',
                'value': 1
            });
        </script>
        """, height=0)
        st.session_state["current_page"] = max(1, current_page - 1)
        st.experimental_rerun()

for idx, page in enumerate(range(start_page, end_page + 1), start=1):
    with pagination_buttons[idx]:
        if st.button(str(page), disabled=page == current_page):
            # Google Analytics 이벤트 전송
            components.html(f"""
            <script>
                gtag('event', 'page_navigation', {{
                    'event_category': 'pagination',
                    'event_label': 'page_{page}',
                    'value': {page}
                }});
            </script>
            """, height=0)
            st.session_state["current_page"] = page
            st.experimental_rerun()

with pagination_buttons[-1]:
    if st.button("次のページ", disabled=current_page == total_pages):
        # Google Analytics 이벤트 전송
        components.html("""
        <script>
            gtag('event', 'page_navigation', {
                'event_category': 'pagination',
                'event_label': 'next_page',
                'value': 1
            });
        </script>
        """, height=0)
        st.session_state["current_page"] = min(total_pages, current_page + 1)
        st.experimental_rerun()

aggregations_response = fetch_aggregations(env_option, INDICES[category_option], query, aggs)
st.write(pd.DataFrame(reformat_aggs(aggregations_response)))

