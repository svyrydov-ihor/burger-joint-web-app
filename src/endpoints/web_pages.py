from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi import status as fastapi_status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from typing import List, Optional
import logging
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.dependencies import get_db_session
from src.services import customer as customer_service
from src.services import burger as burger_service
from src.services import order as order_service
from src.services.ingredient import IngredientService
from src.database.schemes.order import OrderCreate, OrderUpdate, OrderBurgerItemCreate
from src.database.schemes.customer import CustomerCreate, CustomerUpdate
from src.database.schemes.burger import BurgerCreate, BurgerUpdate
from src.database.models.order import OrderStatus
from src.database.crud import order as order_crud

router = APIRouter(
    tags=["Web Pages"],
    default_response_class=HTMLResponse
)

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


# --- Home ---
@router.get("/", name="home")
async def read_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "page_title": "Home"})


# --- Customer Pages ---

# LIST Customers
@router.get("/customers", name="list_customers_page")
async def list_customers_page(request: Request, db: AsyncSession = Depends(get_db_session)):
    customers = await customer_service.CustomerService.get_all_customers(db)
    return templates.TemplateResponse("customers/customer_list.html", {
        "request": request, "page_title": "Customers", "customers": customers
    })


# CREATE Customer (Form Display)
@router.get("/customers/new", name="new_customer_form_page")
async def new_customer_form_page(request: Request):
    return templates.TemplateResponse("customers/customer_form.html", {
        "request": request, "page_title": "New Customer",
        "customer_data": {}, "is_edit_mode": False
    })


# CREATE Customer (Form Submission)
@router.post("/customers/new", name="create_customer")
async def create_customer_page(
        request: Request,
        name: str = Form(...),
        phone: str = Form(...),
        db: AsyncSession = Depends(get_db_session)
):
    customer_in = CustomerCreate(name=name, phone=phone)
    try:
        await customer_service.CustomerService.create_customer(db, customer_in)
        return RedirectResponse(url=router.url_path_for("list_customers_page"), status_code=fastapi_status.HTTP_303_SEE_OTHER)
    except ValueError as e:  # Handles cases like duplicate phone numbers
        return templates.TemplateResponse("customers/customer_form.html", {
            "request": request,
            "page_title": "New Customer",
            "customer_data": customer_in.model_dump(),  # Pass back submitted data
            "is_edit_mode": False,
            "error": str(e)
        }, status_code=400)
    except Exception as e:
        logging.error(f"Error creating customer: {e}", exc_info=True)
        return templates.TemplateResponse("customers/customer_form.html", {
            "request": request,
            "page_title": "New Customer",
            "customer_data": customer_in.model_dump(),
            "is_edit_mode": False,
            "error": "An unexpected error occurred."
        }, status_code=500)


# EDIT Customer
@router.get("/customers/{customer_id}/edit", name="edit_customer_form_page")
async def edit_customer_form_page(request: Request, customer_id: int, db: AsyncSession = Depends(get_db_session)):
    customer = await customer_service.CustomerService.get_customer_by_id(db, customer_id)
    if not customer:
        raise HTTPException(status_code=fastapi_status.HTTP_404_NOT_FOUND, detail="Customer not found")

    customer_data_for_form = customer.model_dump() if hasattr(customer, 'model_dump') else {
        "id": customer.id, "name": customer.name, "phone": customer.phone
    }

    return templates.TemplateResponse("customers/customer_form.html", {
        "request": request,
        "page_title": f"Edit Customer: {customer.name}",
        "customer_data": customer_data_for_form,
        "is_edit_mode": True
    })


