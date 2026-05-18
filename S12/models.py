from peewee import SqliteDatabase, Model, IntegerField, CharField

db = SqliteDatabase('curriculum_plans.db')


class CurriculumPlan(Model):
    """Модель учебного плана (без NULL-полей)"""
    discipline_id = IntegerField(null=False, verbose_name="ID дисциплины")
    specialty_id = IntegerField(null=False, verbose_name="ID специальности")
    semester = IntegerField(null=False, verbose_name="Семестр")
    theory_hours = IntegerField(null=False, verbose_name="Теоретические часы")
    practice_hours = IntegerField(null=False, verbose_name="Практические часы")
    total_hours = IntegerField(null=False, verbose_name="Всего часов")
    assessment_form = CharField(max_length=20, null=False, verbose_name="Форма отчетности")

    class Meta:
        database = db
        table_name = 'curriculum_plans'


def init_db():
    """Инициализация БД"""
    db.connect()
    db.create_tables([CurriculumPlan], safe=True)
    db.close()


# Точка входа для инициализации БД
if __name__ == "__main__":
    init_db()
    print("База данных curriculum_plans.db успешно создана")