"""
Генератор сертификатов на русском языке с поддержкой Unicode
"""
import io
from django.core.files.base import ContentFile
from django.conf import settings
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch, mm
from reportlab.lib.colors import Color, blue, black, gold
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
from datetime import datetime


class RussianCertificateGenerator:
    """Генератор сертификатов на русском языке с поддержкой Unicode"""
    
    def __init__(self):
        self.width, self.height = landscape(A4)
        self._setup_fonts()
        
    def _setup_fonts(self):
        """Настраивает шрифты с поддержкой кириллицы"""
        try:
            # Пытаемся зарегистрировать системные шрифты Windows
            fonts_registered = False
            
            # Проверяем Arial
            arial_path = 'C:/Windows/Fonts/arial.ttf'
            arial_bold_path = 'C:/Windows/Fonts/arialbd.ttf'
            
            if os.path.exists(arial_path):
                try:
                    pdfmetrics.registerFont(TTFont('ArialUnicode', arial_path))
                    self.regular_font = 'ArialUnicode'
                    fonts_registered = True
                    print("Arial Unicode зарегистрирован")
                except Exception as e:
                    print(f"Ошибка регистрации Arial: {e}")
            
            if os.path.exists(arial_bold_path):
                try:
                    pdfmetrics.registerFont(TTFont('ArialBoldUnicode', arial_bold_path))
                    self.bold_font = 'ArialBoldUnicode'
                    print("Arial Bold Unicode зарегистрирован")
                except Exception as e:
                    print(f"Ошибка регистрации Arial Bold: {e}")
                    
            # Если Arial не удалось, пробуем Calibri
            if not fonts_registered:
                calibri_path = 'C:/Windows/Fonts/calibri.ttf'
                calibri_bold_path = 'C:/Windows/Fonts/calibrib.ttf'
                
                if os.path.exists(calibri_path):
                    try:
                        pdfmetrics.registerFont(TTFont('CalibriUnicode', calibri_path))
                        self.regular_font = 'CalibriUnicode'
                        fonts_registered = True
                        print("Calibri Unicode зарегистрирован")
                    except Exception as e:
                        print(f"Ошибка регистрации Calibri: {e}")
                        
                if os.path.exists(calibri_bold_path):
                    try:
                        pdfmetrics.registerFont(TTFont('CalibriBoldUnicode', calibri_bold_path))
                        self.bold_font = 'CalibriBoldUnicode'
                        print("Calibri Bold Unicode зарегистрирован")
                    except Exception as e:
                        print(f"Ошибка регистрации Calibri Bold: {e}")
                        
            # Если ничего не получилось, используем стандартные
            if not fonts_registered:
                print("Используем стандартные шрифты")
                self.regular_font = 'Helvetica'
                self.bold_font = 'Helvetica-Bold'
            else:
                print("Unicode шрифты успешно зарегистрированы")
                
        except Exception as e:
            print(f"Ошибка настройки шрифтов: {e}")
            self.regular_font = 'Helvetica'
            self.bold_font = 'Helvetica-Bold'
        
        # Устанавливаем значения по умолчанию, если не установлены
        if not hasattr(self, 'regular_font'):
            self.regular_font = 'Helvetica'
        if not hasattr(self, 'bold_font'):
            self.bold_font = 'Helvetica-Bold'
        
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
        
        # Элегантный заголовок с тенью
        try:
            # Тень заголовка
            canvas.setFont(self.bold_font, 48)
            canvas.setFillColor(Color(0.7, 0.7, 0.7))  # Серая тень
            title = "СЕРТИФИКАТ"
            title_width = canvas.stringWidth(title, self.bold_font, 48)
            x = (self.width - title_width) / 2
            y = self.height - 125
            canvas.drawString(x + 2, y - 2, title)  # Смещение для тени
            
            # Основной заголовок
            canvas.setFillColor(Color(0.1, 0.2, 0.7))  # Темно-синий
            canvas.drawString(x, y, title)
            
            # Декоративная линия под заголовком
            canvas.setStrokeColor(gold)
            canvas.setLineWidth(3)
            canvas.line(x - 30, y - 15, x + title_width + 30, y - 15)
            
        except:
            # Fallback на английский
            canvas.setFont("Helvetica-Bold", 48)
            canvas.setFillColor(Color(0.7, 0.7, 0.7))
            title = "CERTIFICATE"
            title_width = canvas.stringWidth(title, "Helvetica-Bold", 48)
            x = (self.width - title_width) / 2
            y = self.height - 125
            canvas.drawString(x + 2, y - 2, title)
            
            canvas.setFillColor(Color(0.1, 0.2, 0.7))
            canvas.drawString(x, y, title)
            
            canvas.setStrokeColor(gold)
            canvas.setLineWidth(3)
            canvas.line(x - 30, y - 15, x + title_width + 30, y - 15)
        
        # Элегантный подзаголовок
        try:
            canvas.setFont(self.regular_font, 20)
            canvas.setFillColor(Color(0.3, 0.3, 0.3))  # Темно-серый
            subtitle = "О ЗАВЕРШЕНИИ КУРСА"
            subtitle_width = canvas.stringWidth(subtitle, self.regular_font, 20)
            x = (self.width - subtitle_width) / 2
            y = self.height - 165
            canvas.drawString(x, y, subtitle)
            
            # Декоративные элементы по бокам подзаголовка
            canvas.setStrokeColor(Color(0.8, 0.65, 0.1))
            canvas.setLineWidth(2)
            # Левая декорация
            canvas.line(x - 50, y + 5, x - 20, y + 5)
            canvas.circle(x - 15, y + 5, 3, fill=1)
            # Правая декорация
            canvas.line(x + subtitle_width + 20, y + 5, x + subtitle_width + 50, y + 5)
            canvas.circle(x + subtitle_width + 15, y + 5, 3, fill=1)
            
        except:
            canvas.setFont("Helvetica", 20)
            canvas.setFillColor(Color(0.3, 0.3, 0.3))
            subtitle = "OF COMPLETION"
            subtitle_width = canvas.stringWidth(subtitle, "Helvetica", 20)
            x = (self.width - subtitle_width) / 2
            y = self.height - 165
            canvas.drawString(x, y, subtitle)
        
        # Основной текст
        self._draw_main_text(canvas, certificate)
        
        # Детали курса
        self._draw_course_details(canvas, certificate)
        
        # Подписи и печати
        self._draw_signatures(canvas, certificate)
        
        # ID сертификата
        self._draw_certificate_id(canvas, certificate)
    
    def _draw_border(self, canvas):
        """Рисует декоративную рамку с улучшенным дизайном"""
        # Фоновый градиент (имитация)
        canvas.setFillColor(Color(0.98, 0.98, 0.99))  # Очень светло-серый
        canvas.rect(0, 0, self.width, self.height, fill=1, stroke=0)
        
        # Основная внешняя рамка
        canvas.setStrokeColor(gold)
        canvas.setLineWidth(6)
        canvas.rect(25, 25, self.width - 50, self.height - 50, fill=0, stroke=1)
        
        # Вторая рамка
        canvas.setStrokeColor(Color(0.8, 0.65, 0.1))  # Темнее золотого
        canvas.setLineWidth(2)
        canvas.rect(35, 35, self.width - 70, self.height - 70, fill=0, stroke=1)
        
        # Внутренняя элегантная рамка
        canvas.setStrokeColor(blue)
        canvas.setLineWidth(3)
        canvas.rect(45, 45, self.width - 90, self.height - 90, fill=0, stroke=1)
        
        # Декоративные углы - более сложные
        corner_size = 30
        corners = [(45, self.height - 45), (self.width - 45, self.height - 45), 
                  (45, 45), (self.width - 45, 45)]
        
        for x, y in corners:
            # Золотые угловые элементы
            canvas.setStrokeColor(gold)
            canvas.setFillColor(gold)
            canvas.setLineWidth(3)
            
            # Угловые линии
            if x < self.width / 2:  # Левые углы
                if y > self.height / 2:  # Верхний левый
                    canvas.line(x, y, x + corner_size, y)
                    canvas.line(x, y, x, y - corner_size)
                else:  # Нижний левый
                    canvas.line(x, y, x + corner_size, y)
                    canvas.line(x, y, x, y + corner_size)
            else:  # Правые углы
                if y > self.height / 2:  # Верхний правый
                    canvas.line(x, y, x - corner_size, y)
                    canvas.line(x, y, x, y - corner_size)
                else:  # Нижний правый
                    canvas.line(x, y, x - corner_size, y)
                    canvas.line(x, y, x, y + corner_size)
            
            # Декоративные кружочки
            canvas.circle(x, y, 8, fill=1)
        
        # Центральные декоративные элементы
        center_x = self.width / 2
        
        # Верхний декоративный элемент
        canvas.setStrokeColor(Color(0.2, 0.3, 0.8))  # Темно-синий
        canvas.setFillColor(Color(0.2, 0.3, 0.8))
        canvas.setLineWidth(2)
        
        # Декоративная полоса сверху
        for i in range(5):
            x = center_x - 60 + i * 30
            y = self.height - 75
            canvas.circle(x, y, 4, fill=1)
        
        # Декоративная полоса снизу  
        for i in range(5):
            x = center_x - 60 + i * 30
            y = 75
            canvas.circle(x, y, 4, fill=1)
    
    def _draw_main_text(self, canvas, certificate):
        """Рисует основной текст с именем студента"""
        try:
            # Элегантная вводная фраза
            canvas.setFont(self.regular_font, 16)
            canvas.setFillColor(Color(0.2, 0.2, 0.2))  # Темно-серый
            
            text1 = "Настоящим подтверждается, что"
            text1_width = canvas.stringWidth(text1, self.regular_font, 16)
            x = (self.width - text1_width) / 2
            y = self.height - 220
            canvas.drawString(x, y, text1)
            
            # Декоративная рамка для имени студента
            student_name = certificate.user.get_full_name() or certificate.user.username
            canvas.setFont(self.bold_font, 32)
            
            # Тень для имени
            canvas.setFillColor(Color(0.8, 0.8, 0.8))
            name_width = canvas.stringWidth(student_name, self.bold_font, 32)
            x = (self.width - name_width) / 2
            y = self.height - 265
            canvas.drawString(x + 1, y - 1, student_name)
            
            # Основное имя
            canvas.setFillColor(Color(0.1, 0.3, 0.7))  # Красивый синий
            canvas.drawString(x, y, student_name)
            
            # Элегантное подчеркивание с декором
            canvas.setStrokeColor(gold)
            canvas.setLineWidth(3)
            canvas.line(x - 40, y - 15, x + name_width + 40, y - 15)
            
            # Декоративные элементы по краям линии
            canvas.setFillColor(gold)
            canvas.circle(x - 45, y - 15, 5, fill=1)
            canvas.circle(x + name_width + 45, y - 15, 5, fill=1)
            
            # Элегантный текст завершения
            canvas.setFont(self.regular_font, 16)
            canvas.setFillColor(Color(0.2, 0.2, 0.2))
            
            text2 = "успешно завершил(а) курс"
            text2_width = canvas.stringWidth(text2, self.regular_font, 16)
            x = (self.width - text2_width) / 2
            y = self.height - 305
            canvas.drawString(x, y, text2)
            
        except Exception as e:
            print(f"Ошибка с кириллицей в основном тексте: {e}")
            # Fallback на английский
            canvas.setFont("Helvetica", 18)
            canvas.setFillColor(black)
            
            text1 = "This is to certify that"
            text1_width = canvas.stringWidth(text1, "Helvetica", 18)
            x = (self.width - text1_width) / 2
            y = self.height - 210
            canvas.drawString(x, y, text1)
            
            student_name = certificate.user.get_full_name() or certificate.user.username
            canvas.setFont("Helvetica-Bold", 28)
            canvas.setFillColor(blue)
            
            name_width = canvas.stringWidth(student_name, "Helvetica-Bold", 28)
            x = (self.width - name_width) / 2
            y = self.height - 250
            canvas.drawString(x, y, student_name)
            
            canvas.setStrokeColor(blue)
            canvas.setLineWidth(2)
            canvas.line(x - 20, y - 10, x + name_width + 20, y - 10)
            
            canvas.setFont("Helvetica", 18)
            canvas.setFillColor(black)
            
            text2 = "has successfully completed the course"
            text2_width = canvas.stringWidth(text2, "Helvetica", 18)
            x = (self.width - text2_width) / 2
            y = self.height - 290
            canvas.drawString(x, y, text2)
    
    def _draw_course_details(self, canvas, certificate):
        """Рисует детали курса с улучшенным дизайном"""
        try:
            # Элегантная рамка для названия курса
            course_title = certificate.course.title
            canvas.setFont(self.bold_font, 26)
            
            # Фон для названия курса
            title_width = canvas.stringWidth(course_title, self.bold_font, 26)
            x = (self.width - title_width) / 2
            y = self.height - 350
            
            # Декоративная рамка вокруг названия
            canvas.setStrokeColor(Color(0.8, 0.65, 0.1))
            canvas.setFillColor(Color(0.98, 0.96, 0.9))  # Светло-кремовый фон
            canvas.setLineWidth(2)
            canvas.rect(x - 30, y - 10, title_width + 60, 35, fill=1, stroke=1)
            
            # Название курса
            canvas.setFillColor(Color(0.1, 0.2, 0.6))  # Темно-синий
            canvas.drawString(x, y, course_title)
            
            # Декоративные детали курса в элегантных блоках
            canvas.setFont(self.regular_font, 12)
            details_y = self.height - 410
            
            # Левый блок деталей
            canvas.setStrokeColor(Color(0.7, 0.7, 0.7))
            canvas.setFillColor(Color(0.96, 0.96, 0.98))
            canvas.setLineWidth(1)
            canvas.rect(80, details_y - 70, 200, 80, fill=1, stroke=1)
            
            # Заголовок левого блока
            canvas.setFont(self.bold_font, 10)
            canvas.setFillColor(Color(0.2, 0.2, 0.6))
            canvas.drawString(90, details_y - 10, "ДЕТАЛИ КУРСА")
            
            # Детали в левом блоке
            canvas.setFont(self.regular_font, 10)
            canvas.setFillColor(Color(0.3, 0.3, 0.3))
            
            completion_date = certificate.completion_date.strftime("%d.%m.%Y")
            canvas.drawString(90, details_y - 25, f"Дата завершения:")
            canvas.setFont(self.bold_font, 10)
            canvas.drawString(90, details_y - 38, completion_date)
            
            canvas.setFont(self.regular_font, 10)
            if certificate.total_hours:
                canvas.drawString(90, details_y - 52, f"Продолжительность:")
                canvas.setFont(self.bold_font, 10)
                canvas.drawString(90, details_y - 65, f"{certificate.total_hours} ч.")
            
            # Правый блок деталей (если есть оценка)
            if certificate.grade:
                canvas.setStrokeColor(Color(0.7, 0.7, 0.7))
                canvas.setFillColor(Color(0.96, 0.98, 0.96))
                canvas.setLineWidth(1)
                canvas.rect(self.width - 280, details_y - 70, 200, 80, fill=1, stroke=1)
                
                # Заголовок правого блока
                canvas.setFont(self.bold_font, 10)
                canvas.setFillColor(Color(0.2, 0.6, 0.2))
                canvas.drawString(self.width - 270, details_y - 10, "РЕЗУЛЬТАТЫ")
                
                # Оценка
                canvas.setFont(self.regular_font, 10)
                canvas.setFillColor(Color(0.3, 0.3, 0.3))
                canvas.drawString(self.width - 270, details_y - 25, "Итоговая оценка:")
                
                # Большая оценка
                canvas.setFont(self.bold_font, 20)
                grade_color = Color(0.2, 0.7, 0.2) if certificate.grade >= 70 else Color(0.7, 0.3, 0.2)
                canvas.setFillColor(grade_color)
                canvas.drawString(self.width - 270, details_y - 55, f"{certificate.grade:.0f}/100")
            
            # Тип курса внизу по центру
            course_type = certificate.course.get_type_display()
            canvas.setFont(self.regular_font, 10)
            canvas.setFillColor(Color(0.5, 0.5, 0.5))
            type_width = canvas.stringWidth(f"Тип курса: {course_type}", self.regular_font, 10)
            canvas.drawString((self.width - type_width) / 2, details_y - 85, f"Тип курса: {course_type}")
            
        except Exception as e:
            print(f"Ошибка в деталях курса: {e}")
            # Fallback на английский
            course_title = certificate.course.title
            canvas.setFont("Helvetica-Bold", 24)
            canvas.setFillColor(blue)
            
            title_width = canvas.stringWidth(course_title, "Helvetica-Bold", 24)
            x = (self.width - title_width) / 2
            y = self.height - 330
            canvas.drawString(x, y, course_title)
            
            canvas.setStrokeColor(blue)
            canvas.setLineWidth(2)
            canvas.line(x - 20, y - 10, x + title_width + 20, y - 10)
    
    def _draw_signatures(self, canvas, certificate):
        """Рисует подписи и печати с элегантным дизайном"""
        y_position = 180
        
        try:
            # Левый блок - Подпись преподавателя
            canvas.setStrokeColor(Color(0.7, 0.7, 0.7))
            canvas.setFillColor(Color(0.98, 0.98, 0.99))
            canvas.setLineWidth(1)
            canvas.rect(70, y_position - 60, 280, 70, fill=1, stroke=1)
            
            # Заголовок блока
            canvas.setFont(self.bold_font, 10)
            canvas.setFillColor(Color(0.2, 0.2, 0.6))
            canvas.drawString(80, y_position - 15, "ПРЕПОДАВАТЕЛЬ")
            
            # Элегантная линия для подписи
            canvas.setStrokeColor(Color(0.3, 0.3, 0.3))
            canvas.setLineWidth(2)
            canvas.line(80, y_position - 35, 330, y_position - 35)
            
            # Имя преподавателя
            instructor_name = certificate.course.instructor.get_full_name() or certificate.course.instructor.username
            canvas.setFont(self.regular_font, 11)
            canvas.setFillColor(Color(0.2, 0.2, 0.2))
            canvas.drawString(80, y_position - 50, instructor_name)
            
            # Правый блок - Дата и печать
            canvas.setStrokeColor(Color(0.7, 0.7, 0.7))
            canvas.setFillColor(Color(0.98, 0.99, 0.98))
            canvas.setLineWidth(1)
            canvas.rect(self.width - 300, y_position - 60, 230, 70, fill=1, stroke=1)
            
            # Дата выдачи
            canvas.setFont(self.bold_font, 10)
            canvas.setFillColor(Color(0.2, 0.2, 0.6))
            canvas.drawString(self.width - 290, y_position - 15, "ДАТА ВЫДАЧИ")
            
            issue_date = certificate.issued_at.strftime("%d.%m.%Y")
            canvas.setFont(self.regular_font, 12)
            canvas.setFillColor(Color(0.2, 0.2, 0.2))
            canvas.drawString(self.width - 290, y_position - 35, issue_date)
            
            # Элегантная печать
            seal_x = self.width - 120
            seal_y = y_position - 30
            
            # Внешний круг печати
            canvas.setStrokeColor(Color(0.1, 0.2, 0.7))
            canvas.setFillColor(Color(0.9, 0.95, 1.0))
            canvas.setLineWidth(3)
            canvas.circle(seal_x, seal_y, 30, fill=1, stroke=1)
            
            # Внутренний круг
            canvas.setStrokeColor(Color(0.1, 0.2, 0.7))
            canvas.setLineWidth(2)
            canvas.circle(seal_x, seal_y, 22, fill=0, stroke=1)
            
            # Текст печати
            canvas.setFont(self.bold_font, 8)
            canvas.setFillColor(Color(0.1, 0.2, 0.7))
            text = "М.П."
            text_width = canvas.stringWidth(text, self.bold_font, 8)
            canvas.drawString(seal_x - text_width/2, seal_y - 3, text)
            
            # Декоративные элементы печати
            canvas.setFillColor(Color(0.1, 0.2, 0.7))
            for angle in [0, 72, 144, 216, 288]:  # 5 звездочек
                import math
                x = seal_x + 18 * math.cos(math.radians(angle))
                y = seal_y + 18 * math.sin(math.radians(angle))
                canvas.circle(x, y, 2, fill=1)
                
        except Exception as e:
            print(f"Ошибка в подписях: {e}")
            # Простой fallback
            canvas.setFont("Helvetica", 12)
            canvas.drawString(100, y_position, "Instructor:")
            
            issue_date = certificate.issued_at.strftime("%B %d, %Y")
            canvas.drawString(self.width - 250, y_position, f"Date Issued: {issue_date}")
    
    def _draw_certificate_id(self, canvas, certificate):
        """Рисует ID сертификата"""
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(Color(0.5, 0.5, 0.5))
        
        cert_id_text = f"Certificate ID: {certificate.certificate_id}"
        canvas.drawString(50, 20, cert_id_text)
        
        verification_text = f"Verify: {settings.SITE_URL or 'http://localhost:8000'}{certificate.verification_url}"
        canvas.drawString(50, 10, verification_text)


def generate_certificate_for_enrollment(certificate):
    """Основная функция для генерации сертификата"""
    generator = RussianCertificateGenerator()
    pdf_content = generator.generate_certificate_pdf(certificate)
    
    # Сохраняем PDF в модель
    certificate.pdf_file.save(
        f'certificate_{certificate.certificate_id}.pdf',
        pdf_content,
        save=True
    )
    
    return certificate