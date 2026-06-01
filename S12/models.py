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


def init_db():
    """Создание таблиц и заполнение начальными данными"""
    db.connect()
    db.create_tables([Specialty, Discipline, CurriculumPlan], safe=True)

    if not Specialty.select().exists():
        sp = Specialty.create(name='Информационные системы и программирование')
        d1 = Discipline.create(name='Математика')
        d2 = Discipline.create(name='МДК 01.01 Разработка программных модулей')

        CurriculumPlan.create(
            specialty=sp,
            discipline=d1,
            semester=1,
            theory_hours=48,
            practice_hours=32,
            assessment_type='exam',
            year=2024
        )
        CurriculumPlan.create(
            specialty=sp,
            discipline=d2,
            semester=2,
            theory_hours=30,
            practice_hours=60,
            assessment_type='graded_credit',
            year=2024
        )


if __name__ == '__main__':
    init_db()
    print("База данных curriculum_plan.db успешно инициализирована.")