# UPDATE Customer
@router.post("/customers/{customer_id}/edit", name="update_customer_submit")
async def update_customer_submit_page(
        request: Request,
        customer_id: int,
        name: str = Form(...),
        phone: str = Form(...),
        db: AsyncSession = Depends(get_db_session)
):
    customer_update_data = CustomerUpdate(name=name, phone=phone)
    try:
        updated_customer = await customer_service.CustomerService.update_customer(db, customer_id, customer_update_data)
        if not updated_customer:
            # Should be caught by service if customer not found, service might return None or raise error
            existing_customer = await customer_service.CustomerService.get_customer_by_id(db, customer_id)
            if not existing_customer:
                raise HTTPException(status_code=fastapi_status.HTTP_404_NOT_FOUND, detail="Customer not found for update")

        return RedirectResponse(url=router.url_path_for("list_customers_page"), status_code=fastapi_status.HTTP_303_SEE_OTHER)
    except ValueError as e:  # Handles cases like duplicate phone numbers or other validation
        current_form_data = {"id": customer_id, "name": name, "phone": phone}
        return templates.TemplateResponse("customers/customer_form.html", {
            "request": request,
            "page_title": f"Edit Customer: {name}",  # Show current attempt
            "customer_data": current_form_data,
            "is_edit_mode": True,
            "error": str(e)
        }, status_code=400)
    except Exception as e:
        logging.error(f"Error updating customer {customer_id}: {e}", exc_info=True)
        current_form_data = {"id": customer_id, "name": name, "phone": phone}
        return templates.TemplateResponse("customers/customer_form.html", {
            "request": request,
            "page_title": f"Edit Customer: {name}",
            "customer_data": current_form_data,
            "is_edit_mode": True,
            "error": "An unexpected error occurred."
        }, status_code=500)


# DELETE Customer
@router.post("/customers/{customer_id}/delete", name="delete_customer_submit")
async def delete_customer_submit_page(request: Request, customer_id: int, db: AsyncSession = Depends(get_db_session)):
    try:
        deleted_customer = await customer_service.CustomerService.delete_customer(db, customer_id)
        if not deleted_customer:
            raise HTTPException(status_code=fastapi_status.HTTP_404_NOT_FOUND, detail="Customer not found for deletion")
        return RedirectResponse(url=router.url_path_for("list_customers_page"), status_code=fastapi_status.HTTP_303_SEE_OTHER)
    except Exception as e:  # Catch potential ForeignKeyViolation or other DB issues if customer has orders.
        logging.error(f"Error deleting customer {customer_id}: {e}", exc_info=True)
        # Redirect with an error message. You might need a way to display these messages (e.g., query params, flash messages).
        return RedirectResponse(
            url=router.url_path_for("list_customers_page") + f"?error=delete_failed&customer_id={customer_id}",
            status_code=fastapi_status.HTTP_303_SEE_OTHER)


# --- Burger Pages ---
@router.get("/burgers", name="list_burgers_page")
async def list_burgers_page(request: Request, db: AsyncSession = Depends(get_db_session)):
    burgers = await burger_service.BurgerService.get_all_burgers(db)
    return templates.TemplateResponse("burgers/burger_list.html", {
        "request": request, "page_title": "Burgers", "burgers": burgers
    })


# CREATE Burger (Form Display)
@router.get("/burgers/new", name="new_burger_form_page")
async def new_burger_form_page(request: Request, db: AsyncSession = Depends(get_db_session)):
    all_ingredients = await IngredientService.get_all_ingredients(db)
    return templates.TemplateResponse("burgers/burger_form.html", {
        "request": request,
        "page_title": "New Burger",
        "burger_data": {},  # Empty for new burger
        "all_ingredients": all_ingredients,
        "is_edit_mode": False,
        "initial_selected_ingredients_js": []  # Empty for new burger
    })


# CREATE Burger (Form Submission)
@router.post("/burgers/new", name="create_burger")
async def create_burger_page(
        request: Request,
        name: str = Form(...),
        description: Optional[str] = Form(None),
        price: float = Form(...),
        ingredient_ids: List[int] = Form([]),
        db: AsyncSession = Depends(get_db_session)
):
    burger_in = BurgerCreate(
        name=name,
        description=description,
        price=price,
        ingredient_ids=ingredient_ids
    )
    try:
        await burger_service.BurgerService.create_burger(db, burger_in)
        return RedirectResponse(url=router.url_path_for("list_burgers_page"), status_code=fastapi_status.HTTP_303_SEE_OTHER)
    except ValueError as e:
        all_ingredients = await IngredientService.get_all_ingredients(db)
        submitted_ingredients_for_js = []

        return templates.TemplateResponse("burgers/burger_form.html", {
            "request": request,
            "page_title": "New Burger",
            "burger_data": burger_in.model_dump(),  # Show submitted data back
            "all_ingredients": all_ingredients,
            "is_edit_mode": False,
            "initial_selected_ingredients_js": submitted_ingredients_for_js,
            "error": str(e)
        }, status_code=400)
    except Exception as e:
        logging.error(f"Error creating burger: {e}", exc_info=True)
        all_ingredients = await IngredientService.get_all_ingredients(db)
        return templates.TemplateResponse("burgers/burger_form.html", {
            "request": request,
            "page_title": "New Burger",
            "burger_data": burger_in.model_dump(),
            "all_ingredients": all_ingredients,
            "is_edit_mode": False,
            "initial_selected_ingredients_js": [],
            "error": "An unexpected error occurred while creating the burger."
        }, status_code=500)


