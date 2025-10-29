import pytest

@pytest.mark.asyncio
async def test_search_basic(mocker):
    from backend.rag.retrieval import RetrievalService
    mock_store = mocker.Mock()
    mock_store.search.return_value = [{"id": "1", "score": 0.9, "content": "doc"}]
    svc = RetrievalService(store=mock_store)
    res = await svc.search("query")
    assert len(res) == 1

@pytest.mark.asyncio
async def test_search_with_filters(mocker):
    from backend.rag.retrieval import RetrievalService
    mock_store = mocker.Mock()
    mock_store.search.return_value = [{"id": "1", "score": 0.9, "content": "doc", "type": "lei"}]
    svc = RetrievalService(store=mock_store)
    res = await svc.search("query", filters={"type": "lei"})
    assert all(r.get("type") == "lei" for r in res)

@pytest.mark.asyncio
async def test_search_threshold(mocker):
    from backend.rag.retrieval import RetrievalService
    mock_store = mocker.Mock()
    mock_store.search.return_value = [{"id": "1", "score": 0.4, "content": "doc"}]
    svc = RetrievalService(store=mock_store)
    res = await svc.search("query", min_score=0.5)
    assert res == []

@pytest.mark.asyncio
async def test_search_empty_results(mocker):
    from backend.rag.retrieval import RetrievalService
    mock_store = mocker.Mock()
    mock_store.search.return_value = []
    svc = RetrievalService(store=mock_store)
    res = await svc.search("notfound")
    assert res == []
