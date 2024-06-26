import aiosqlite
import aiomysql
import warnings

warnings.filterwarnings("ignore", category=aiomysql.Warning, message="Table '.*' already exists")

async def check_tables(self):

    async with self.pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await conn.commit()

            await cursor.execute("""
            CREATE TABLE IF NOT EXISTS guilds (
                GuildId INT PRIMARY KEY AUTO_INCREMENT,
                GuildName VARCHAR(255),
                GuildDescription TEXT,
                GuildLevel INT,
                GuildBoosts INT,
                GuildMembers INT,
                OwnerId INT,
                CommandCooldown INT DEFAULT 30
            )
            """)

            await cursor.execute("""
            CREATE TABLE IF NOT EXISTS guild_members (
                MembershipId INT PRIMARY KEY AUTO_INCREMENT,
                GuildName TEXT,
                GuildID INT,
                MemberID INT,
                PrimaryID INT
            )
            """)

            await cursor.execute("""
            CREATE TABLE IF NOT EXISTS guild_invites (
                InviteId INT PRIMARY KEY AUTO_INCREMENT,
                GuildId INT,
                MessageId INT
            )
            """)

            await cursor.execute("""
            CREATE TABLE IF NOT EXISTS profiles (
                ProfileId INT PRIMARY KEY AUTO_INCREMENT,
                UserId INT,
                DisplayName TEXT,
                Description TEXT,
                Status TEXT,
                DisplayPicture TEXT,
                Thumbnail TEXT,
                embedColor TEXT
            )
            """)

            await cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventories (
                InvId INT PRIMARY KEY AUTO_INCREMENT,
                UserId INT,
                Items TEXT DEFAULT '{}'
            )
            """)

            await cursor.execute("""
            CREATE TABLE IF NOT EXISTS dimensions (
                DimId INT PRIMARY KEY AUTO_INCREMENT,
                DimName TEXT,
                Blocks TEXT DEFAULT '{}',
                Mobs TEXT DEFAULT '{}'
            )
            """)

            await cursor.execute("""
            CREATE TABLE IF NOT EXISTS wallets (
                WalletId INT PRIMARY KEY AUTO_INCREMENT,
                UserId INT,
                Coins INT DEFAULT 0
            )
            """)

            await cursor.execute("""
            CREATE TABLE IF NOT EXISTS shop (
                ItemId INT PRIMARY KEY AUTO_INCREMENT,
                ItemName TEXT,
                SafeName TEXT,
                Cost INT
            )
            """)

            await cursor.execute("""
            CREATE TABLE IF NOT EXISTS items (
                ItemId INT PRIMARY KEY AUTO_INCREMENT,
                ItemName TEXT,
                SellValue INT DEFAULT 0,
                CanSell INT DEFAULT 0,
                CostValue INT DEFAULT 0,
                CanBuy INT DEFAULT 0,
                CanSmelt INT DEFAULT 0,
                HarvestLevel INT DEFAULT 0,
                Emoji TEXT DEFAULT ''
            )
            """)

            await conn.commit()

    return
    # Guilds
    async with aiosqlite.connect('guilds.db') as db:
        # Creates the "guilds" table
        await db.execute("""
        CREATE TABLE IF NOT EXISTS guilds (
            GuildId INTEGER PRIMARY KEY AUTOINCREMENT,
            GuildName STRING,
            GuildDescription STRING,
            GuildLevel INTEGER,
            GuildBoosts INTEGER,
            GuildMembers INTEGER,
            OwnerId INTEGER,
            CommandCooldown INTEGER DEFAULT 30
        )
        """)

        # Creates the "guild_members" table
        await db.execute("""
        CREATE TABLE IF NOT EXISTS guild_members (
            MembershipId INTEGER PRIMARY KEY AUTOINCREMENT,
            GuildName STRING,
            GuildID INTEGER,
            MemberID INTEGER,
            PrimaryID INTEGER
        )
        """)

        # Creates the "guild_invites" table
        await db.execute("""
        CREATE TABLE IF NOT EXISTS guild_invites (
            InviteId INTEGER PRIMARY KEY AUTOINCREMENT,
            GuildId INTEGER,
            MessageId INTEGER
        )
        """)

        # Creates the "profiles" table
        await db.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            ProfileId INTEGER PRIMARY KEY AUTOINCREMENT,
            UserId INTEGER,
            DisplayName STRING,
            Description STRING,
            Status STRING,
            DisplayPicture STRING,
            Thumbnail STRING,
            embedColor STRING
        )
        """)
        await db.commit()

    # Quacky
    async with aiosqlite.connect('quacky.db') as db:
        # Creates the "inventories" table
        await db.execute("""
        CREATE TABLE IF NOT EXISTS inventories (
            InvId INTEGER PRIMARY KEY AUTOINCREMENT,
            UserId INTEGER,
            Items TEXT DEFAULT '{}'
        )
        """)

        # Creates the "dimensions" table
        await db.execute("""
        CREATE TABLE IF NOT EXISTS dimensions (
            DimId INTEGER PRIMARY KEY AUTOINCREMENT,
            DimName TEXT,
            Blocks TEXT DEFAULT '{}',
            Mobs TEXT DEFAULT '{}'
        )
        """)

        # Creates the "wallets" table
        await db.execute("""
        CREATE TABLE IF NOT EXISTS wallets (
            WalletId INTEGER PRIMARY KEY AUTOINCREMENT,
            UserId INTEGER,
            Coins INTEGER DEFAULT 0
        )
        """)

        # Creates the "shop" table
        await db.execute("""
        CREATE TABLE IF NOT EXISTS shop (
            ItemId INTEGER PRIMARY KEY AUTOINCREMENT,
            ItemName STRING,
            SafeName STRING,
            Cost INTEGER
        )
        """)

        # Crates the "items" table
        await db.execute("""
        CREATE TABLE IF NOT EXISTS items (
            ItemId INTEGER PRIMARY KEY AUTOINCREMENT,
            ItemName STRING,
            SellValue INTEGER DEFAULT 0,
            CanSell INTEGER DEFAULT 0,
            CostValue INTEGER DEFAULT 0,
            CanBuy INTEGER DEFAULT 0,
            CanSmelt INTEGER DEFAULT 0,
            HarvestLevel INTEGER DEFAULT 0,
            Emoji STRING DEFAULT ''
        )
        """)
        await db.commit()