# EDIT Burger (Form Display)
@router.get("/burgers/{burger_id}/edit", name="edit_burger_form_page")
async def edit_burger_form_page(request: Request, burger_id: int, db: AsyncSession = Depends(get_db_session)):
    burger = await burger_service.BurgerService.get_burger_by_id(db, burger_id)
    if not burger:
        raise HTTPException(status_code=fastapi_status.HTTP_404_NOT_FOUND, detail="Burger not found")

    all_ingredients = await IngredientService.get_all_ingredients(db)

    initial_selected_ingredients_for_js = []
    if burger.ingredient_items:
        for item in burger.ingredient_items:
            if item.ingredient:  # Ensure ingredient exists (it might have been deleted)
                for _ in range(item.quantity):  # Add one entry for each unit of quantity
                    initial_selected_ingredients_for_js.append({
                        "id": str(item.ingredient.id),
                        "name": item.ingredient.name
                    })

    burger_data_for_form = burger.model_dump() if hasattr(burger, 'model_dump') else {
        "id": burger.id, "name": burger.name, "description": burger.description, "price": burger.price
    }

    return templates.TemplateResponse("burgers/burger_form.html", {
        "request": request,
        "page_title": f"Edit Burger: {burger.name}",
        "burger_data": burger_data_for_form,
        "all_ingredients": all_ingredients,
        "is_edit_mode": True,
        "initial_selected_ingredients_js": initial_selected_ingredients_for_js
    })


# UPDATE Burger (Form Submission)
@router.post("/burgers/{burger_id}/edit", name="update_burger_submit")
async def update_burger_submit_page(
        request: Request,
        burger_id: int,
        name: str = Form(...),
        description: Optional[str] = Form(None),
        price: float = Form(...),
        ingredient_ids: List[int] = Form([]),
        db: AsyncSession = Depends(get_db_session)
):
    burger_update_data = BurgerUpdate(
        name=name,
        description=description,
        price=price,
        ingredient_ids=ingredient_ids
    )
    try:
        updated_burger = await burger_service.BurgerService.update_burger(db, burger_id, burger_update_data)
        if not updated_burger:
            # This case might be covered by service raising an error or returning None
            raise HTTPException(status_code=fastapi_status.HTTP_404_NOT_FOUND, detail="Burger not found for update")
        return RedirectResponse(url=router.url_path_for("list_burgers_page"), status_code=fastapi_status.HTTP_303_SEE_OTHER)
    except ValueError as e:  # Specific error from service/crud
        all_ingredients = await IngredientService.get_all_ingredients(db)
        current_form_data = {"id": burger_id, "name": name, "description": description, "price": price}
        return templates.TemplateResponse("burgers/burger_form.html", {
            "request": request, "page_title": f"Edit Burger: {name}", "burger_data": current_form_data,
            "all_ingredients": all_ingredients, "is_edit_mode": True,
            "initial_selected_ingredients_js": [{"id": str(ing_id), "name": "Unknown"} for ing_id in ingredient_ids],
            # Simplified: fetch names for better UX
            "error": str(e)
        }, status_code=400)
    except Exception as e:  # Generic error
        logging.error(f"Error updating burger {burger_id}: {e}", exc_info=True)
        all_ingredients = await IngredientService.get_all_ingredients(db)
        current_form_data = {"id": burger_id, "name": name, "description": description, "price": price}
        return templates.TemplateResponse("burgers/burger_form.html", {
            "request": request, "page_title": f"Edit Burger: {name}", "burger_data": current_form_data,
            "all_ingredients": all_ingredients, "is_edit_mode": True,
            "initial_selected_ingredients_js": [],  # Simplified
            "error": "An unexpected error occurred."
        }, status_code=500)


