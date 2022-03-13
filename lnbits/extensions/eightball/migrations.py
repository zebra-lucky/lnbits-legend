async def m001_initial(db):
    """
    Initial eightball tables.
    """
    await db.execute(
        f"""
        CREATE TABLE eightball.games (
            id {db.serial_primary_key},
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            wallet TEXT NOT NULL,
            image TEXT, -- image/png;base64,...
            enabled BOOLEAN NOT NULL DEFAULT true,
            price INTEGER NOT NULL,
            unit TEXT NOT NULL DEFAULT 'sat',
            wordlist TEXT
        );
        """
    )
