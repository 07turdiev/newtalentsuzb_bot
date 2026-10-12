from aiogram import Router

from . import admin, apply, common, user


def routers() -> list[Router]:
    # Tartib muhim: «Bekor qilish» va /start har qanday holatda birinchi ushlanadi,
    # admin buyruqlari ariza to'ldirishdan oldin, eskirgan tugmalar esa eng oxirida.
    return [common.router, user.router, admin.router, apply.router, common.fallback_router]
