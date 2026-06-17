import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from config import settings
from models import User, Post

async def seed_posts_for_existing_user():
    print("🚀 Connecting to cloud database...")
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        # 1. Search for your existing user profile by email
        print("🔍 Searching for your user profile (praveen107487@gmail.com)...")
        result = await session.execute(
            select(User).where(User.email == "praveen107487@gmail.com")
        )
        existing_user = result.scalar_one_or_none()

        if not existing_user:
            print("❌ Error: Could not find a user with that email in the cloud database.")
            print("💡 please make sure you registered the account on your live website first!")
            await engine.dispose()
            return

        print(f"🎉 Found User: {existing_user.username} (ID: {existing_user.id})")

        # 2. Check if posts already exist so we don't duplicate them
        check_posts = await session.execute(
            select(Post).where(Post.user_id == existing_user.id)
        )
        if check_posts.scalars().first():
            print("💡 You already have posts in the database. Skipping seeding to prevent duplicates.")
            await engine.dispose()
            return

        # 3. Add the sample posts linked directly to your account
        async with session.begin():
            post1 = Post(
                title="My First Live Blog Post!",
                content="Hello World! This post was generated via an async seeding script and attached directly to my user account profile.",
                user_id=existing_user.id
            )
            post2 = Post(
                title="FastAPI + Render Cloud Pipeline",
                content="Successfully deployed my asynchronous backend app to Render using an automated Git integration pipeline. Database tables managed via Alembic revisions.",
                user_id=existing_user.id
            )
            session.add_all([post1, post2])
            print("✅ 2 sample blog posts staged for your profile.")

    print("🎉 Database successfully updated! Your feed will now be populated.")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(seed_posts_for_existing_user())