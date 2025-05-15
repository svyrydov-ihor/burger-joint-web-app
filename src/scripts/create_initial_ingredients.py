import asyncio
from typing import Dict, List
from fastapi import Depends
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.database import AsyncSessionLocal, engine, Base
from src.database.models import Ingredient

initial_ingredients = [{"name": "Bun", "manufacturer": "Top bakery"},
                       {"name": "Beef patty", "manufacturer": "Meet company"},
                       {"name": "Smoked bacon", "manufacturer": "Meet company"},
                       {"name": "American cheese", "manufacturer": "Cheese corporation"},
                       {"name": "Mozzarella cheese", "manufacturer": "Cheese corporation"},
                       {"name": "Tomato slices", "manufacturer": "Great veggies"},
                       {"name": "Shredded lettuce", "manufacturer": "Great veggies"},
                       {"name": "Pickle slices", "manufacturer": "Great veggies"},
                       {"name": "Onions", "manufacturer": "Great veggies"},
                       {"name": "Mushrooms", "manufacturer": "Some company #555"},
                       {"name": "Eggs", "manufacturer": "Some company #555"},
                       {"name": "Ketchup", "manufacturer": "Sauce makers"},
                       {"name": "Mustard", "manufacturer": "Sauce makers"},
                       {"name": "Mayonnaise", "manufacturer": "Sauce makers"},
                       {"name": "Pepper sauce", "manufacturer": "Sauce makers"}]

async def create_initial_ingredients(db: AsyncSession, initial_ingredients: List[Dict[str, str]]) -> None:
    """Deletes all existing ingredients and creates initial ingredients in the database"""
    await db.execute(delete(Ingredient))

    new_ingredient_objs = []
    for item_data in initial_ingredients:
        db_ingredient = Ingredient(name=item_data["name"], manufacturer=item_data["manufacturer"])
        new_ingredient_objs.append(db_ingredient)

    db.add_all(new_ingredient_objs)

    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise

async def run_script():
    async with AsyncSessionLocal() as session:
        await create_initial_ingredients(db=session, initial_ingredients=initial_ingredients)

if __name__ == "__main__":
    asyncio.run(run_script())