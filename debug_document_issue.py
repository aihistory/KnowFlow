#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档数据诊断脚本
用于检查和修复文档分块配置问题
"""

import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from server.services.files.document_service import DocumentService

def diagnose_document(doc_id):
    """诊断特定文档的数据问题"""
    print(f"🔍 诊断文档: {doc_id}")
    
    # 1. 检查文档是否存在
    document = DocumentService.get_by_id(doc_id)
    if not document:
        print(f"❌ 文档不存在: {doc_id}")
        return False
    
    print(f"✅ 文档存在: {document.name}")
    print(f"   ID: {document.id}")
    print(f"   知识库ID: {document.kb_id}")
    print(f"   类型: {document.type}")
    print(f"   状态: {document.status}")
    
    # 2. 检查 parser_config 字段
    print(f"\n📄 parser_config 检查:")
    print(f"   原始值: {document.parser_config}")
    print(f"   类型: {type(document.parser_config)}")
    
    if document.parser_config:
        try:
            if isinstance(document.parser_config, str):
                parsed_config = json.loads(document.parser_config)
                print(f"   ✅ JSON 解析成功")
                print(f"   解析后: {parsed_config}")
                
                # 检查 chunking_config
                if 'chunking_config' in parsed_config:
                    print(f"   ✅ 包含 chunking_config: {parsed_config['chunking_config']}")
                else:
                    print(f"   ⚠️  缺少 chunking_config，将使用默认配置")
                    
            else:
                print(f"   ✅ 已经是字典类型")
                
        except json.JSONDecodeError as e:
            print(f"   ❌ JSON 解析错误: {e}")
            print(f"   需要修复 parser_config 字段")
            return False
    else:
        print(f"   ⚠️  parser_config 为空")
        
    return True

def fix_document_config(doc_id):
    """修复文档配置问题"""
    print(f"\n🔧 修复文档配置: {doc_id}")
    
    document = DocumentService.get_by_id(doc_id)
    if not document:
        print(f"❌ 文档不存在: {doc_id}")
        return False
    
    # 默认配置
    default_config = {
        "pages": [[1, 1000000]],
        "chunking_config": {
            "strategy": "smart",
            "chunk_token_num": 256,
            "min_chunk_tokens": 10
        }
    }
    
    try:
        # 尝试解析现有配置
        current_config = default_config.copy()
        if document.parser_config:
            if isinstance(document.parser_config, str):
                try:
                    parsed = json.loads(document.parser_config)
                    current_config.update(parsed)
                except json.JSONDecodeError:
                    print(f"   ⚠️  JSON 解析失败，使用默认配置")
            else:
                current_config.update(document.parser_config)
        
        # 确保包含 chunking_config
        if 'chunking_config' not in current_config:
            current_config['chunking_config'] = default_config['chunking_config']
        
        # 更新文档
        update_data = {
            'parser_config': json.dumps(current_config)
        }
        
        result = DocumentService.update(doc_id, update_data)
        print(f"   ✅ 配置修复成功，影响行数: {result}")
        print(f"   新配置: {current_config}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 修复失败: {e}")
        return False

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法: python debug_document_issue.py <doc_id> [--fix]")
        print("示例: python debug_document_issue.py 6a209a9c57cc11f0b66dd0f405336f4c")
        print("修复: python debug_document_issue.py 6a209a9c57cc11f0b66dd0f405336f4c --fix")
        return
    
    doc_id = sys.argv[1]
    fix_mode = '--fix' in sys.argv
    
    print(f"📊 KnowFlow 文档诊断工具")
    print(f"=" * 50)
    
    # 诊断文档
    is_healthy = diagnose_document(doc_id)
    
    if fix_mode:
        if not is_healthy:
            print(f"\n🔧 检测到问题，开始修复...")
            fix_document_config(doc_id)
        else:
            print(f"\n✅ 文档状态正常，无需修复")
    else:
        if not is_healthy:
            print(f"\n💡 建议运行修复: python debug_document_issue.py {doc_id} --fix")
    
    print(f"\n" + "=" * 50)
    print(f"诊断完成")

if __name__ == "__main__":
    main() 