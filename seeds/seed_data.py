"""
Seed script: South Indian recipes + ingredients + demo user.
Run with: python -m seeds.seed_data
"""
import asyncio
import json
import sys
import os

# Make sure we can import from app/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from app.core.database import AsyncSessionLocal, create_tables
from app.models.user import User
from app.models.ingredient import Ingredient
from app.models.recipe import Recipe, RecipeIngredient

# ── Ingredient master list ────────────────────────────────────────────────────
INGREDIENTS = [
    # Grains
    {"name": "Idli Rice", "unit": "grams", "category": "grain"},
    {"name": "Parboiled Rice", "unit": "grams", "category": "grain"},
    {"name": "Raw Rice", "unit": "grams", "category": "grain"},
    {"name": "Urad Dal", "unit": "grams", "category": "lentil"},
    {"name": "Chana Dal", "unit": "grams", "category": "lentil"},
    {"name": "Toor Dal", "unit": "grams", "category": "lentil"},
    {"name": "Moong Dal", "unit": "grams", "category": "lentil"},
    {"name": "Rava (Semolina)", "unit": "grams", "category": "grain"},
    {"name": "Flattened Rice (Poha)", "unit": "grams", "category": "grain"},
    # Vegetables
    {"name": "Tomato", "unit": "pieces", "category": "veg"},
    {"name": "Onion", "unit": "pieces", "category": "veg"},
    {"name": "Drumstick (Murungakkai)", "unit": "pieces", "category": "veg"},
    {"name": "Small Eggplant", "unit": "pieces", "category": "veg"},
    {"name": "Green Banana", "unit": "pieces", "category": "veg"},
    {"name": "Potato", "unit": "pieces", "category": "veg"},
    {"name": "Curry Leaves", "unit": "grams", "category": "veg"},
    {"name": "Coriander Leaves", "unit": "grams", "category": "veg"},
    {"name": "Green Chili", "unit": "pieces", "category": "veg"},
    {"name": "Ginger", "unit": "grams", "category": "veg"},
    {"name": "Garlic", "unit": "pieces", "category": "veg"},
    # Spices
    {"name": "Mustard Seeds", "unit": "tsp", "category": "spice"},
    {"name": "Cumin Seeds", "unit": "tsp", "category": "spice"},
    {"name": "Dried Red Chili", "unit": "pieces", "category": "spice"},
    {"name": "Turmeric Powder", "unit": "tsp", "category": "spice"},
    {"name": "Red Chili Powder", "unit": "tsp", "category": "spice"},
    {"name": "Coriander Powder", "unit": "tsp", "category": "spice"},
    {"name": "Black Pepper", "unit": "tsp", "category": "spice"},
    {"name": "Asafoetida (Hing)", "unit": "tsp", "category": "spice"},
    {"name": "Sambar Powder", "unit": "tbsp", "category": "spice"},
    {"name": "Rasam Powder", "unit": "tsp", "category": "spice"},
    {"name": "Fenugreek Seeds", "unit": "tsp", "category": "spice"},
    {"name": "Curry Powder", "unit": "tsp", "category": "spice"},
    # Dairy / Coconut
    {"name": "Fresh Coconut", "unit": "grams", "category": "dairy"},
    {"name": "Coconut Milk", "unit": "ml", "category": "dairy"},
    {"name": "Yogurt (Curd)", "unit": "grams", "category": "dairy"},
    {"name": "Ghee", "unit": "tbsp", "category": "dairy"},
    # Other
    {"name": "Tamarind", "unit": "grams", "category": "other"},
    {"name": "Jaggery", "unit": "grams", "category": "other"},
    {"name": "Salt", "unit": "tsp", "category": "other"},
    {"name": "Oil", "unit": "tbsp", "category": "oil"},
    {"name": "Water", "unit": "ml", "category": "other"},
    {"name": "Cashews", "unit": "grams", "category": "other"},
    {"name": "Raisins", "unit": "grams", "category": "other"},
]

