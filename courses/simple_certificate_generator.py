"""
Простой генератор сертификатов на английском языке
"""
import io
from django.core.files.base import ContentFile
from django.conf import settings
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch, mm
from reportlab.lib.colors import Color, blue, black, gold
from datetime import datetime


class SimpleCertificateGenerator:
    """Простой генератор сертификатов на английском языке"""
    
    def __init__(self):
        self.width, self.height = landscape(A4)
    
    def _clean_text(self, text):
        """Очищает текст от кириллицы и заменяет на латиницу"""
        if not text:
            return ""
            
        # Словарь замен для транслитерации
        cyrillic_to_latin = {
            'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'YO',
            'Ж': 'ZH', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M',
            'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
            'Ф': 'F', 'Х': 'H', 'Ц': 'TS', 'Ч': 'CH', 'Ш': 'SH', 'Щ': 'SCH',
            'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'YU', 'Я': 'YA',
            'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
            'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
            'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
            'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
            'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya'
        }
        
        # Специальные замены для популярных терминов
        special_replacements = {
            'Вебинар': 'Webinar',
            'вебинар': 'webinar',
            'Введение в Python': 'Introduction to Python',
            'Мария Сидорова': 'Maria Sidorova',
            'Анна Петрова': 'Anna Petrova',
            'Иван Иванов': 'Ivan Ivanov',
            'Преподаватель': 'Instructor',
            'преподаватель': 'instructor'
        }
        
        # Сначала проверяем специальные замены
        for ru, en in special_replacements.items():
            if ru in text:
                text = text.replace(ru, en)
        
        # Затем транслитерируем оставшуюся кириллицу
        result = ""
        for char in text:
            if char in cyrillic_to_latin:
                result += cyrillic_to_latin[char]
            else:
                result += char
                
        return result
        
    def generate_certificate_pdf(self, certificate):
        """Генерирует PDF сертификат"""
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=landscape(A4))
        
        # Рисуем сертификат
        self._draw_certificate(p, certificate)
        
        p.showPage()
        p.save()
        
        # Создаем ContentFile для сохранения
        buffer.seek(0)
        pdf_content = ContentFile(buffer.getvalue())
        pdf_content.name = f'certificate_{certificate.certificate_id}.pdf'
        
        return pdf_content
    
    def _draw_certificate(self, canvas, certificate):
        """Рисует содержимое сертификата"""
        
        # Фон и рамка
        self._draw_border(canvas)
        
        # Заголовок
        canvas.setFont("Helvetica-Bold", 42)
        canvas.setFillColor(blue)
        title = "CERTIFICATE"
        title_width = canvas.stringWidth(title, "Helvetica-Bold", 42)
        x = (self.width - title_width) / 2
        y = self.height - 120
        canvas.drawString(x, y, title)
        
        # Подзаголовок
        canvas.setFont("Helvetica", 24)
        canvas.setFillColor(black)
        subtitle = "OF COMPLETION"
        subtitle_width = canvas.stringWidth(subtitle, "Helvetica", 24)
        x = (self.width - subtitle_width) / 2
        y = self.height - 160
        canvas.drawString(x, y, subtitle)
        
        # Основной текст
        canvas.setFont("Helvetica", 18)
        text1 = "This is to certify that"
        text1_width = canvas.stringWidth(text1, "Helvetica", 18)
        x = (self.width - text1_width) / 2
        y = self.height - 210
        canvas.drawString(x, y, text1)
        
        # Имя студента (убираем кириллицу)
        student_name = certificate.user.get_full_name() or certificate.user.username
        student_name = self._clean_text(student_name)
        canvas.setFont("Helvetica-Bold", 28)
        canvas.setFillColor(blue)
        name_width = canvas.stringWidth(student_name, "Helvetica-Bold", 28)
        x = (self.width - name_width) / 2
        y = self.height - 250
        canvas.drawString(x, y, student_name)
        
        # Подчеркивание имени
        canvas.setStrokeColor(blue)
        canvas.setLineWidth(2)
        canvas.line(x - 20, y - 10, x + name_width + 20, y - 10)
        
        # Текст завершения
        canvas.setFont("Helvetica", 18)
        canvas.setFillColor(black)
        text2 = "has successfully completed the course"
        text2_width = canvas.stringWidth(text2, "Helvetica", 18)
        x = (self.width - text2_width) / 2
        y = self.height - 290
        canvas.drawString(x, y, text2)
        
        # Название курса (убираем кириллицу)
        course_title = self._clean_text(certificate.course.title)
        canvas.setFont("Helvetica-Bold", 24)
        canvas.setFillColor(blue)
        title_width = canvas.stringWidth(course_title, "Helvetica-Bold", 24)
        x = (self.width - title_width) / 2
        y = self.height - 330
        canvas.drawString(x, y, course_title)
        
        # Подчеркивание названия курса
        canvas.setStrokeColor(blue)
        canvas.setLineWidth(2)
        canvas.line(x - 20, y - 10, x + title_width + 20, y - 10)
        
        # Детали курса
        self._draw_course_details(canvas, certificate)
        
        # Подписи и печати
        self._draw_signatures(canvas, certificate)
        
        # ID сертификата
        self._draw_certificate_id(canvas, certificate)
    
    def _draw_border(self, canvas):
        """Рисует декоративную рамку"""
        # Внешняя рамка
        canvas.setStrokeColor(gold)
        canvas.setLineWidth(4)
        canvas.rect(30, 30, self.width - 60, self.height - 60)
        
        # Внутренняя рамка
        canvas.setStrokeColor(blue)
        canvas.setLineWidth(2)
        canvas.rect(50, 50, self.width - 100, self.height - 100)
        
        # Декоративные элементы в углах
        for x, y in [(70, self.height - 70), (self.width - 70, self.height - 70), 
                     (70, 70), (self.width - 70, 70)]:
            canvas.setStrokeColor(gold)
            canvas.setFillColor(gold)
            canvas.circle(x, y, 12, fill=1)
    
    def _draw_course_details(self, canvas, certificate):
        """Рисует детали курса"""
        canvas.setFont("Helvetica", 12)
        canvas.setFillColor(black)
        
        details_y = self.height - 380
        
        # Дата завершения
        completion_date = certificate.completion_date.strftime("%B %d, %Y")
        canvas.drawString(100, details_y, f"Completion Date: {completion_date}")
        
        # Продолжительность
        if certificate.total_hours:
            canvas.drawString(100, details_y - 20, f"Duration: {certificate.total_hours} hours")
        
        # Итоговая оценка
        if certificate.grade:
            canvas.drawString(100, details_y - 40, f"Final Grade: {certificate.grade:.1f}/100")
        
        # Тип курса
        course_type = certificate.course.get_type_display()
        canvas.drawString(100, details_y - 60, f"Course Type: {course_type}")
    
    def _draw_signatures(self, canvas, certificate):
        """Рисует подписи и печати"""
        y_position = 160
        
        # Подпись преподавателя
        canvas.setFont("Helvetica", 12)
        canvas.drawString(100, y_position, "Instructor:")
        
        # Линия для подписи
        canvas.setStrokeColor(black)
        canvas.setLineWidth(1)
        canvas.line(100, y_position - 20, 320, y_position - 20)
        
        # Имя преподавателя (убираем кириллицу)
        instructor_name = certificate.course.instructor.get_full_name() or certificate.course.instructor.username
        instructor_name = self._clean_text(instructor_name)
        canvas.drawString(100, y_position - 35, instructor_name)
        
        # Дата выдачи
        issue_date = certificate.issued_at.strftime("%B %d, %Y")
        canvas.drawString(self.width - 250, y_position, f"Date Issued: {issue_date}")
        
        # Место для печати
        canvas.setStrokeColor(blue)
        canvas.setLineWidth(3)
        canvas.circle(self.width - 120, y_position - 30, 35, fill=0)
        canvas.setFont("Helvetica-Bold", 10)
        text = "OFFICIAL SEAL"
        text_width = canvas.stringWidth(text, "Helvetica-Bold", 10)
        canvas.drawString(self.width - 120 - text_width/2, y_position - 33, text)
    
    def _draw_certificate_id(self, canvas, certificate):
        """Рисует ID сертификата"""
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(Color(0.5, 0.5, 0.5))
        
        cert_id_text = f"Certificate ID: {certificate.certificate_id}"
        canvas.drawString(50, 20, cert_id_text)
        
        verification_text = f"Verify at: {settings.SITE_URL or 'http://localhost:8000'}{certificate.verification_url}"
        canvas.drawString(50, 10, verification_text)


def generate_certificate_for_enrollment(certificate):
    """Основная функция для генерации сертификата"""
    generator = SimpleCertificateGenerator()
    pdf_content = generator.generate_certificate_pdf(certificate)
    
    # Сохраняем PDF в модель
    certificate.pdf_file.save(
        f'certificate_{certificate.certificate_id}.pdf',
        pdf_content,
        save=True
    )
    
    return certificate