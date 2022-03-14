async def m001_initial(db):
    """
    Initial eightball tables.
    """
    await db.execute(
        f"""
        CREATE TABLE eightball.games (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            user TEXT NOT NULL,
            wallet TEXT NOT NULL,
            price INTEGER NOT NULL,
            wordlist TEXT
        );
        """
    )
