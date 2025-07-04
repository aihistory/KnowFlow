from peewee import *
from .base_service import BaseService
from .models import Document
from .utils import get_uuid, StatusEnum

class DocumentService(BaseService):
    model = Document
    
    @classmethod
    def create_document(cls, kb_id: str, name: str, location: str, size: int, file_type: str, created_by: str = None, parser_id: str = None, parser_config: dict = None) -> Document:
        """
        创建文档记录
        
        Args:
            kb_id: 知识库ID
            name: 文件名
            location: 存储位置
            size: 文件大小
            file_type: 文件类型
            created_by: 创建者ID
            parser_id: 解析器ID
            parser_config: 解析器配置
            
        Returns:
            Document: 创建的文档对象
        """
        doc_id = get_uuid()
        
        # 构建默认的解析器配置，包含分块配置
        default_parser_config = {
            "pages": [[1, 1000000]],
            "chunking_config": {
                "strategy": "smart",
                "chunk_token_num": 256,
                "min_chunk_tokens": 10
            }
        }
        
        # 如果提供了自定义配置，则合并
        if parser_config:
            if isinstance(parser_config, dict):
                default_parser_config.update(parser_config)
            else:
                # 如果是字符串，尝试解析
                try:
                    import json
                    custom_config = json.loads(parser_config) if isinstance(parser_config, str) else parser_config
                    default_parser_config.update(custom_config)
                except (json.JSONDecodeError, TypeError):
                    # 解析失败，使用默认配置
                    pass
        
        # 确保分块配置存在
        if 'chunking_config' not in default_parser_config:
            default_parser_config['chunking_config'] = {
                "strategy": "smart",
                "chunk_token_num": 256,
                "min_chunk_tokens": 10
            }
        
        # 构建基本文档数据
        doc_data = {
            'id': doc_id,
            'kb_id': kb_id,
            'name': name,
            'location': location,
            'size': size,
            'type': file_type,
            'created_by': created_by or 'system',
            'parser_id': parser_id or '',
            'parser_config': default_parser_config,
            'source_type': 'local',
            'token_num': 0,
            'chunk_num': 0,
            'progress': 0,
            'progress_msg': '',
            'run': '0',  # 未开始解析
            'status': StatusEnum.VALID.value
        }
        
        return cls.insert(doc_data)
    
    @classmethod
    def get_by_kb_id(cls, kb_id: str) -> list[Document]:
        return cls.query(kb_id=kb_id)
    
    @classmethod
    def update(cls, doc_id: str, data: dict) -> int:
        """
        更新文档记录
        
        Args:
            doc_id: 文档ID
            data: 要更新的数据字典
            
        Returns:
            int: 受影响的行数
        """
        return cls.model.update(**data).where(cls.model.id == doc_id).execute()