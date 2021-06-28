from sqlalchemy.exc import OperationalError  # type: ignore


async def m001_initial(db):
    """
    Initial admin table.
    """
    await db.execute(
        """
        CREATE TABLE IF NOT EXISTS admin (
            id TEXT PRIMARY KEY
        );
    """
    )