# DELETE Burger
@router.post("/burgers/{burger_id}/delete", name="delete_burger_submit")
async def delete_burger_submit_page(request: Request, burger_id: int, db: AsyncSession = Depends(get_db_session)):
    try:
        deleted_burger = await burger_service.BurgerService.delete_burger(db, burger_id)
        if not deleted_burger:
            raise HTTPException(status_code=fastapi_status.HTTP_404_NOT_FOUND, detail="Burger not found for deletion")
        return RedirectResponse(url=router.url_path_for("list_burgers_page"), status_code=fastapi_status.HTTP_303_SEE_OTHER)
    except Exception as e:
        logging.error(f"Error deleting burger {burger_id}: {e}", exc_info=True)
        # Redirect to list page, possibly with an error query parameter or flash message
        return RedirectResponse(url=router.url_path_for("list_burgers_page") + "?error=delete_failed",
                                status_code=fastapi_status.HTTP_303_SEE_OTHER)


# HTMX ingredient item
@router.get("/burgers/htmx/get-ingredient-item/{ingredient_id}", name="get_ingredient_item_htmx")
async def get_ingredient_item_htmx_route(
        request: Request, ingredient_id: int, db: AsyncSession = Depends(get_db_session)
):
    ingredient = await IngredientService.get_ingredient_by_id(db, ingredient_id)
    if not ingredient:
        return HTMLResponse("<span>Ingredient not found</span>", status_code=404)
    return templates.TemplateResponse("partials/burger_ingredient_item_htmx.html", {
        "request": request, "ingredient": ingredient
    })


# --- Order Pages ---

# LIST Orders
@router.get("/orders", name="list_orders_page")
async def list_orders_page(request: Request, db: AsyncSession = Depends(get_db_session)):
    # The OrderService.get_all_orders already returns OrderResponse objects
    # which include customer details and calculated total_price.
    orders = await order_service.OrderService.get_all_orders(db)
    return templates.TemplateResponse("orders/order_list.html", {
        "request": request, "page_title": "Orders", "orders": orders
    })


# CREATE Order (Form Display)
@router.get("/orders/new", name="new_order_form_page")
async def new_order_form_page(request: Request, db: AsyncSession = Depends(get_db_session)):
    customers = await customer_service.CustomerService.get_all_customers(db)
    burgers = await burger_service.BurgerService.get_all_burgers(db)
    if not customers:
        return templates.TemplateResponse("orders/order_form.html", {
            "request": request, "page_title": "New Order",
            "error": "No customers available. Please create a customer first.",
            "customers": [], "burgers": burgers, "order_statuses": [s.value for s in OrderStatus],
            "order_data": {}, "is_edit_mode": False, "order_items_js": []
        })
    return templates.TemplateResponse("orders/order_form.html", {
        "request": request,
        "page_title": "New Order",
        "customers": customers,
        "burgers": burgers,  # Pass available burgers
        "order_statuses": [s.value for s in OrderStatus],  # For status dropdown
        "order_data": {},
        "is_edit_mode": False,
        "order_items_js": []
    })


