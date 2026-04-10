# [INPUT]: 聚合 graph 子模块的公共接口
# [OUTPUT]: 对外提供 init_db, get_connection, store (模块), DocumentIndexer, EmbeddingStore
# [POS]: graph 包入口
# [PROTOCOL]: 变更时更新此头部，然后检查 AGENTS.md

from . import store
from .store import get_connection, init_db
from .indexer import DocumentIndexer

__all__ = ["get_connection", "init_db", "store", "DocumentIndexer", "EmbeddingStore"]


def __getattr__(name: str):
    """EmbeddingStore 延迟导入，避免启动时拉 chromadb+torch。"""
    if name == "EmbeddingStore":
        from .embeddings import EmbeddingStore
        return EmbeddingStore
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
