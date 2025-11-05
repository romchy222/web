"""
Модуль для генерации PDF сертификатов
"""
import io
from django.core.files.base import ContentFile
from django.conf import settings
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch, mm
from reportlab.lib.colors import Color, blue, black, gold
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from datetime import datetime
import os


class CertificateGenerator:
    """Класс для генерации PDF сертификатов"""
    
    def __init__(self):
        self.width, self.height = landscape(A4)
        self.styles = getSampleStyleSheet()
        
        # Регистрируем шрифты с поддержкой кириллицы
        self._register_fonts()
    
    def _register_fonts(self):
        """Регистрирует шрифты с поддержкой кириллицы"""
        try:
            # Пробуем зарегистрировать системные шрифты Windows
            arial_path = 'C:/Windows/Fonts/arial.ttf'
            arial_bold_path = 'C:/Windows/Fonts/arialbd.ttf'
            
            if os.path.exists(arial_path) and os.path.exists(arial_bold_path):
                # Регистрируем TTF шрифты Arial с поддержкой Unicode
                pdfmetrics.registerFont(TTFont('Arial-Unicode', arial_path))
                pdfmetrics.registerFont(TTFont('Arial-Bold-Unicode', arial_bold_path))
                self.regular_font = 'Arial-Unicode'
                self.bold_font = 'Arial-Bold-Unicode'
                print("Зарегистрированы Arial шрифты с Unicode")
            else:
                # Если Arial не найден, пробуем Calibri
                calibri_path = 'C:/Windows/Fonts/calibri.ttf' 
                calibri_bold_path = 'C:/Windows/Fonts/calibrib.ttf'
                
                if os.path.exists(calibri_path) and os.path.exists(calibri_bold_path):
                    pdfmetrics.registerFont(TTFont('Calibri-Unicode', calibri_path))
                    pdfmetrics.registerFont(TTFont('Calibri-Bold-Unicode', calibri_bold_path))
                    self.regular_font = 'Calibri-Unicode'
                    self.bold_font = 'Calibri-Bold-Unicode'
                    print("Зарегистрированы Calibri шрифты с Unicode")
                else:
                    raise Exception("Системные шрифты не найдены")
                    
        except Exception as e:
            print(f"Не удалось загрузить системные шрифты: {e}")
            # Fallback: используем транслитерацию для стандартных шрифтов
            self.regular_font = 'Helvetica'
            self.bold_font = 'Helvetica-Bold'
            self.use_transliteration = True
        
        if not hasattr(self, 'use_transliteration'):
            self.use_transliteration = False
    
    def _transliterate(self, text):
        """Транслитерирует русский текст в латиницу"""
        if not self.use_transliteration:
            return text
            
        ru_en = {
            'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
            'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
            'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
            'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
            'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
            'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'YO',
            'Ж': 'ZH', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M',
            'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
            'Ф': 'F', 'Х': 'H', 'Ц': 'TS', 'Ч': 'CH', 'Ш': 'SH', 'Щ': 'SCH',
            'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'YU', 'Я': 'YA'
        }
        
        result = ''
        for char in text:
            result += ru_en.get(char, char)
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
        self._draw_title(canvas)
        
        # Основной текст
        self._draw_main_text(canvas, certificate)
        
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
        canvas.setLineWidth(3)
        canvas.rect(30, 30, self.width - 60, self.height - 60)
        
        # Внутренняя рамка
        canvas.setStrokeColor(blue)
        canvas.setLineWidth(1)
        canvas.rect(50, 50, self.width - 100, self.height - 100)
        
        # Декоративные элементы в углах
        for x, y in [(70, self.height - 70), (self.width - 70, self.height - 70), 
                     (70, 70), (self.width - 70, 70)]:
            canvas.circle(x, y, 10, fill=0)
    
    def _draw_title(self, canvas):
        """Рисует заголовок сертификата"""
        canvas.setFont(self.bold_font, 36)
        canvas.setFillColor(blue)
        
        title = self._transliterate("SERTIFIKAT" if self.use_transliteration else "СЕРТИФИКАТ")
        title_width = canvas.stringWidth(title, self.bold_font, 36)
        x = (self.width - title_width) / 2
        y = self.height - 120
        
        canvas.drawString(x, y, title)
        
        # Подзаголовок
        canvas.setFont(self.regular_font, 20)
        canvas.setFillColor(black)
        
        subtitle = self._transliterate("O ZAVERSHENII KURSA" if self.use_transliteration else "О ЗАВЕРШЕНИИ КУРСА")
        subtitle_width = canvas.stringWidth(subtitle, self.regular_font, 20)
        x = (self.width - subtitle_width) / 2
        y = self.height - 150
        
        canvas.drawString(x, y, subtitle)
    
    def _draw_main_text(self, canvas, certificate):
        """Рисует основной текст с именем студента"""
        canvas.setFont(self.regular_font, 16)
        canvas.setFillColor(black)
        
        # Текст "Настоящим подтверждается, что"
        text1 = self._transliterate("Nastoyaschim podtverzhdaetsya, chto" if self.use_transliteration else "Настоящим подтверждается, что")
        text1_width = canvas.stringWidth(text1, self.regular_font, 16)
        x = (self.width - text1_width) / 2
        y = self.height - 200
        canvas.drawString(x, y, text1)
        
        # Имя студента
        student_name = certificate.user.get_full_name() or certificate.user.username
        student_name = self._transliterate(student_name)
        canvas.setFont(self.bold_font, 24)
        canvas.setFillColor(blue)
        
        name_width = canvas.stringWidth(student_name, self.bold_font, 24)
        x = (self.width - name_width) / 2
        y = self.height - 240
        canvas.drawString(x, y, student_name)
        
        # Подчеркивание имени
        canvas.setStrokeColor(blue)
        canvas.setLineWidth(2)
        canvas.line(x - 20, y - 10, x + name_width + 20, y - 10)
        
        # Текст "успешно завершил(а) курс"
        canvas.setFont(self.regular_font, 16)
        canvas.setFillColor(black)
        
        text2 = self._transliterate("uspeshno zavershil(a) kurs" if self.use_transliteration else "успешно завершил(а) курс")
        text2_width = canvas.stringWidth(text2, self.regular_font, 16)
        x = (self.width - text2_width) / 2
        y = self.height - 280
        canvas.drawString(x, y, text2)
    
    def _draw_course_details(self, canvas, certificate):
        """Рисует детали курса"""
        # Название курса
        course_title = self._transliterate(certificate.course.title)
        canvas.setFont(self.bold_font, 20)
        canvas.setFillColor(blue)
        
        title_width = canvas.stringWidth(course_title, self.bold_font, 20)
        x = (self.width - title_width) / 2
        y = self.height - 320
        canvas.drawString(x, y, course_title)
        
        # Подчеркивание названия курса
        canvas.setStrokeColor(blue)
        canvas.setLineWidth(2)
        canvas.line(x - 20, y - 10, x + title_width + 20, y - 10)
        
        # Детали курса
        canvas.setFont(self.regular_font, 12)
        canvas.setFillColor(black)
        
        details_y = self.height - 370
        
        # Дата завершения
        completion_date = certificate.completion_date.strftime("%d.%m.%Y")
        canvas.drawString(100, details_y, f"Дата завершения: {completion_date}")
        
        # Продолжительность
        if certificate.total_hours:
            canvas.drawString(100, details_y - 20, f"Продолжительность: {certificate.total_hours} ч.")
        
        # Итоговая оценка
        if certificate.grade:
            canvas.drawString(100, details_y - 40, f"Итоговая оценка: {certificate.grade:.1f}/100")
        
        # Тип курса
        course_type = certificate.course.get_type_display()
        canvas.drawString(100, details_y - 60, f"Тип курса: {course_type}")
    
    def _draw_signatures(self, canvas, certificate):
        """Рисует подписи и печати"""
        y_position = 150
        
        # Подпись преподавателя
        canvas.setFont(self.regular_font, 10)
        canvas.drawString(100, y_position, "Преподаватель:")
        
        # Линия для подписи
        canvas.setStrokeColor(black)
        canvas.setLineWidth(1)
        canvas.line(100, y_position - 20, 300, y_position - 20)
        
        # Имя преподавателя
        instructor_name = certificate.course.instructor.get_full_name()
        if instructor_name:
            canvas.drawString(100, y_position - 35, instructor_name)
        
        # Дата выдачи
        issue_date = certificate.issued_at.strftime("%d.%m.%Y")
        canvas.drawString(self.width - 200, y_position, f"Дата выдачи: {issue_date}")
        
        # Место для печати
        canvas.setStrokeColor(blue)
        canvas.setLineWidth(2)
        canvas.circle(self.width - 150, y_position - 40, 30, fill=0)
        canvas.setFont(self.regular_font, 8)
        text = "М.П."
        text_width = canvas.stringWidth(text, self.regular_font, 8)
        canvas.drawString(self.width - 150 - text_width/2, y_position - 43, text)
    
    def _draw_certificate_id(self, canvas, certificate):
        """Рисует ID сертификата"""
        canvas.setFont(self.regular_font, 8)
        canvas.setFillColor(Color(0.5, 0.5, 0.5))  # Серый цвет
        
        cert_id_text = f"Номер сертификата: {certificate.certificate_id}"
        canvas.drawString(50, 20, cert_id_text)
        
        # QR код или ссылка для верификации (упрощенный вариант)
        verification_text = f"Проверить подлинность: {settings.SITE_URL or 'http://localhost:8000'}{certificate.verification_url}"
        canvas.drawString(50, 10, verification_text)


def generate_certificate_for_enrollment(certificate):
    """Основная функция для генерации сертификата"""
    generator = CertificateGenerator()
    pdf_content = generator.generate_certificate_pdf(certificate)
    
    # Сохраняем PDF в модель
    certificate.pdf_file.save(
        f'certificate_{certificate.certificate_id}.pdf',
        pdf_content,
        save=True
    )
    
    return certificate