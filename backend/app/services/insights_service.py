"""
Insights Service - Smart analysis engine using custom logic

Modular design: to swap to Gemini API later, only change the internals
of this service. The route and frontend remain unchanged.
"""
from datetime import datetime, date, timedelta
from collections import Counter
from app.models import Project, Task, TeamMember


class InsightsService:
    """Generates smart insights from project/task/team data."""

    @staticmethod
    def generate() -> list[dict]:
        """
        Main entry point. Loads all data once, runs all analysis
        methods, and returns a flat list of insights sorted by priority.
        """
        today = date.today()

        # Batch load all data (avoid N+1 queries)
        tasks = Task.query.all()
        projects = Project.query.all()
        members = TeamMember.query.all()

        insights = []

        # Critical
        insights.extend(InsightsService._overdue_tasks(tasks, today))
        insights.extend(InsightsService._overdue_projects(projects, today))
        insights.extend(InsightsService._unassigned_high_priority(tasks))

        # Warning
        insights.extend(InsightsService._due_soon_tasks(tasks, today))
        insights.extend(InsightsService._overloaded_members(tasks, members))
        insights.extend(InsightsService._behind_schedule_projects(projects, today))

        # Positive
        insights.extend(InsightsService._recently_completed(tasks))
        insights.extend(InsightsService._on_track_projects(projects, today))
        insights.extend(InsightsService._top_performer(tasks, members))

        # Info
        insights.extend(InsightsService._summary_stats(tasks, projects, members))

        # Sort: critical first, then warning, positive, info
        priority = {'critical': 0, 'warning': 1, 'positive': 2, 'info': 3}
        insights.sort(key=lambda i: priority.get(i['type'], 99))

        return insights

    # ─── CRITICAL ────────────────────────────────────────────

    @staticmethod
    def _overdue_tasks(tasks: list, today: date) -> list[dict]:
        overdue = [
            t for t in tasks
            if t.end_date and t.end_date < today and t.status != 'completed'
        ]
        if not overdue:
            return []

        count = len(overdue)
        high_priority = [t for t in overdue if t.priority == 'high']

        desc = f'{count} tarefa{"s" if count > 1 else ""} com prazo vencido.'
        if high_priority:
            desc += f' {len(high_priority)} {"são" if len(high_priority) > 1 else "é"} de alta prioridade.'

        # Name the most overdue
        most_overdue = max(overdue, key=lambda t: (today - t.end_date).days)
        days_late = (today - most_overdue.end_date).days
        desc += f' "{most_overdue.name}" está {days_late} dia{"s" if days_late > 1 else ""} atrasada.'

        return [{
            'type': 'critical',
            'icon': 'AlertTriangle',
            'title': f'{count} tarefa{"s" if count > 1 else ""} atrasada{"s" if count > 1 else ""}',
            'description': desc
        }]

    @staticmethod
    def _overdue_projects(projects: list, today: date) -> list[dict]:
        overdue = [
            p for p in projects
            if p.end_date and p.end_date < today
            and p.status not in ('completed',)
        ]
        if not overdue:
            return []

        results = []
        for p in overdue:
            days_late = (today - p.end_date).days
            results.append({
                'type': 'critical',
                'icon': 'FolderClock',
                'title': f'Projeto "{p.name}" passou do prazo',
                'description': f'O prazo terminou há {days_late} dia{"s" if days_late > 1 else ""} e o projeto está {p.progress}% concluído.'
            })
        return results

    @staticmethod
    def _unassigned_high_priority(tasks: list) -> list[dict]:
        unassigned = [
            t for t in tasks
            if t.priority == 'high' and not t.assignee_id and t.status != 'completed'
        ]
        if not unassigned:
            return []

        count = len(unassigned)
        names = ', '.join(f'"{t.name}"' for t in unassigned[:3])
        extra = f' e mais {count - 3}' if count > 3 else ''

        return [{
            'type': 'critical',
            'icon': 'UserX',
            'title': f'{count} tarefa{"s" if count > 1 else ""} de alta prioridade sem responsável',
            'description': f'{names}{extra} {"precisam" if count > 1 else "precisa"} de um responsável atribuído.'
        }]

    # ─── WARNING ─────────────────────────────────────────────

    @staticmethod
    def _due_soon_tasks(tasks: list, today: date) -> list[dict]:
        deadline = today + timedelta(days=3)
        due_soon = [
            t for t in tasks
            if t.end_date and today <= t.end_date <= deadline
            and t.status != 'completed'
        ]
        if not due_soon:
            return []

        count = len(due_soon)
        names = ', '.join(f'"{t.name}"' for t in due_soon[:3])

        return [{
            'type': 'warning',
            'icon': 'Clock',
            'title': f'{count} tarefa{"s" if count > 1 else ""} vencem nos próximos 3 dias',
            'description': f'{names} {"precisam" if count > 1 else "precisa"} de atenção.'
        }]

    @staticmethod
    def _overloaded_members(tasks: list, members: list) -> list[dict]:
        threshold = 5
        active_statuses = ('todo', 'in-progress', 'review')

        # Count active tasks per assignee
        task_counts = Counter(
            t.assignee_id for t in tasks
            if t.assignee_id and t.status in active_statuses
        )

        member_map = {m.id: m.name for m in members}

        overloaded = [
            (member_map.get(mid, 'Desconhecido'), count)
            for mid, count in task_counts.items()
            if count >= threshold
        ]

        if not overloaded:
            return []

        results = []
        for name, count in overloaded:
            results.append({
                'type': 'warning',
                'icon': 'UserCog',
                'title': f'{name} está sobrecarregado(a)',
                'description': f'{count} tarefas ativas atribuídas. Considere redistribuir a carga de trabalho.'
            })
        return results

    @staticmethod
    def _behind_schedule_projects(projects: list, today: date) -> list[dict]:
        results = []
        for p in projects:
            if p.status in ('completed', 'on-hold') or not p.start_date or not p.end_date:
                continue
            if p.end_date <= p.start_date:
                continue

            total_days = (p.end_date - p.start_date).days
            elapsed_days = (today - p.start_date).days

            if elapsed_days <= 0 or total_days <= 0:
                continue

            expected_progress = min((elapsed_days / total_days) * 100, 100)
            actual_progress = p.progress or 0

            # Behind schedule: actual progress is less than 70% of expected
            if expected_progress > 30 and actual_progress < expected_progress * 0.7:
                diff = int(expected_progress - actual_progress)
                results.append({
                    'type': 'warning',
                    'icon': 'TrendingDown',
                    'title': f'"{p.name}" está atrás do cronograma',
                    'description': f'Progresso atual: {actual_progress}%. Esperado: {int(expected_progress)}%. Diferença de {diff} pontos percentuais.'
                })

        return results

    # ─── POSITIVE ────────────────────────────────────────────

    @staticmethod
    def _recently_completed(tasks: list) -> list[dict]:
        completed = [t for t in tasks if t.status == 'completed']
        if not completed:
            return []

        count = len(completed)
        total = len(tasks)
        pct = int((count / total) * 100) if total > 0 else 0

        return [{
            'type': 'positive',
            'icon': 'CheckCircle2',
            'title': f'{count} tarefa{"s" if count > 1 else ""} concluída{"s" if count > 1 else ""}',
            'description': f'{pct}% de todas as tarefas foram finalizadas.'
        }]

    @staticmethod
    def _on_track_projects(projects: list, today: date) -> list[dict]:
        on_track = []
        for p in projects:
            if p.status in ('completed', 'on-hold') or not p.start_date or not p.end_date:
                continue
            if p.end_date <= p.start_date:
                continue

            total_days = (p.end_date - p.start_date).days
            elapsed_days = (today - p.start_date).days

            if elapsed_days <= 0 or total_days <= 0:
                continue

            expected_progress = min((elapsed_days / total_days) * 100, 100)
            actual_progress = p.progress or 0

            if actual_progress >= expected_progress:
                on_track.append(p)

        if not on_track:
            return []

        names = ', '.join(f'"{p.name}"' for p in on_track[:3])
        count = len(on_track)

        return [{
            'type': 'positive',
            'icon': 'TrendingUp',
            'title': f'{count} projeto{"s" if count > 1 else ""} no prazo',
            'description': f'{names} {"estão" if count > 1 else "está"} com progresso igual ou acima do esperado.'
        }]

    @staticmethod
    def _top_performer(tasks: list, members: list) -> list[dict]:
        completed_counts = Counter(
            t.assignee_id for t in tasks
            if t.status == 'completed' and t.assignee_id
        )

        if not completed_counts:
            return []

        top_id, top_count = completed_counts.most_common(1)[0]

        if top_count < 2:
            return []

        member_map = {m.id: m.name for m in members}
        name = member_map.get(top_id, 'Desconhecido')

        return [{
            'type': 'positive',
            'icon': 'Trophy',
            'title': f'{name} lidera em entregas',
            'description': f'{top_count} tarefas concluídas. Maior número de entregas da equipe.'
        }]

    # ─── INFO ────────────────────────────────────────────────

    @staticmethod
    def _summary_stats(tasks: list, projects: list, members: list) -> list[dict]:
        active_projects = [p for p in projects if p.status == 'active']
        active_members = [m for m in members if m.status == 'active']

        total_tasks = len(tasks)
        if total_tasks == 0:
            return [{
                'type': 'info',
                'icon': 'Info',
                'title': 'Nenhuma tarefa cadastrada',
                'description': 'Comece criando projetos e tarefas para ver insights detalhados.'
            }]

        high = len([t for t in tasks if t.priority == 'high' and t.status != 'completed'])
        medium = len([t for t in tasks if t.priority == 'medium' and t.status != 'completed'])
        low = len([t for t in tasks if t.priority == 'low' and t.status != 'completed'])

        return [{
            'type': 'info',
            'icon': 'BarChart3',
            'title': 'Resumo geral',
            'description': (
                f'{len(active_projects)} projeto{"s" if len(active_projects) != 1 else ""} ativo{"s" if len(active_projects) != 1 else ""}, '
                f'{len(active_members)} membro{"s" if len(active_members) != 1 else ""} disponível{"is" if len(active_members) != 1 else ""}, '
                f'{total_tasks} tarefas no total. '
                f'Pendentes por prioridade: {high} alta, {medium} média, {low} baixa.'
            )
        }]
