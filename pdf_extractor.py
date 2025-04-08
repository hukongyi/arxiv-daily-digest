import fitz  # PyMuPDF
import os
from pathlib import Path
import tempfile
import re
import traceback

# 可选的OCR支持
try:
    from pdf2image import convert_from_path
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False


class PDFExtractor:
    def __init__(self, ocr_fallback=True, max_pages=None):
        """
        初始化PDF提取器
        
        Args:
            ocr_fallback: 当常规提取失败时是否使用OCR
            max_pages: 最大处理页数，None表示处理所有页面
        """
        self.ocr_fallback = ocr_fallback and OCR_AVAILABLE
        self.max_pages = max_pages
    
    def extract_text_pymupdf(self, pdf_path):
        """
        使用PyMuPDF提取PDF文本
        
        Args:
            pdf_path: PDF文件路径
            
        Returns:
            提取的文本
        """
        try:
            doc = fitz.open(pdf_path)
            page_count = doc.page_count
            
            if self.max_pages and page_count > self.max_pages:
                print(f"PDF有{page_count}页，但只处理前{self.max_pages}页")
                page_count = self.max_pages
            
            text_parts = []
            
            # 提取每一页的文本
            for page_num in range(page_count):
                page = doc[page_num]
                text = page.get_text("text")
                text_parts.append(text)
            
            doc.close()
            full_text = "\n".join(text_parts)
            
            # 检查提取的文本是否有效
            if len(full_text.strip()) < 100:
                print(f"提取的文本太短，可能提取失败: {len(full_text)} 字符")
                return None
            
            return full_text
        
        except Exception as e:
            print(f"PyMuPDF提取失败: {str(e)}")
            traceback.print_exc()
            return None
    
    def extract_text_ocr(self, pdf_path):
        """
        使用OCR提取PDF文本
        
        Args:
            pdf_path: PDF文件路径
            
        Returns:
            提取的文本
        """
        if not OCR_AVAILABLE:
            print("OCR库未安装，无法使用OCR")
            return None
        
        try:
            print(f"使用OCR处理: {pdf_path}")
            
            # 将PDF转换为图像
            images = convert_from_path(pdf_path, dpi=300)
            
            if self.max_pages and len(images) > self.max_pages:
                print(f"PDF有{len(images)}页，但只处理前{self.max_pages}页")
                images = images[:self.max_pages]
            
            text_parts = []
            
            # 对每个图像进行OCR
            for i, image in enumerate(images):
                print(f"OCR处理第 {i+1}/{len(images)} 页...")
                text = pytesseract.image_to_string(image, lang='eng')
                text_parts.append(text)
            
            full_text = "\n".join(text_parts)
            return full_text
        
        except Exception as e:
            print(f"OCR提取失败: {str(e)}")
            traceback.print_exc()
            return None
    
    def extract_text(self, pdf_path):
        """
        提取PDF文本，首先尝试PyMuPDF，如果失败则尝试OCR
        
        Args:
            pdf_path: PDF文件路径
            
        Returns:
            提取的文本，如果提取失败则返回None
        """
        if not os.path.exists(pdf_path):
            print(f"文件不存在: {pdf_path}")
            return None
        
        # 首先尝试使用PyMuPDF提取
        text = self.extract_text_pymupdf(pdf_path)
        
        # 如果PyMuPDF提取失败且启用了OCR回退，则尝试OCR
        if text is None and self.ocr_fallback:
            print(f"PyMuPDF提取失败，尝试OCR: {pdf_path}")
            text = self.extract_text_ocr(pdf_path)
        
        return text
    
    def clean_text(self, text):
        """
        清理提取的文本
        
        Args:
            text: 提取的原始文本
            
        Returns:
            清理后的文本
        """
        if text is None:
            return None
        
        # 移除多余的空白行
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # 移除页眉页脚（简单启发式方法）
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # 跳过可能的页码行
            if re.match(r'^\s*\d+\s*$', line):
                continue
            
            # 跳过短的页眉/页脚行
            if len(line.strip()) < 5:
                continue
                
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def extract_and_clean(self, pdf_path):
        """
        提取并清理PDF文本
        
        Args:
            pdf_path: PDF文件路径
            
        Returns:
            清理后的文本，如果提取失败则返回None
        """
        text = self.extract_text(pdf_path)
        return self.clean_text(text)
    
    def process_papers(self, papers):
        """
        处理论文列表，提取每篇论文的全文
        
        Args:
            papers: 论文列表，每个论文应包含pdf_path字段
            
        Returns:
            更新后的论文列表，每个论文增加full_text字段
        """
        for paper in papers:
            if 'pdf_path' in paper and paper['pdf_path']:
                full_text = self.extract_and_clean(paper['pdf_path'])
                paper['full_text'] = full_text
                
                # 计算提取的文本长度
                if full_text:
                    text_length = len(full_text)
                    print(f"提取了 {text_length} 字符的文本: {paper['title']}")
                else:
                    print(f"文本提取失败: {paper['title']}")
            else:
                paper['full_text'] = None
                print(f"没有PDF路径，跳过文本提取: {paper['title']}")
        
        return papers
