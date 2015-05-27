# Anodos.Catalog

### Version
Dev

### Tech
* [Django] - The web framework for perfectionists with deadlines.
* [Foundation] - The most advanced responsive front-end framework in the world.

### User roles
  - Заказчик: if user.is_authenticated
  - Менеджер продуктов: if perms.catalog.change_product
  - Менеджер отдела закупок: if perms.catalog.change_distributor
  - Менеджер отдела продаж: if perms.catalog.change_order
  - Представитель производителя: if perms.catalog.change_vendor
