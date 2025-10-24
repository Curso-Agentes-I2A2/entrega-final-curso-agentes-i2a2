import pytest
import numpy as np

@pytest.mark.asyncio
async def test_generate_embeddings(mocker):
    from backend.rag.embedding import EmbeddingService
    mock_api = mocker.Mock()
    mock_api.create.return_value = {"data": [[0.1, 0.2, 0.3]]}
    svc = EmbeddingService(api_client=mock_api)
    emb = await svc.generate("test")
    assert isinstance(emb, list)
    assert len(emb) > 0

@pytest.mark.asyncio
async def test_embeddings_consistency(mocker):
    from backend.rag.embedding import EmbeddingService
    mock_api = mocker.Mock()
    mock_api.create.side_effect = lambda text: {"data": [[float(abs(hash(text)) % 100)]]}
    svc = EmbeddingService(api_client=mock_api)
    a = await svc.generate("same text")
    b = await svc.generate("same text")
    assert a == b

@pytest.mark.asyncio
async def test_embeddings_cache(mocker):
    from backend.rag.embedding import EmbeddingService
    svc = EmbeddingService(api_client=None)
    # inject cache
    svc._cache = {}
    first = await svc.generate("cache test")
    second = await svc.generate("cache test")
    assert first == second

@pytest.mark.asyncio
async def test_fallback_to_local_model(mocker):
    from backend.rag.embedding import EmbeddingService
    mock_api = mocker.Mock()
    mock_api.create.side_effect = Exception("api down")
    svc = EmbeddingService(api_client=mock_api, local_model_enabled=True)
    emb = await svc.generate("texto")
    assert isinstance(emb, list)
