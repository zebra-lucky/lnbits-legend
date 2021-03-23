async def m001_initial(db):
    """
    Creates an improved scrambles table and migrates the existing data.
    """
    await db.execute(
        """
        CREATE TABLE IF NOT EXISTS scrambles_game (
            id TEXT PRIMARY KEY,
            wallet TEXT,
            title TEXT,
            top_left TEXT,
            bottom_right TEXT
        );
    """
    )