"""
Excel Parser Service

Parse file Excel để import câu hỏi trắc nghiệm.

Format Excel:
- Cột 1: text (Nội dung câu hỏi)
- Cột 2: A (Đáp án A)
- Cột 3: B (Đáp án B)
- Cột 4: C (Đáp án C)
- Cột 5: D (Đáp án D)
- Cột 6: correct (Đáp án đúng: A/B/C/D)
- Cột 7: explanation (Giải thích - optional)
- Cột 8: points (Điểm cho câu hỏi - optional, mặc định 1)
"""
from typing import List, Dict, Any, BinaryIO
import io


class ExcelParseError(Exception):
    """Error khi parse Excel"""
    pass


class ExcelQuestionParser:
    """
    Parse file Excel để lấy danh sách câu hỏi
    
    Hỗ trợ cả .xlsx và .xls
    """
    
    # Column mapping
    COLUMN_MAPPING = {
        0: 'text',
        1: 'A',
        2: 'B',
        3: 'C',
        4: 'D',
        5: 'correct',
        6: 'explanation',
        7: 'points',
    }
    
    # Alternative column names (in header row)
    HEADER_MAPPING = {
        'text': 'text',
        'câu hỏi': 'text',
        'nội dung': 'text',
        'question': 'text',
        'content': 'text',
        'a': 'A',
        'đáp án a': 'A',
        'option a': 'A',
        'b': 'B',
        'đáp án b': 'B',
        'option b': 'B',
        'c': 'C',
        'đáp án c': 'C',
        'option c': 'C',
        'd': 'D',
        'đáp án d': 'D',
        'option d': 'D',
        'correct': 'correct',
        'đáp án đúng': 'correct',
        'answer': 'correct',
        'đáp án': 'correct',
        'explanation': 'explanation',
        'giải thích': 'explanation',
        'points': 'points',
        'điểm': 'points',
        'point': 'points',
        'score': 'points',
    }
    
    def parse(self, file: BinaryIO, filename: str = '') -> List[Dict[str, Any]]:
        """
        Parse file Excel và trả về danh sách câu hỏi
        
        Args:
            file: File object (binary mode)
            filename: Tên file để xác định format
            
        Returns:
            List of dicts: [{'text': '...', 'A': '...', 'B': '...', 'C': '...', 'D': '...', 'correct': 'A', 'explanation': '...', 'points': '1'}]
        """
        try:
            import openpyxl
        except ImportError:
            raise ExcelParseError("Cần cài đặt openpyxl: pip install openpyxl")
        
        # Đọc file
        try:
            # Reset file position
            file.seek(0)
            workbook = openpyxl.load_workbook(file, read_only=True, data_only=True)
            sheet = workbook.active
        except Exception as e:
            raise ExcelParseError(f"Không thể đọc file Excel: {str(e)}")
        
        questions = []
        column_mapping = None
        
        for row_idx, row in enumerate(sheet.iter_rows(values_only=True), start=1):
            # Skip empty rows
            if not row or all(cell is None or str(cell).strip() == '' for cell in row):
                continue
            
            # Detect header row
            if column_mapping is None:
                column_mapping = self._detect_column_mapping(row)
                if column_mapping:
                    continue  # Skip header row
                else:
                    # No header detected, use default mapping
                    column_mapping = self.COLUMN_MAPPING
            
            # Parse data row
            question_data = self._parse_row(row, column_mapping)
            if question_data:
                questions.append(question_data)
        
        workbook.close()
        return questions
    
    def _detect_column_mapping(self, row) -> Dict[int, str]:
        """
        Detect column mapping from header row
        
        Returns None if no header detected
        """
        mapping = {}
        has_header = False
        
        for col_idx, cell in enumerate(row):
            if cell is None:
                continue
            
            cell_lower = str(cell).strip().lower()
            if cell_lower in self.HEADER_MAPPING:
                mapping[col_idx] = self.HEADER_MAPPING[cell_lower]
                has_header = True
        
        if has_header and 'text' in mapping.values():
            return mapping
        
        return None
    
    def _parse_row(self, row, column_mapping: Dict[int, str]) -> Dict[str, Any]:
        """
        Parse a single data row
        """
        data = {}
        
        for col_idx, field_name in column_mapping.items():
            if col_idx < len(row):
                value = row[col_idx]
                if value is not None:
                    # Xử lý đặc biệt cho points (có thể là số)
                    if field_name == 'points':
                        try:
                            # Thử convert sang số
                            points_value = float(value)
                            data[field_name] = str(points_value)
                        except (ValueError, TypeError):
                            # Nếu không phải số, dùng string
                            data[field_name] = str(value).strip() if str(value).strip() else ''
                    else:
                        data[field_name] = str(value).strip()
                else:
                    data[field_name] = ''
            else:
                data[field_name] = ''
        
        # Skip if no text
        if not data.get('text'):
            return None
        
        return data
    
    def parse_from_bytes(self, file_bytes: bytes) -> List[Dict[str, Any]]:
        """
        Parse từ bytes data
        """
        return self.parse(io.BytesIO(file_bytes))

