from flask import request, jsonify
from utils import success_response, error_response
from services.files.document_service import DocumentService
from .. import documents_bp
import json
import logging

# 设置日志记录
logger = logging.getLogger(__name__)

@documents_bp.route('/<doc_id>/chunking-config', methods=['GET'])
def get_document_chunking_config(doc_id):
    """获取文档分块配置"""
    try:
        logger.info(f"获取文档分块配置: doc_id={doc_id}")
        
        # 从数据库获取文档信息
        document = DocumentService.get_by_id(doc_id)
        if not document:
            logger.warning(f"文档不存在: doc_id={doc_id}")
            return error_response("文档不存在", code=404)
        
        logger.info(f"文档信息: name={document.name}, parser_config={document.parser_config}")
        
        # 解析parser_config中的chunking_config
        parser_config = {}
        if document.parser_config:
            try:
                if isinstance(document.parser_config, str):
                    parser_config = json.loads(document.parser_config)
                else:
                    parser_config = document.parser_config
            except json.JSONDecodeError as e:
                logger.error(f"JSON解析错误: doc_id={doc_id}, error={str(e)}, raw_config={document.parser_config}")
                # 使用默认配置
                parser_config = {}
        
        chunking_config = parser_config.get('chunking_config', {
            'strategy': 'smart',
            'chunk_token_num': 256,
            'min_chunk_tokens': 10
        })
        
        logger.info(f"返回分块配置: doc_id={doc_id}, config={chunking_config}")
        return success_response(data={'chunking_config': chunking_config})
        
    except Exception as e:
        logger.error(f"获取分块配置失败: doc_id={doc_id}, error={str(e)}", exc_info=True)
        return error_response(f"获取分块配置失败: {str(e)}", code=500)

@documents_bp.route('/<doc_id>/chunking-config', methods=['PUT'])
def update_document_chunking_config(doc_id):
    """更新文档分块配置"""
    try:
        logger.info(f"更新文档分块配置: doc_id={doc_id}")
        
        data = request.get_json()
        if not data or 'chunking_config' not in data:
            logger.warning(f"缺少分块配置数据: doc_id={doc_id}, data={data}")
            return error_response("缺少分块配置数据", code=400)
        
        chunking_config = data['chunking_config']
        logger.info(f"接收到的分块配置: doc_id={doc_id}, config={chunking_config}")
        
        # 验证分块配置
        required_fields = ['strategy', 'chunk_token_num', 'min_chunk_tokens']
        for field in required_fields:
            if field not in chunking_config:
                logger.warning(f"缺少必需字段: doc_id={doc_id}, field={field}")
                return error_response(f"缺少必需字段: {field}", code=400)
        
        # 验证策略类型
        valid_strategies = ['basic', 'smart', 'advanced', 'strict_regex']
        if chunking_config['strategy'] not in valid_strategies:
            logger.warning(f"无效的分块策略: doc_id={doc_id}, strategy={chunking_config['strategy']}")
            return error_response(f"无效的分块策略: {chunking_config['strategy']}", code=400)
        
        # 验证数值范围
        if not (50 <= chunking_config['chunk_token_num'] <= 2048):
            logger.warning(f"chunk_token_num超出范围: doc_id={doc_id}, value={chunking_config['chunk_token_num']}")
            return error_response("chunk_token_num必须在50-2048之间", code=400)
        
        if not (10 <= chunking_config['min_chunk_tokens'] <= 500):
            logger.warning(f"min_chunk_tokens超出范围: doc_id={doc_id}, value={chunking_config['min_chunk_tokens']}")
            return error_response("min_chunk_tokens必须在10-500之间", code=400)
        
        # 获取现有文档
        document = DocumentService.get_by_id(doc_id)
        if not document:
            logger.warning(f"文档不存在: doc_id={doc_id}")
            return error_response("文档不存在", code=404)
        
        # 更新parser_config中的chunking_config
        current_parser_config = {}
        if document.parser_config:
            try:
                if isinstance(document.parser_config, str):
                    current_parser_config = json.loads(document.parser_config)
                else:
                    current_parser_config = document.parser_config
            except json.JSONDecodeError as e:
                logger.error(f"JSON解析错误: doc_id={doc_id}, error={str(e)}, raw_config={document.parser_config}")
                # 使用默认配置
                current_parser_config = {"pages": [[1, 1000000]]}
        
        current_parser_config['chunking_config'] = chunking_config
        
        # 更新文档
        update_data = {
            'parser_config': json.dumps(current_parser_config)
        }
        
        logger.info(f"更新文档配置: doc_id={doc_id}, new_config={update_data}")
        
        result = DocumentService.update(doc_id, update_data)
        logger.info(f"更新结果: doc_id={doc_id}, affected_rows={result}")
        
        return success_response(data={'message': '分块配置更新成功'})
        
    except Exception as e:
        logger.error(f"更新分块配置失败: doc_id={doc_id}, error={str(e)}", exc_info=True)
        return error_response(f"更新分块配置失败: {str(e)}", code=500) 