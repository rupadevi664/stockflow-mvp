
import pymysql
from app.core.config import settings


def test_mysql_connection():
    connection = pymysql.connect(
        host=settings.DATABASE_HOST,
        port=settings.DATABASE_PORT,
        user=settings.DATABASE_USER,
        password=settings.DATABASE_PASSWORD,
        database=settings.DATABASE_NAME
    )

    assert connection.open is True

    connection.close()
