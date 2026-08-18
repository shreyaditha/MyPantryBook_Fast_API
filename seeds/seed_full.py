"""
Seed script — loads south_indian_recipes_seed.json into the app database.
Maps the JSON schema to the actual app models.

Usage:
    cd c:\\Users\\lenov\\OneDrive\\shreya\\Projects\\fast_api_pantry
    python -m seeds.seed_full
"""
import asyncio
import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal, engine, Base
from app.models.user import User          # noqa: F401 — needed for relationship resolution
from app.models.notification import Notification  # noqa: F401
from app.models.pantry import PantryItem  # noqa: F401
from app.models.recipe import Recipe, RecipeIngredient
from app.models.ingredient import Ingredient


# Guess ingredient category from its name
CATEGORY_MAP = {
    "dal": "lentil", "urad": "lentil", "toor": "lentil", "moong": "lentil",
    "chana": "lentil",
    "rice": "grain", "semolina": "grain", "rava": "grain", "vermicelli": "grain",
    "flour": "grain",
    "onion": "veg", "tomato": "veg", "potato": "veg", "carrot": "veg",
    "beans": "veg", "cabbage": "veg", "brinjal": "veg", "drumstick": "veg",
    "peas": "veg", "lemon": "veg", "mixed veg": "veg",
    "pepper": "spice", "chilli": "spice", "mustard": "spice", "cumin": "spice",
    "turmeric": "spice", "coriander": "spice", "fenugreek": "spice",
    "cardamom": "spice", "asafoetida": "spice", "fennel": "spice",
    "tamarind": "spice", "sambar powder": "spice", "rasam powder": "spice",
    "salt": "spice", "jaggery": "spice", "curry leaves": "spice",
    "ginger": "spice", "garlic": "spice",
    "ghee": "oil", "oil": "oil", "coconut oil": "oil",
    "coconut milk": "dairy", "curd": "dairy", "yogurt": "dairy",
    "milk": "dairy",
    "chicken": "other", "fish": "other", "mutton": "other",
    "cashew": "other", "raisins": "other", "peanuts": "other",
    "sugar": "other",
}


def guess_category(name: str) -> str:
    name_lower = name.lower()
    for key, cat in CATEGORY_MAP.items():
        if key in name_lower:
            return cat
    return "other"


# Normalise a unit string from the JSON to what the model uses
def normalise_unit(unit: str) -> str:
    mapping = {
        "cup": "cups", "cups": "cups",
        "tsp": "tsp", "tbsp": "tbsp",
        "piece": "pieces", "pieces": "pieces",
        "pinch": "tsp",
        "clove": "pieces", "cloves": "pieces",
        "stick": "pieces", "g": "grams", "grams": "grams",
        "ml": "ml",
    }
    return mapping.get(unit.lower().strip(), unit.lower().strip())


async def seed(session: AsyncSession, recipes_data: list[dict]) -> None:
    ingredient_cache: dict[str, Ingredient] = {}

    for r in recipes_data:
        # Skip if recipe with same title already exists
        existing = await session.execute(
            select(Recipe).where(Recipe.title == r["name"])
        )
        if existing.scalar_one_or_none():
            print(f"  [SKIP] {r['name']} — already exists")
            continue

        instructions_json = json.dumps(r["instructions"])
        description = (
            f"{r['region']} recipe · {'Vegetarian' if r['is_vegetarian'] else 'Non-vegetarian'} · "
            f"Tags: {', '.join(r['tags'])}"
        )

        recipe = Recipe(
            title=r["name"],
            description=description,
            cuisine=r["cuisine"],
            prep_time_minutes=r["prep_time_minutes"] + r["cook_time_minutes"],
            servings=r["servings"],
            difficulty=r["difficulty"],
            instructions=instructions_json,
        )
        session.add(recipe)
        await session.flush()  # get recipe.id

        for ing_data in r["ingredients"]:
            name = ing_data["name"].strip()
            unit = normalise_unit(str(ing_data["unit"]))

            # Check cache first
            ingredient = ingredient_cache.get(name)
            if ingredient is None:
                result = await session.execute(
                    select(Ingredient).where(Ingredient.name == name)
                )
                ingredient = result.scalar_one_or_none()
                if ingredient is None:
                    ingredient = Ingredient(
                        name=name,
                        unit=unit,
                        category=guess_category(name),
                    )
                    session.add(ingredient)
                    await session.flush()
                ingredient_cache[name] = ingredient

            session.add(RecipeIngredient(
                recipe_id=recipe.id,
                ingredient_id=ingredient.id,
                quantity_needed=float(ing_data["quantity"]),
                unit=unit,
            ))

        print(f"  [OK]   {r['name']}")

    await session.commit()


async def main():
    json_path = Path(__file__).parent / "south_indian_recipes_seed.json"
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)
    recipes = data["recipes"]
    print(f"Loaded {len(recipes)} recipes from JSON\n")

    async with AsyncSessionLocal() as session:
        await seed(session, recipes)

    print(f"\nDone — {len(recipes)} recipes processed.")


if __name__ == "__main__":
    asyncio.run(main())
