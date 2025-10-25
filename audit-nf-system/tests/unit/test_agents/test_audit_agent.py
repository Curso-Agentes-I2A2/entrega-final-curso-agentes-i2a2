import pytest

@pytest.mark.asyncio
async def test_audit_valid_invoice(mock_rag_client, mock_llm, valid_invoice_data):
    from backend.agents.audit_agent import AuditAgent
    agent = AuditAgent(rag_client=mock_rag_client, llm=mock_llm)
    result = await agent.audit(valid_invoice_data)
    assert isinstance(result, dict)
    assert "aprovada" in result or "status" in result

@pytest.mark.asyncio
async def test_audit_invalid_invoice(mock_rag_client, mock_llm, invalid_invoice_data):
    from backend.agents.audit_agent import AuditAgent
    agent = AuditAgent(rag_client=mock_rag_client, llm=mock_llm)
    result = await agent.audit(invalid_invoice_data)
    assert isinstance(result, dict)
    assert "irregularidades" in result or "aprovada" in result

@pytest.mark.asyncio
async def test_agent_with_rag_called(mocker, mock_rag_client, mock_llm, valid_invoice_data):
    from backend.agents.audit_agent import AuditAgent
    spy = mocker.spy(mock_rag_client, "search")
    agent = AuditAgent(rag_client=mock_rag_client, llm=mock_llm)
    await agent.audit(valid_invoice_data)
    assert spy.called

@pytest.mark.asyncio
async def test_agent_with_mcp_tools(mocker, mock_llm, valid_invoice_data):
    from backend.agents.audit_agent import AuditAgent
    mcp_tools = mocker.Mock()
    agent = AuditAgent(rag_client=None, llm=mock_llm, mcp_tools=mcp_tools)
    res = await agent.audit(valid_invoice_data)
    # ensure agent used toolset (this is generic; adjust asserts to your implementation)
    assert hasattr(agent, "mcp_tools")

@pytest.mark.asyncio
async def test_agent_error_handling(mocker, valid_invoice_data):
    from backend.agents.audit_agent import AuditAgent
    bad_llm = mocker.Mock()
    bad_llm.generate.side_effect = Exception("LLM fail")
    agent = AuditAgent(rag_client=None, llm=bad_llm)
    res = await agent.audit(valid_invoice_data)
    # should return a dict even on error
    assert isinstance(res, dict)
