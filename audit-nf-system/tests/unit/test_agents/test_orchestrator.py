import pytest

@pytest.mark.asyncio
async def test_orchestrator_triggers_agents(mocker, mock_llm):
    from backend.agents.orchestrator import Orchestrator
    mock_agent = mocker.Mock()
    mock_agent.run.return_value = {"status": "done"}
    orch = Orchestrator(agents=[mock_agent])
    res = await orch.run_all({"input": "x"})
    assert isinstance(res, list)
    assert res[0]["status"] == "done"
