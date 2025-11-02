# agents/utils/llm_factory.py
import logging
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.language_models.chat_models import BaseChatModel
from ..config import settings
from typing import List

logger = logging.getLogger(__name__)

def create_llm_with_fallback() -> BaseChatModel:
    """
    Cria a instância do LLM.
    Tenta carregar os LLMs em ordem de prioridade (Claude, OpenAI, Gemini)
    e constrói uma cadeia de fallbacks com os que estiverem disponíveis.
    """
    llm_candidates: List[BaseChatModel] = []
    
    # --- 1. Tentar Anthropic (Primário) ---
    if settings.api_keys.anthropic_api_key:
        try:
            llm_candidates.append(
                ChatAnthropic(
                    model=settings.llm.primary_model,
                    api_key=settings.api_keys.anthropic_api_key,
                    temperature=settings.llm.temperature,
                    max_tokens=settings.llm.max_tokens,
                    timeout=settings.llm.timeout,
                )
            )
            logger.info(f"LLM Primário (Claude) carregado: {settings.llm.primary_model}")
        except Exception as e:
            logger.warning(f"Falha ao carregar Anthropic (Claude): {e}")

    # --- 2. Tentar OpenAI (Secundário) ---
    if settings.api_keys.openai_api_key:
        try:
            llm_candidates.append(
                ChatOpenAI(
                    model=settings.llm.secondary_model,
                    api_key=settings.api_keys.openai_api_key,
                    temperature=settings.llm.temperature,
                    max_tokens=settings.llm.max_tokens,
                    timeout=settings.llm.timeout,
                )
            )
            logger.info(f"LLM Secundário (OpenAI) carregado: {settings.llm.secondary_model}")
        except Exception as e:
            logger.warning(f"Falha ao carregar OpenAI (GPT): {e}")

    # --- 3. Tentar Google Gemini (Terciário / Seu Fallback) ---
    if settings.api_keys.google_api_key:
        try:
            llm_candidates.append(
                ChatGoogleGenerativeAI(
                    model=settings.llm.tertiary_model,
                    google_api_key=settings.api_keys.google_api_key,
                    temperature=settings.llm.temperature,
                    max_tokens=settings.llm.max_tokens,
                    # O timeout é tratado de forma diferente no Gemini,
                    # mas o construtor aceita.
                )
            )
            logger.info(f"LLM Terciário (Gemini) carregado: {settings.llm.tertiary_model}")
        except Exception as e:
            logger.warning(f"Falha ao carregar Google (Gemini): {e}")

    # --- 4. Construir a Cadeia de Fallbacks ---
    if not llm_candidates:
        # Se nenhuma chave de API foi fornecida
        logger.error("Nenhuma chave de API de LLM foi fornecida. O agente não pode funcionar.")
        raise ValueError("Nenhuma chave de API de LLM configurada no .env (Anthropic, OpenAI ou Google).")

    # O primeiro LLM carregado com sucesso será o primário
    primary_llm = llm_candidates[0]
    
    # Todos os outros se tornam fallbacks
    fallbacks = llm_candidates[1:] 

    def get_model_name(llm):
        """Gets model name, handling different attribute names across versions"""
        if hasattr(llm, 'model_name'):
            return llm.model_name
        elif hasattr(llm, 'model'):
            return llm.model
        else:
            return type(llm).__name__

    if fallbacks:
        logger.info(f"LLM Primário: {get_model_name(primary_llm)}. Fallbacks: {[get_model_name(llm) for llm in fallbacks]}")
        return primary_llm.with_fallbacks(fallbacks)
    else:
        # Se apenas um LLM foi carregado (ex: só o Gemini)
        logger.info(f"LLM Único carregado: {get_model_name(primary_llm)}")
        return primary_llm