# ── Recipe definitions ────────────────────────────────────────────────────────
RECIPES = [
    {
        "title": "Soft Idli",
        "description": "Fluffy steamed rice cakes — the ultimate South Indian breakfast. Soft, pillowy, and perfect with sambar and chutney.",
        "cuisine": "South Indian",
        "prep_time_minutes": 30,
        "servings": 4,
        "difficulty": "medium",
        "instructions": [
            "Wash and soak idli rice and urad dal separately for 6 hours.",
            "Grind urad dal first to a smooth, fluffy batter, then grind rice to a slightly coarse texture.",
            "Mix both batters together, add salt, and ferment overnight (8-10 hours) in a warm place.",
            "Grease idli moulds with a little oil.",
            "Pour batter into moulds and steam for 12-15 minutes on medium heat.",
            "Insert a toothpick — if it comes out clean, the idlis are done.",
            "Let cool for 2 minutes, then gently scoop out with a wet spoon.",
            "Serve hot with sambar and coconut chutney.",
        ],
        "ingredients": [
            ("Idli Rice", 400, "grams"),
            ("Urad Dal", 130, "grams"),
            ("Salt", 2, "tsp"),
            ("Water", 400, "ml"),
        ],
    },
    {
        "title": "Crispy Masala Dosa",
        "description": "Golden, lacy crepes filled with a spiced potato filling. The crown jewel of South Indian breakfasts.",
        "cuisine": "South Indian",
        "prep_time_minutes": 45,
        "servings": 4,
        "difficulty": "medium",
        "instructions": [
            "Prepare dosa batter: soak raw rice and urad dal for 6 hours, then grind and ferment overnight.",
            "For the potato filling: boil and mash potatoes. Heat oil, add mustard seeds and let them splutter.",
            "Add curry leaves, dried red chili, onion and sauté until translucent.",
            "Add turmeric and mashed potatoes. Mix well and season with salt. Set aside.",
            "Heat a flat tawa or griddle. Pour a ladle of batter in the center and spread in circular motion.",
            "Drizzle oil around the edges. Cook until golden and crisp on the bottom.",
            "Place potato filling on one half, fold the dosa over it.",
            "Serve immediately with coconut chutney and sambar.",
        ],
        "ingredients": [
            ("Raw Rice", 300, "grams"),
            ("Urad Dal", 100, "grams"),
            ("Potato", 3, "pieces"),
            ("Onion", 1, "pieces"),
            ("Mustard Seeds", 1, "tsp"),
            ("Curry Leaves", 5, "grams"),
            ("Turmeric Powder", 0.5, "tsp"),
            ("Green Chili", 2, "pieces"),
            ("Oil", 3, "tbsp"),
            ("Salt", 2, "tsp"),
        ],
    },
    {
        "title": "Toor Dal Sambar",
        "description": "A rich, tangy lentil and vegetable stew flavored with tamarind and homemade sambar powder. The soul of South Indian cooking.",
        "cuisine": "South Indian",
        "prep_time_minutes": 40,
        "servings": 6,
        "difficulty": "medium",
        "instructions": [
            "Pressure cook toor dal with turmeric until completely soft.",
            "Soak tamarind in warm water and extract the pulp.",
            "In a large pot, heat oil and add mustard seeds, dried red chili, and curry leaves.",
            "Add onion and tomato. Sauté for 5 minutes.",
            "Add drumstick pieces and cook for 3 minutes.",
            "Pour in tamarind water and bring to a boil.",
            "Add sambar powder, red chili powder, and cooked dal. Simmer for 15 minutes.",
            "Adjust salt and consistency. Finish with a pinch of asafoetida.",
            "Garnish with coriander leaves and serve hot with idli or rice.",
        ],
        "ingredients": [
            ("Toor Dal", 200, "grams"),
            ("Drumstick (Murungakkai)", 2, "pieces"),
            ("Tomato", 2, "pieces"),
            ("Onion", 1, "pieces"),
            ("Tamarind", 30, "grams"),
            ("Sambar Powder", 2, "tbsp"),
            ("Turmeric Powder", 0.5, "tsp"),
            ("Red Chili Powder", 1, "tsp"),
            ("Mustard Seeds", 1, "tsp"),
            ("Dried Red Chili", 2, "pieces"),
            ("Curry Leaves", 5, "grams"),
            ("Asafoetida (Hing)", 0.25, "tsp"),
            ("Oil", 2, "tbsp"),
            ("Salt", 2, "tsp"),
            ("Coriander Leaves", 10, "grams"),
        ],
    },
    {
        "title": "Pepper Rasam",
        "description": "A thin, fiery tomato-tamarind soup with black pepper and cumin. Perfect for cold days and clearing sinuses.",
        "cuisine": "South Indian",
        "prep_time_minutes": 25,
        "servings": 4,
        "difficulty": "easy",
        "instructions": [
            "Soak tamarind in 1 cup warm water and extract thick pulp.",
            "Coarsely crush black pepper and cumin seeds together.",
            "Pressure cook tomatoes and toor dal until soft. Mash together.",
            "In a pot, heat the tamarind water with tomato-dal mixture.",
            "Add rasam powder, crushed pepper-cumin, turmeric, and salt.",
            "Bring to a boil and simmer 10 minutes until fragrant.",
            "In a small pan, heat ghee. Add mustard seeds, dried red chili, and curry leaves.",
            "Pour the tempering over the rasam.",
            "Serve as soup or mixed into rice with a drizzle of ghee.",
        ],
        "ingredients": [
            ("Toor Dal", 50, "grams"),
            ("Tomato", 3, "pieces"),
            ("Tamarind", 20, "grams"),
            ("Black Pepper", 1.5, "tsp"),
            ("Cumin Seeds", 1, "tsp"),
            ("Rasam Powder", 2, "tsp"),
            ("Turmeric Powder", 0.25, "tsp"),
            ("Mustard Seeds", 0.5, "tsp"),
            ("Dried Red Chili", 2, "pieces"),
            ("Curry Leaves", 5, "grams"),
            ("Ghee", 1, "tbsp"),
            ("Asafoetida (Hing)", 0.25, "tsp"),
            ("Salt", 1.5, "tsp"),
            ("Coriander Leaves", 10, "grams"),
        ],
    },
    {
        "title": "Ven Pongal",
        "description": "Creamy, comforting rice and moong dal porridge flavored with black pepper, cumin, ginger, and generous ghee. A temple classic.",
        "cuisine": "South Indian",
        "prep_time_minutes": 30,
        "servings": 4,
        "difficulty": "easy",
        "instructions": [
            "Dry roast moong dal until it turns light golden and smells nutty. Set aside.",
            "Wash raw rice and combine with the roasted moong dal.",
            "Add 5 cups water and pressure cook for 4-5 whistles until very soft and mushy.",
            "Meanwhile, heat ghee in a pan. Add cumin seeds and let them sizzle.",
            "Add whole black peppercorns, ginger, curry leaves, cashews, and raisins.",
            "Fry until cashews are golden.",
            "Add this tempering to the cooked rice-dal mixture. Mix vigorously.",
            "Season with salt. The pongal should be loose and creamy.",
            "Serve hot with sambar, chutney, and extra ghee on top.",
        ],
        "ingredients": [
            ("Raw Rice", 200, "grams"),
            ("Moong Dal", 100, "grams"),
            ("Ghee", 3, "tbsp"),
            ("Cumin Seeds", 1, "tsp"),
            ("Black Pepper", 1.5, "tsp"),
            ("Ginger", 15, "grams"),
            ("Curry Leaves", 8, "grams"),
            ("Cashews", 30, "grams"),
            ("Raisins", 20, "grams"),
            ("Salt", 1.5, "tsp"),
            ("Water", 1200, "ml"),
        ],
    },
    {
        "title": "Crispy Medu Vada",
        "description": "Savory doughnut-shaped fritters made from urad dal batter. Crispy on the outside, soft inside — the perfect accompaniment to sambar.",
        "cuisine": "South Indian",
        "prep_time_minutes": 45,
        "servings": 4,
        "difficulty": "hard",
        "instructions": [
            "Soak urad dal for 4-6 hours. Drain completely.",
            "Grind to a thick, smooth batter using as little water as possible.",
            "Add salt, black pepper, cumin seeds, green chili, ginger, and curry leaves to the batter.",
            "Beat the batter vigorously with your hand for 5 minutes to make it light and airy.",
            "Heat oil for deep frying to 180°C.",
            "Wet your hands. Take a portion of batter, shape into a ring with a hole in the center.",
            "Gently slide into hot oil. Fry until golden and crisp, turning once (4-5 minutes per batch).",
            "Drain on kitchen paper.",
            "Serve immediately with sambar and coconut chutney.",
        ],
        "ingredients": [
            ("Urad Dal", 250, "grams"),
            ("Green Chili", 2, "pieces"),
            ("Ginger", 10, "grams"),
            ("Curry Leaves", 5, "grams"),
            ("Black Pepper", 1, "tsp"),
            ("Cumin Seeds", 1, "tsp"),
            ("Asafoetida (Hing)", 0.25, "tsp"),
            ("Salt", 1, "tsp"),
            ("Oil", 500, "ml"),
        ],
    },
    {
        "title": "Coconut Chutney",
        "description": "The universal South Indian condiment — smooth, cool coconut chutney with a sputtering mustard and curry leaf tempering.",
        "cuisine": "South Indian",
        "prep_time_minutes": 15,
        "servings": 4,
        "difficulty": "easy",
        "instructions": [
            "Grate or chop fresh coconut.",
            "Add coconut, green chili, ginger, roasted chana dal, and salt to a blender.",
            "Blend with a little water to a smooth paste.",
            "Transfer to a bowl. Taste and adjust salt.",
            "For tempering: heat oil in a small pan, add mustard seeds.",
            "Once they splutter, add dried red chili and curry leaves.",
            "Pour the tempering immediately over the chutney.",
            "Serve with idli, dosa, or vada.",
        ],
        "ingredients": [
            ("Fresh Coconut", 150, "grams"),
            ("Green Chili", 2, "pieces"),
            ("Ginger", 5, "grams"),
            ("Chana Dal", 30, "grams"),
            ("Mustard Seeds", 0.5, "tsp"),
            ("Dried Red Chili", 1, "pieces"),
            ("Curry Leaves", 5, "grams"),
            ("Oil", 1, "tbsp"),
            ("Salt", 1, "tsp"),
        ],
    },
    {
        "title": "Tamarind Rice (Puliyodarai)",
        "description": "Tangy, spicy tamarind-coated rice with roasted peanuts and a complex spice tempering. A temple offering turned everyday favorite.",
        "cuisine": "Tamil",
        "prep_time_minutes": 60,
        "servings": 4,
        "difficulty": "medium",
        "instructions": [
            "Cook raw rice until each grain is separate. Spread and cool.",
            "Soak tamarind in 2 cups hot water and extract thick pulp.",
            "Heat oil in a heavy pan. Add mustard seeds, chana dal, and urad dal.",
            "Add dried red chili, curry leaves, and peanuts. Fry until peanuts are golden.",
            "Add tamarind pulp and cook on medium-low heat until thick (15-20 minutes), stirring often.",
            "Add red chili powder, turmeric, sambar powder, jaggery, and salt. Cook 5 more minutes.",
            "The paste should be thick enough to coat the back of a spoon.",
            "Mix the paste into cooled rice gradually until every grain is coated.",
            "Serve at room temperature or warmed slightly. Keeps well for 2-3 days.",
        ],
        "ingredients": [
            ("Raw Rice", 300, "grams"),
            ("Tamarind", 60, "grams"),
            ("Mustard Seeds", 1, "tsp"),
            ("Chana Dal", 20, "grams"),
            ("Urad Dal", 10, "grams"),
            ("Dried Red Chili", 4, "pieces"),
            ("Curry Leaves", 8, "grams"),
            ("Red Chili Powder", 1.5, "tsp"),
            ("Turmeric Powder", 0.5, "tsp"),
            ("Sambar Powder", 1, "tbsp"),
            ("Jaggery", 10, "grams"),
            ("Oil", 4, "tbsp"),
            ("Salt", 2, "tsp"),
            ("Asafoetida (Hing)", 0.25, "tsp"),
        ],
    },
]