# CREATE Order (Form Submission)
@router.post("/orders/new", name="create_order_submit")
async def create_order_submit_page(
        request: Request,
        customer_id: int = Form(...),
        item_burger_ids: List[int] = Form([]),
        item_quantities: List[int] = Form([]),
        status: str = Form(OrderStatus.Pending.value),  # Default status
        db: AsyncSession = Depends(get_db_session)
):
    order_burger_items_create: List[OrderBurgerItemCreate] = []
    if len(item_burger_ids) != len(item_quantities):
        customers = await customer_service.CustomerService.get_all_customers(db)
        burgers = await burger_service.BurgerService.get_all_burgers(db)
        return templates.TemplateResponse("orders/order_form.html", {
            "request": request, "page_title": "New Order", "customers": customers, "burgers": burgers,
            "order_statuses": [s.value for s in OrderStatus],
            "order_data": {"customer_id": customer_id, "status": status},
            "is_edit_mode": False, "order_items_js": [],
            "error": "Mismatch in burger items and quantities."
        }, status_code=400)

    for burger_id, quantity in zip(item_burger_ids, item_quantities):
        if quantity > 0:
            order_burger_items_create.append(OrderBurgerItemCreate(burger_id=burger_id, quantity=quantity))

    if not order_burger_items_create:  # Check if any valid items were added
        customers = await customer_service.CustomerService.get_all_customers(db)
        burgers = await burger_service.BurgerService.get_all_burgers(db)
        return templates.TemplateResponse("orders/order_form.html", {
            "request": request, "page_title": "New Order", "customers": customers, "burgers": burgers,
            "order_statuses": [s.value for s in OrderStatus],
            "order_data": {"customer_id": customer_id, "status": status},
            "is_edit_mode": False, "order_items_js": [],
            "error": "An order must contain at least one burger."
        }, status_code=400)

    order_in = OrderCreate(
        customer_id=customer_id,
        items=order_burger_items_create
        # Status will be default Pending by model, or set explicitly if schema changes
    )
    try:
        new_order_response = await order_service.OrderService.create_order(db, order_in)

        # If status needs to be set explicitly after creation and is part of the form:
        if new_order_response and status != OrderStatus.Pending.value:  # Default
            status_update_data = OrderUpdate(status=OrderStatus(status))
            await order_service.OrderService.update_order(db, new_order_response.id, status_update_data)

        return RedirectResponse(url=router.url_path_for("list_orders_page"), status_code=fastapi_status.HTTP_303_SEE_OTHER)
    except ValueError as e:
        customers = await customer_service.CustomerService.get_all_customers(db)
        burgers = await burger_service.BurgerService.get_all_burgers(db)
        # Reconstruct submitted items for display
        submitted_items_js = []
        for burger_id, quantity in zip(item_burger_ids, item_quantities):
            burger_obj = await burger_service.BurgerService.get_burger_by_id(db, burger_id)
            if burger_obj:
                submitted_items_js.append(
                    {"burger_id": str(burger_id), "burger_name": burger_obj.name, "quantity": quantity,
                     "price": burger_obj.price})

        return templates.TemplateResponse("orders/order_form.html", {
            "request": request, "page_title": "New Order", "customers": customers, "burgers": burgers,
            "order_statuses": [s.value for s in OrderStatus],
            "order_data": {"customer_id": customer_id, "status": status},  # Pass back submitted data
            "is_edit_mode": False, "order_items_js": submitted_items_js,
            "error": str(e)
        }, status_code=400)
    except Exception as e:
        logging.error(f"Error creating order: {e}", exc_info=True)
        customers = await customer_service.CustomerService.get_all_customers(db)
        burgers = await burger_service.BurgerService.get_all_burgers(db)
        return templates.TemplateResponse("orders/order_form.html", {
            "request": request, "page_title": "New Order", "customers": customers, "burgers": burgers,
            "order_statuses": [s.value for s in OrderStatus],
            "order_data": {"customer_id": customer_id, "status": status},
            "is_edit_mode": False, "order_items_js": [],
            "error": "An unexpected error occurred."
        }, status_code=500)


# EDIT Order (Form Display)
@router.get("/orders/{order_id}/edit", name="edit_order_form_page")
async def edit_order_form_page(request: Request, order_id: int, db: AsyncSession = Depends(get_db_session)):
    order_response = await order_service.OrderService.get_order_by_id_with_total_price(db, order_id)
    if not order_response:
        raise HTTPException(status_code=fastapi_status.HTTP_404_NOT_FOUND, detail="Order not found")

    order_db_obj = await order_crud.get_order_by_id(db, order_id)  # Use CRUD to get full model

    customers = await customer_service.CustomerService.get_all_customers(db)
    burgers = await burger_service.BurgerService.get_all_burgers(db)

    order_items_for_js = []
    if order_db_obj and order_db_obj.burger_items:
        for item in order_db_obj.burger_items:
            if item.burger:
                order_items_for_js.append({
                    "burger_id": str(item.burger_id),
                    "burger_name": item.burger.name,
                    "quantity": item.quantity,
                    "price": item.burger.price  # For display in JS if needed
                })

    order_data_for_form = {
        "id": order_response.id,
        "customer_id": order_response.customer.id if order_response.customer else None,
        "status": order_response.status.value
    }

    return templates.TemplateResponse("orders/order_form.html", {
        "request": request,
        "page_title": f"Edit Order #{order_response.id}",
        "customers": customers,
        "burgers": burgers,
        "order_statuses": [s.value for s in OrderStatus],
        "order_data": order_data_for_form,
        "is_edit_mode": True,
        "order_items_js": order_items_for_js  # Pass existing items to JS
    })


