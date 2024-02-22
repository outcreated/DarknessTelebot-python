from typing import Optional
from keyboards import inline


async def get_admin_panel_kb():
    return await inline.generate_admin_panel_kb()


async def get_admin_product_menu():
    return await inline.generate_admin_product_menu()


async def get_addproduct_menu(boolean: Optional[bool] = False,
                              product_name: Optional[str] = "",
                              product_description: Optional[str] = ""):
    return await inline.generate_addproduct_menu(boolean,
                                                 product_name,
                                                 product_description)


async def get_edit_product_menu(var: int):
    return await inline.generate_edit_product_menu(var)
