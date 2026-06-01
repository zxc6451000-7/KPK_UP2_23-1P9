from datetime import datetime
from peewee import (
    SqliteDatabase, Model, AutoField, IntegerField, CharField,
    BooleanField, DateTimeField, Check, ForeignKeyField
)

db = SqliteDatabase('curriculum_plan.db')


class BaseModel(Model):
    class Meta:
        database = db


class Specialty(BaseModel):
    """Внешняя сущность: специальность (заглушка, управляется Specialty Service)"""
    id = AutoField(primary_key=True)
    name = CharField(max_length=200)

    class Meta:
        table_name = 'specialties'


class Discipline(BaseModel):
    """Внешняя сущность: дисциплина (заглушка, управляется Discipline Service)"""
    id = AutoField(primary_key=True)
    name = CharField(max_length=200)

    class Meta:
        table_name = 'disciplines'


class CurriculumPlan(BaseModel):
    """Основная сущность: запись учебного плана."""
    id = AutoField(primary_key=True)
    specialty = ForeignKeyField(Specialty, backref='plans', on_delete='RESTRICT')
    discipline = ForeignKeyField(Discipline, backref='plans', on_delete='RESTRICT')
    semester = IntegerField(constraints=[Check('semester >= 1 AND semester <= 12')])
    theory_hours = IntegerField(constraints=[Check('theory_hours >= 0')])
    practice_hours = IntegerField(constraints=[Check('practice_hours >= 0')])
    total_hours = IntegerField(constraints=[Check('total_hours >= 0')])
    assessment_type = CharField(max_length=20, constraints=[
        Check("assessment_type IN ('exam', 'credit', 'graded_credit')")
    ])
    year = IntegerField(constraints=[Check('year >= 2000')])
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    class Meta:
        table_name = 'curriculum_plans'
        # Уникальность по (specialty, discipline, semester, year)
        indexes = (
            (('specialty', 'discipline', 'semester', 'year'), True),
        )

    def save(self, *args, **kwargs):
        self.total_hours = self.theory_hours + self.practice_hours
        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)

    @classmethod
    def soft_delete(cls, plan_id):
        """Мягкое удаление: is_active = False. Возвращает True если деактивировано, иначе False."""
        updated = cls.update(is_active=False).where(
            (cls.id == plan_id) & (cls.is_active == True)
        ).execute()
        return updated > 0

    @classmethod
    def get_by_id(cls, plan_id):
        """Получить запись по ID (только активные)."""
        return cls.select().where((cls.id == plan_id) & (cls.is_active == True)).first()

    @classmethod
    def get_list(cls, specialty_id=None, discipline_id=None, semester=None,
                 year=None, assessment_type=None, is_active=True,offset=0):
        """Получить список записей по фильтрам."""
        query = cls.select().where(cls.is_active == is_active)

        if specialty_id is not None:
            query = query.where(cls.specialty == specialty_id)
        if discipline_id is not None:
            query = query.where(cls.discipline == discipline_id)
        if semester is not None:
            query = query.where(cls.semester == semester)
        if year is not None:
            query = query.where(cls.year == year)
        if assessment_type is not None:
            query = query.where(cls.assessment_type == assessment_type)

        return query.limit(limit).offset(offset)

    @classmethod
    def update_plan(cls, plan_id, theory_hours=None, practice_hours=None, assessment_type=None):
        """Обновление записи (только разрешённые поля)."""
        data = {}
        if theory_hours is not None:
            data['theory_hours'] = theory_hours
        if practice_hours is not None:
            data['practice_hours'] = practice_hours
        if assessment_type is not None:
            data['assessment_type'] = assessment_type

        if not data:
            return None

        # Обновляем и пересчитываем total_hours
        plan = cls.get_by_id(plan_id)
        if not plan:
            return None

        if theory_hours is not None:
            plan.theory_hours = theory_hours
        if practice_hours is not None:
            plan.practice_hours = practice_hours
        plan.total_hours = plan.theory_hours + plan.practice_hours

        if assessment_type is not None:
            plan.assessment_type = assessment_type

        plan.updated_at = datetime.now()
        plan.save()
        return plan


def init_db():
    """Создание таблиц и заполнение начальными данными"""
    db.connect()
    db.create_tables([Specialty, Discipline, CurriculumPlan], safe=True)

if __name__ == '__main__':
    init_db()
    print("База данных curriculum_plan.db успешно инициализирована.")