# UPDATE Order (Form Submission)
@router.post("/orders/{order_id}/edit", name="update_order_submit")
async def update_order_submit_page(
        request: Request,
        order_id: int,
        customer_id: int = Form(...),
        item_burger_ids: List[int] = Form([]),
        item_quantities: List[int] = Form([]),
        status: str = Form(...),
        db: AsyncSession = Depends(get_db_session)
):
    order_burger_items_update: List[OrderBurgerItemCreate] = []
    if len(item_burger_ids) != len(item_quantities):
        pass

    for burger_id, quantity in zip(item_burger_ids, item_quantities):
        if quantity > 0:
            order_burger_items_update.append(OrderBurgerItemCreate(burger_id=burger_id, quantity=quantity))

    if not order_burger_items_update and customer_id:
        pass

    order_update_data = OrderUpdate(
        customer_id=customer_id,
        items=order_burger_items_update if order_burger_items_update else None,
        status=OrderStatus(status)
    )

    try:
        updated_order = await order_service.OrderService.update_order(db, order_id, order_update_data)
        if not updated_order:
            raise HTTPException(status_code=fastapi_status.HTTP_404_NOT_FOUND, detail="Order not found or update failed")
        return RedirectResponse(url=router.url_path_for("list_orders_page"), status_code=fastapi_status.HTTP_303_SEE_OTHER)
    except ValueError as e:
        customers = await customer_service.CustomerService.get_all_customers(db)
        burgers = await burger_service.BurgerService.get_all_burgers(db)
        current_form_data = {"id": order_id, "customer_id": customer_id, "status": status}
        # Reconstruct submitted_items_js for display
        submitted_items_js = []
        for burger_id, quantity in zip(item_burger_ids, item_quantities):
            burger_obj = await burger_service.BurgerService.get_burger_by_id(db, burger_id)
            if burger_obj:
                submitted_items_js.append(
                    {"burger_id": str(burger_id), "burger_name": burger_obj.name, "quantity": quantity,
                     "price": burger_obj.price})

        return templates.TemplateResponse("orders/order_form.html", {
            "request": request, "page_title": f"Edit Order #{order_id}", "customers": customers, "burgers": burgers,
            "order_statuses": [s.value for s in OrderStatus], "order_data": current_form_data,
            "is_edit_mode": True, "order_items_js": submitted_items_js, "error": str(e)
        }, status_code=400)
    except Exception as e:
        logging.error(f"Error updating order {order_id}: {e}", exc_info=True)
        customers = await customer_service.CustomerService.get_all_customers(db)
        burgers = await burger_service.BurgerService.get_all_burgers(db)
        current_form_data = {"id": order_id, "customer_id": customer_id, "status": status}
        return templates.TemplateResponse("orders/order_form.html", {
            "request": request, "page_title": f"Edit Order #{order_id}", "customers": customers, "burgers": burgers,
            "order_statuses": [s.value for s in OrderStatus], "order_data": current_form_data,
            "is_edit_mode": True, "order_items_js": [], "error": "An unexpected error occurred."
        }, status_code=500)


# DELETE Order
@router.post("/orders/{order_id}/delete", name="delete_order_submit")
async def delete_order_submit_page(request: Request, order_id: int, db: AsyncSession = Depends(get_db_session)):
    try:
        deleted_order = await order_service.OrderService.delete_order(db, order_id)
        if not deleted_order:
            raise HTTPException(status_code=fastapi_status.HTTP_404_NOT_FOUND, detail="Order not found for deletion")
        return RedirectResponse(url=router.url_path_for("list_orders_page"), status_code=fastapi_status.HTTP_303_SEE_OTHER)
    except Exception as e:
        logging.error(f"Error deleting order {order_id}: {e}", exc_info=True)
        return RedirectResponse(
            url=router.url_path_for("list_orders_page") + f"?error=delete_failed&order_id={order_id}",
            status_code=fastapi_status.HTTP_303_SEE_OTHER)