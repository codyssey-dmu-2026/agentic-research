"""Pick port implementations from settings. The only place that does so."""

from .config import Settings
from .embeddings import HashEmbedding, OpenAIEmbedding
from .llm import OpenAILLM, RuleBasedLLM
from .news import CsvNewsSource
from .ports import EmbeddingPort, LLMPort, NewsSource, VectorStorePort
from .risk.provider import StoredRiskTagProvider
from .vectorstore import ChromaVectorStore


class MissingAPIKeyError(RuntimeError):
    pass


def _api_key(settings: Settings, what: str):
    if settings.openai_api_key is None:
        raise MissingAPIKeyError(f"{what}=openai requires OPENAI_API_KEY in .env")
    return settings.openai_api_key


def build_embedding(settings: Settings) -> EmbeddingPort:
    if settings.embedding_provider == "openai":
        key = _api_key(settings, "AGENT_EMBEDDING_PROVIDER")
        return OpenAIEmbedding(settings.embedding_model, key)
    return HashEmbedding()


def build_llm(settings: Settings) -> LLMPort:
    if settings.llm_provider == "openai":
        key = _api_key(settings, "AGENT_LLM_PROVIDER")
        return OpenAILLM(settings.llm_model, key, settings.llm_timeout_s)
    return RuleBasedLLM()


def build_vector_store(settings: Settings) -> VectorStorePort:
    return ChromaVectorStore(settings.chroma_dir, build_embedding(settings))


def build_news_source(settings: Settings) -> NewsSource:
    return CsvNewsSource(settings.news_dir)


def build_risk_provider(settings: Settings) -> StoredRiskTagProvider:
    return StoredRiskTagProvider.from_jsonl(settings.risk_tags_path)