async def seed():
    await create_tables()
    async with AsyncSessionLocal() as db:
        # ── Create demo user ──────────────────────────────────────────────────
        existing_user = await db.execute(select(User).where(User.id == 1))
        if not existing_user.scalar_one_or_none():
            demo_user = User(
                id=1,
                username="cook",
                email="cook@mypantrybook.local",
                hashed_password="demo_no_auth",
            )
            db.add(demo_user)
            await db.flush()
            print("✅ Created demo user")
        else:
            print("ℹ️  Demo user already exists")

        # ── Create ingredients ────────────────────────────────────────────────
        ing_map = {}  # name -> Ingredient.id
        for ing_data in INGREDIENTS:
            existing = await db.execute(select(Ingredient).where(Ingredient.name == ing_data["name"]))
            existing_ing = existing.scalar_one_or_none()
            if existing_ing:
                ing_map[ing_data["name"]] = existing_ing.id
            else:
                ing = Ingredient(**ing_data)
                db.add(ing)
                await db.flush()
                ing_map[ing_data["name"]] = ing.id
                print(f"  🌿 Added ingredient: {ing_data['name']}")

        print(f"✅ {len(ing_map)} ingredients ready")

        # ── Create recipes ────────────────────────────────────────────────────
        created_recipes = 0
        for recipe_data in RECIPES:
            existing_r = await db.execute(select(Recipe).where(Recipe.title == recipe_data["title"]))
            if existing_r.scalar_one_or_none():
                print(f"ℹ️  Recipe already exists: {recipe_data['title']}")
                continue

            recipe = Recipe(
                title=recipe_data["title"],
                description=recipe_data["description"],
                cuisine=recipe_data["cuisine"],
                prep_time_minutes=recipe_data["prep_time_minutes"],
                servings=recipe_data["servings"],
                difficulty=recipe_data["difficulty"],
                instructions=json.dumps(recipe_data["instructions"]),
                created_by=1,
            )
            db.add(recipe)
            await db.flush()

            for ing_name, qty, unit in recipe_data["ingredients"]:
                ing_id = ing_map.get(ing_name)
                if not ing_id:
                    print(f"  ⚠️  Unknown ingredient '{ing_name}' in recipe '{recipe_data['title']}'")
                    continue
                ri = RecipeIngredient(
                    recipe_id=recipe.id,
                    ingredient_id=ing_id,
                    quantity_needed=qty,
                    unit=unit,
                )
                db.add(ri)

            print(f"  📖 Added recipe: {recipe_data['title']}")
            created_recipes += 1

        await db.commit()
        print(f"\n✅ Seed complete! {created_recipes} recipes added.")
        print("🚀 Run the app with: python -m uvicorn app.main:app --reload")


if __name__ == "__main__":
    asyncio.run(seed())
