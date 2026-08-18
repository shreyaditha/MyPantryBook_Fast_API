import json
from pathlib import Path
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_tables():
    """Create all tables and auto-seed initial recipes if empty."""
    async with engine.begin() as conn:
        from app.models import user, ingredient, pantry, recipe, notification  # noqa: F401
        await conn.run_sync(Base.metadata.create_all)

    # Auto-seed recipes if database has no recipes (e.g. on fresh Vercel container startup)
    try:
        from app.models.recipe import Recipe
        async with AsyncSessionLocal() as session:
            res = await session.execute(select(func.count(Recipe.id)))
            count = res.scalar() or 0
            if count == 0:
                json_path = Path(__file__).resolve().parent.parent.parent / "seeds" / "south_indian_recipes_seed.json"
                if json_path.exists():
                    from seeds.seed_full import seed
                    with open(json_path, encoding="utf-8") as f:
                        data = json.load(f)
                    await seed(session, data.get("recipes", []))
    except Exception as e:
        print(f"[Auto-seed Warning] {e}")
