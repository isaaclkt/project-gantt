"""
PDF Export Service - Professional Corporate Reports

Generates professional PDF reports for projects following corporate design standards:
- Clean typography hierarchy
- Proper table formatting with zebra striping
- Consistent spacing and alignment
- Professional color scheme
- Proper page numbering with footer
"""
from datetime import datetime, timedelta
from io import BytesIO
from typing import Optional, List
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    KeepTogether,
    PageBreak,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.graphics.shapes import Drawing, Rect, Line
from reportlab.graphics.shapes import String as RLString
from app.config.database import db
from app.models import Project, User


class PDFExportService:
    """Service for generating professional PDF reports"""

    # Corporate color scheme
    PRIMARY_COLOR = colors.HexColor('#1E40AF')
    PRIMARY_DARK = colors.HexColor('#1E3A8A')
    SECONDARY_BG = colors.HexColor('#F9FAFB')
    ACCENT_COLOR = colors.HexColor('#3B82F6')
    SUCCESS_COLOR = colors.HexColor('#10B981')
    WARNING_COLOR = colors.HexColor('#F59E0B')
    DANGER_COLOR = colors.HexColor('#EF4444')

    TEXT_DARK = colors.HexColor('#1F2937')
    TEXT_GRAY = colors.HexColor('#6B7280')
    TEXT_LIGHT = colors.HexColor('#9CA3AF')
    BORDER_COLOR = colors.HexColor('#E5E7EB')
    HEADER_BG = colors.HexColor('#F3F4F6')

    # Status configuration - initialized after class definition
    STATUS_CONFIG = None
    PROJECT_STATUS_CONFIG = None
    PRIORITY_CONFIG = None

    @staticmethod
    def _init_configs():
        """Initialize configuration dictionaries after class is defined"""
        if PDFExportService.STATUS_CONFIG is None:
            PDFExportService.STATUS_CONFIG = {
                'todo': {'label': 'A Fazer', 'color': PDFExportService.TEXT_GRAY},
                'in-progress': {'label': 'Em Progresso', 'color': PDFExportService.ACCENT_COLOR},
                'review': {'label': 'Em Revisao', 'color': PDFExportService.WARNING_COLOR},
                'completed': {'label': 'Concluida', 'color': PDFExportService.SUCCESS_COLOR},
            }

            PDFExportService.PROJECT_STATUS_CONFIG = {
                'planning': {'label': 'Planejamento', 'color': PDFExportService.TEXT_GRAY},
                'active': {'label': 'Ativo', 'color': PDFExportService.ACCENT_COLOR},
                'on-hold': {'label': 'Em Pausa', 'color': PDFExportService.WARNING_COLOR},
                'completed': {'label': 'Concluido', 'color': PDFExportService.SUCCESS_COLOR},
            }

            PDFExportService.PRIORITY_CONFIG = {
                'low': {'label': 'Baixa', 'color': PDFExportService.SUCCESS_COLOR},
                'medium': {'label': 'Media', 'color': PDFExportService.WARNING_COLOR},
                'high': {'label': 'Alta', 'color': PDFExportService.DANGER_COLOR},
            }

    @staticmethod
    def _get_styles() -> dict:
        """Get or create professional document styles"""
        styles = getSampleStyleSheet()

        # Title style - large, bold
        styles['Title'].fontSize = 20
        styles['Title'].textColor = PDFExportService.PRIMARY_DARK
        styles['Title'].spaceAfter = 12
        styles['Title'].fontName = 'Helvetica-Bold'
        styles['Title'].alignment = TA_CENTER

        # Section header style
        styles.add(ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=PDFExportService.PRIMARY_DARK,
            spaceAfter=8,
            fontName='Helvetica-Bold',
            borderWidth=0,
            borderPadding=0,
        ))

        # Normal body text
        styles['Normal'].fontSize = 10
        styles['Normal'].textColor = PDFExportService.TEXT_DARK
        styles['Normal'].spaceAfter = 4
        styles['Normal'].leading = 14

        # Secondary text (lighter)
        styles.add(ParagraphStyle(
            'Secondary',
            parent=styles['Normal'],
            fontSize=10,
            textColor=PDFExportService.TEXT_GRAY,
            spaceAfter=4,
            leading=14,
        ))

        # Small text
        styles.add(ParagraphStyle(
            'Small',
            parent=styles['Normal'],
            fontSize=9,
            textColor=PDFExportService.TEXT_GRAY,
            spaceAfter=3,
        ))

        # Footer style
        styles.add(ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=PDFExportService.TEXT_LIGHT,
            alignment=TA_RIGHT,
        ))

        return styles

    @staticmethod
    def generate_project_report(project_id: str) -> BytesIO:
        """
        Generate a professional PDF report for a project.

        Args:
            project_id: The project ID to generate report for

        Returns:
            BytesIO object containing the PDF data
        """
        # Initialize config dictionaries
        PDFExportService._init_configs()

        # Get project
        project = Project.query.get(project_id)
        if not project:
            raise ValueError('Project not found')

        # Get project owner
        owner = User.query.get(project.owner_id) if project.owner_id else None

        # Get all tasks (non-deleted)
        tasks = project.tasks.filter_by(deleted_at=None).all()

        # Sort tasks by start date
        tasks.sort(key=lambda t: t.start_date)

        # Calculate date range for Gantt
        if tasks:
            min_date = min(task.start_date for task in tasks)
            max_date = max(task.end_date for task in tasks)
            padding_days = 3
            min_date = min_date - timedelta(days=padding_days)
            max_date = max_date + timedelta(days=padding_days)
            total_days = (max_date - min_date).days + 1
        else:
            min_date = project.start_date
            max_date = project.end_date
            total_days = (max_date - min_date).days + 1

        # Create PDF document with professional margins
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=1.5 * cm,
            leftMargin=1.5 * cm,
            topMargin=1.5 * cm,
            bottomMargin=1.2 * cm,
        )

        # Get styles
        styles = PDFExportService._get_styles()

        # Build story (document content)
        story = []

        # 1. Title page
        story.extend(PDFExportService._create_title_page(project, styles))

        # 2. Project information
        story.append(PageBreak())
        story.extend(PDFExportService._create_project_section(project, owner, styles))

        # 3. Gantt chart (REMOVIDO - mantendo apenas lista de tarefas)
        # story.append(PageBreak())
        # story.extend(PDFExportService._create_gantt_section(tasks, min_date, total_days, styles))

        # 4. Task list
        story.append(PageBreak())
        story.extend(PDFExportService._create_task_list_section(tasks, styles))

        # Build PDF with page number callback
        doc.build(story, onFirstPage=PDFExportService._add_page_footer,
                     onLaterPages=PDFExportService._add_page_footer)

        buffer.seek(0)
        return buffer

    @staticmethod
    def _create_title_page(project: Project, styles: dict) -> List:
        """Create the title page with project header"""
        elements = []

        # Large spacer at top
        elements.append(Spacer(1, 2 * cm))

        # Project name as main title
        elements.append(Paragraph(
            project.name,
            styles['Title']
        ))

        # Subtitle
        elements.append(Spacer(1, 0.5 * cm))
        elements.append(Paragraph(
            "Relatorio de Progresso",
            styles['SectionHeader']
        ))

        # Divider line
        elements.append(Spacer(1, 1 * cm))
        elements.append(Table([['']], colWidths=[16 * cm],
                               style=TableStyle([
                                   ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                   ('BOTTOMPADDING', (0, 0), (0, -1), 0),
                                   ('LINEBELOW', (0, 0), (0, -1), 1, PDFExportService.PRIMARY_DARK),
                               ])))

        return elements

    @staticmethod
    def _create_project_section(project: Project, owner: Optional[User], styles: dict) -> List:
        """Create project information section with professional layout"""
        elements = []

        # Section header
        elements.append(Paragraph("Informacoes do Projeto", styles['SectionHeader']))
        elements.append(Spacer(1, 0.3 * cm))

        # Info grid data
        info_data = [
            ['Descricao', project.description or 'Nao informada'],
            ['Periodo', f"{project.start_date.strftime('%d/%m/%Y')} ate {project.end_date.strftime('%d/%m/%Y')}"],
            ['Status', PDFExportService.PROJECT_STATUS_CONFIG.get(project.status, {}).get('label', project.status)],
            ['Responsavel', owner.name if owner else 'Nao atribuido'],
            ['Departamento', owner.department_ref.name if owner and owner.department_ref else 'Nao informado'],
            ['Progresso Geral', f"{project.progress}%"],
        ]

        # Create info table
        for label, value in info_data:
            elements.append(Spacer(1, 0.1 * cm))

            # Label
            elements.append(Paragraph(
                f"{label}:",
                styles['Normal']
            ))

            # Value
            elements.append(Paragraph(
                value,
                styles['Normal']
            ))

        # Progress bar visualization
        elements.append(Spacer(1, 0.5 * cm))
        progress_color = PDFExportService.SUCCESS_COLOR if project.progress >= 75 else PDFExportService.WARNING_COLOR if project.progress >= 50 else PDFExportService.TEXT_GRAY

        # Background
        elements.append(Table(
            [[''], ['']],
            colWidths=[14 * cm],
            hAlign='LEFT',
            vAlign='MIDDLE'
        ))

        # Foreground (progress)
        progress_bar_width_cm = project.progress / 100 * 14
        elements.append(Table(
            [[''], ['']],
            colWidths=[progress_bar_width_cm * cm],
            hAlign='LEFT',
            vAlign='MIDDLE'
        ))

        return elements

    @staticmethod
    def _create_gantt_section(tasks: List, min_date, total_days: int, styles: dict) -> List:
        """Create Gantt chart visualization with professional layout"""
        elements = []

        # Section header
        elements.append(Paragraph("Cronograma (Gantt)", styles['SectionHeader']))
        elements.append(Spacer(1, 0.3 * cm))

        if not tasks:
            elements.append(Paragraph(
                "Nenhuma tarefa cadastrada.",
                styles['Secondary']
            ))
            return elements

        # Calculate dimensions
        chart_width = 17 * cm
        row_height = 0.5 * cm
        chart_height = max(4 * cm, len(tasks) * row_height)
        col_width = chart_width / total_days

        # Determine date display interval
        if total_days <= 30:
            show_every = 5
        elif total_days <= 60:
            show_every = 10
        else:
            show_every = 15

        # Create drawing
        drawing = Drawing(chart_width, chart_height)

        # Draw date headers and grid
        y = chart_height - 0.5 * cm
        for i in range(total_days):
            x = i * col_width

            # Vertical grid line
            drawing.add(Line(
                x, 0, x, chart_height - 0.6 * cm,
                strokeColor=PDFExportService.BORDER_COLOR,
                strokeWidth=0.5
            ))

            # Date label
            if i % show_every == 0 or i == total_days - 1:
                current_date = min_date + timedelta(days=i)
                date_str = current_date.strftime('%d/%m')
                drawing.add(RLString(
                    x + col_width / 2, y,
                    date_str,
                    fontName='Helvetica',
                    fontSize=7,
                    fillColor=PDFExportService.TEXT_GRAY,
                    textAnchor='middle'
                ))

        # Draw task bars
        for i, task in enumerate(tasks):
            y = chart_height - 0.6 * cm - (i + 1) * row_height

            # Calculate position
            task_start = (task.start_date - min_date).days
            task_duration = (task.end_date - task.start_date).days + 1
            x = task_start * col_width
            width = task_duration * col_width

            # Get color based on status
            status_config = PDFExportService.STATUS_CONFIG.get(task.status, {})
            color = status_config.get('color', PDFExportService.TEXT_GRAY)

            # Task bar background
            drawing.add(Rect(
                x, y + 0.05 * cm,
                width,
                row_height - 0.1 * cm,
                fillColor=color,
                strokeColor=PDFExportService.BORDER_COLOR,
                strokeWidth=1,
                rx=3,
                ry=3
            ))

            # Task number
            drawing.add(RLString(
                x + 3,
                y + row_height / 2 + 2,
                f"{i + 1}",
                fontName='Helvetica-Bold',
                fontSize=8,
                fillColor=colors.white,
                textAnchor='middle'
            ))

            # Task name - use RLString with truncation
            task_label = task.name
            if len(task_label) > 25:
                task_label = task_label[:25] + "..."

            drawing.add(RLString(
                x + 10,
                y + row_height / 2 + 2,
                task_label,
                fontName='Helvetica',
                fontSize=8,
                fillColor=colors.white,
                textAnchor='start'
            ))

        # Legend
        elements.append(Spacer(1, 0.3 * cm))
        legend_data = []
        for status, label in [
            ('todo', 'A Fazer'),
            ('in-progress', 'Em Progresso'),
            ('review', 'Em Revisao'),
            ('completed', 'Concluida'),
        ]:
            status_config = PDFExportService.STATUS_CONFIG.get(status, {})
            color = status_config.get('color', PDFExportService.TEXT_GRAY)
            legend_data.append([
                Rect(0, 0, 0.3 * cm, 0.3 * cm, fillColor=color, strokeColor=None),
                RLString(0.4 * cm, 0.05 * cm, label,
                          fontName='Helvetica', fontSize=8, fillColor=PDFExportService.TEXT_DARK),
            ])

        if legend_data:
            legend_table = Table(legend_data, colWidths=[0.4 * cm] * len(legend_data))
            legend_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ]))
            elements.append(legend_table)

        elements.append(Spacer(1, 0.3 * cm))
        elements.append(drawing)

        return elements

    @staticmethod
    def _create_task_list_section(tasks: List, styles: dict) -> List:
        """Create detailed task list table with professional layout"""
        elements = []

        # Section header
        elements.append(Paragraph("Lista de Tarefas", styles['SectionHeader']))
        elements.append(Spacer(1, 0.3 * cm))

        if not tasks:
            elements.append(Paragraph(
                "Nenhuma tarefa cadastrada.",
                styles['Secondary']
            ))
            return elements

        # Calculate statistics
        total = len(tasks)
        completed = len([t for t in tasks if t.status == 'completed'])
        in_progress = len([t for t in tasks if t.status == 'in-progress'])
        pending = total - completed - in_progress

        # Statistics cards
        stats_data = [
            ['Total', str(total)],
            ['Concluidas', str(completed)],
            ['Em Progresso', str(in_progress)],
            ['Pendentes', str(pending)],
        ]

        stats_table = Table(stats_data, colWidths=[4 * cm] * 4)
        stats_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
            ('BACKGROUND', (0, 0), (-1, -1), PDFExportService.PRIMARY_COLOR),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(stats_table)
        elements.append(Spacer(1, 0.8 * cm))

        # Task list table
        # Header row
        header_data = [['#', 'Tarefa', 'Status', 'Prioridade', 'Progresso', 'Inicio', 'Termino', 'Responsavel']]

        # Data rows
        for i, task in enumerate(tasks):
            assignee_name = task.assignee.name if task.assignee else 'Nao atribuido'
            status_config = PDFExportService.STATUS_CONFIG.get(task.status, {})
            priority_config = PDFExportService.PRIORITY_CONFIG.get(task.priority, {})

            row_data = [
                str(i + 1),
                task.name,
                status_config.get('label', task.status),
                priority_config.get('label', task.priority),
                f"{task.progress}%",
                task.start_date.strftime('%d/%m/%Y'),
                task.end_date.strftime('%d/%m/%Y'),
                assignee_name,
            ]
            header_data.append(row_data)

        # Column widths
        col_widths = [0.5 * cm, 4.5 * cm, 2 * cm, 1.2 * cm, 1.5 * cm, 1.5 * cm, 2 * cm]

        # Create table
        task_table = Table(header_data, colWidths=col_widths, repeatRows=1)
        task_table.setStyle(TableStyle([
            # Header styling
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('BACKGROUND', (0, 0), (-1, 0), PDFExportService.PRIMARY_COLOR),
            ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),

            # Body styling - even rows
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TEXTCOLOR', (0, 1), (-1, -1), PDFExportService.TEXT_DARK),
            ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
            ('TOPPADDING', (0, 1), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 5),

            # Body styling - odd rows (zebra striping)
            ('FONTNAME', (0, 2), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 2), (-1, -1), 9),
            ('TEXTCOLOR', (0, 2), (-1, -1), PDFExportService.TEXT_DARK),
            ('VALIGN', (0, 2), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 2), (-1, -1), 'CENTER'),
            ('TOPPADDING', (0, 2), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 2), (-1, -1), 5),

            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, PDFExportService.BORDER_COLOR),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [PDFExportService.SECONDARY_BG, colors.white]),
        ]))
        elements.append(task_table)

        return elements

    @staticmethod
    def _add_page_footer(canvas, doc):
        """Add footer to each page with page numbering and generation info"""
        canvas.saveState()

        # Background for footer
        canvas.setFillColor(PDFExportService.SECONDARY_BG)
        canvas.rect(1 * cm, 0, 18 * cm, 0.5 * cm, fill=1, stroke=0)

        # Divider line
        canvas.setLineWidth(1)
        canvas.setStrokeColor(PDFExportService.BORDER_COLOR)
        canvas.line(1 * cm, 0.4 * cm, 18 * cm, 0.4 * cm)

        # Page number (right aligned)
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(PDFExportService.TEXT_LIGHT)
        canvas.drawRightString(
            17 * cm,
            0.3 * cm,
            f"Pagina {canvas.getPageNumber()}"
        )

        # Generation info (left aligned)
        canvas.setFillColor(PDFExportService.TEXT_LIGHT)
        canvas.drawString(
            1 * cm,
            0.3 * cm,
            f"Gerado em: {datetime.now().strftime('%d/%m/%Y as %H:%M')}"
        )

        canvas.restoreState()
